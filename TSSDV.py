import gdal,os,sys,glob,PIL,time,subprocess,uuid,FileDialog,abc
from gdalconst import *
from numpy import *
from pylab import *
from PIL import imtools
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import numpy.ma as ma
import numpy as np
from jdcal import *
import sys
import PyQt4
from PyQt4 import QtCore, QtGui,uic

form_class=uic.loadUiType("abc.ui")[0]

class MyWindowClass(QtGui.QMainWindow,form_class):
    
    def __init__(self,parent=None):        
        QtGui.QMainWindow.__init__(self,parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.pushbutton_clicked)
        self.pushButton_2.clicked.connect(self.pushbutton_2_clicked)
        self.comboBox.currentIndexChanged.connect(self.combo)
        self.comboBox_2.currentIndexChanged.connect(self.colormaps)
        self.radioButton.clicked.connect(self.auto)
        self.radioButton_2.clicked.connect(self.manual)
        self.radioButton_3.clicked.connect(self.single)
        self.radioButton_4.clicked.connect(self.dual)
        self.pushButton_3.clicked.connect(self.pushme)
        self.pushButton_4.clicked.connect(self.pushclose)
        self.pushButton_5.clicked.connect(self.Mstart)
        self.pushButton_6.clicked.connect(self.Mprev)
        self.pushButton_7.clicked.connect(self.Mnext)
        self.pushButton_8.clicked.connect(self.Reset)
        self.actionHelp.triggered.connect(self.myhelp)
        self.actionAbout.triggered.connect(self.myabout)
        self.checkBox.stateChanged.connect(self.my)
        self.checkBox_3.stateChanged.connect(self.my)
        self.radioButton.setChecked(True)
        self.auto()
        self.radioButton_3.setChecked(True)
        self.single()
        self.folderflag=0
        self.strech=0
        self.index=0
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(("globe.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colormap='Greens'
        self.comboBox_2.setCurrentIndex(4)
        self.buttonindicate=0

    def myabout(self):
        self.msgBox=QtGui.QMessageBox()
        self.msgBox.setWindowTitle("    About   ")
        self.msgBox.setWindowIcon(self.icon)
        self.msgBox.setText("Time Series Satellite Data Visualizer \n                Version: 1.0.0")
        self.msgBox.exec_()
        

    def myhelp(self):
        os.system("documentation.pdf")
        

    def colormaps(self):
        self.colormap=str(self.comboBox_2.currentText())   #get the value of colormap to be selcted     
        
    def my(self):
        pass
        
    def Mstart(self):
        self.index=0                    #Manual Printing turn to to index zero
        self.manprint()                         #calling Manual print option
        self.pushButton_6.setEnabled(0)         #previous button disabled
        self.pushButton_7.setEnabled(1)         #Next button Enabled 
        self.pushButton_5.setEnabled(0)         #start button diabled

    def Mprev(self):
        self.pushButton_7.setEnabled(1)         #enable Next button
        if self.index==0:
            self.pushButton_5.setEnabled(0)
            self.pushButton_6.setEnabled(0)         #diable previous button if index is zero
        else:
            self.index=self.index-1                 #subtract index value
        self.manprint()
            
    def Mnext(self):
        if self.buttonindicate==0:
            self.msgBox8=QtGui.QMessageBox()            
            self.msgBox8.setWindowTitle("    Alert   ")
            self.msgBox8.setWindowIcon(self.icon)
            self.msgBox8.setText("Press Show Button First   ")
            self.msgBox8.exec_()
            
        else:
            my=len(self.listoftif)                  
            self.pushButton_5.setEnabled(1)     #start button enabled
            self.pushButton_6.setEnabled(1)     #previous button eabled
            if self.index==my-1:
                self.pushButton_7.setEnabled(0)         #diable next button if index is last
            else:
                self.index=self.index+1       #add index value
            self.manprint()
      
    def pushbutton_clicked(self):       #Select Folder of tif files
        self.folderflag=1
        self.dirname=str(QtGui.QFileDialog.getExistingDirectory(self,"Select Directory"))
        self.lineEdit.setText(str(self.dirname))
        self.fulldirname=self.dirname+'\*.tif'
        self.listoftif=glob.glob(self.fulldirname)
        

    def pushbutton_2_clicked(self):
        self.shapefilename=str(QtGui.QFileDialog.getOpenFileName(self,"Select Shape File","","*.shp"))
        self.lineEdit_2.setText(str(self.shapefilename))
        

    def pushclose(self):
        sys.exit(1)        #Close Button 

    def combo(self,n):
        
        self.strech=n
        if self.strech==3 or self.strech==4:           #if Standard Deviation/Percentile clipping selected , enable text edit , else diable
            self.lineEdit_4.setEnabled(1)
        if self.strech==0 or self.strech==1 or self.strech==2:
            self.lineEdit_4.setEnabled(0)
        if self.strech==1:                  #if histogram selected , diable Fix legend , else enable
            self.groupBox_4.setEnabled(0)
        else:
            self.groupBox_4.setEnabled(1)

    def auto(self):
        self.doAnimate=1
        self.groupBox_5.setEnabled(0)  #if automatic selected , manual button disabled

    def manual(self):
        self.doAnimate=0
        self.groupBox_5.setEnabled(1)           #if manual selected , manual button enabled
        if self.index==0:
            self.pushButton_5.setEnabled(0)
            self.pushButton_6.setEnabled(0)
        
    def single(self):
        self.comboBox.setCurrentIndex(0)        # set to Min-Max
        self.doBoth=0
        
    def dual(self):
        self.doBoth=1
        self.comboBox.setCurrentIndex(1)   #set to Histogram

    def Reset(self):            #reset all options
        self.listoftif=''
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_4.setEnabled(0)
        self.checkBox.setChecked(0)
        self.radioButton.setChecked(True)
        self.auto()
        self.radioButton_3.setChecked(True)
        self.single()
        self.colormap='Greens'
        plt.close()
        
    def fixlegend(self):   # set values of fixlegend
        if self.checkBox.isChecked():
            maxlist=[]
            minlist=[]
            if self.comboBox.currentIndex()==0 or self.comboBox.currentIndex()==2:    #if min-max , 2 Iqr select calculate mininum/maximum value of colormap
                for i in range (len(self.listoftif)):
                    dataset=gdal.Open(self.listoftif[i],GA_ReadOnly)   #get dataset
                    if dataset is None:
                        print'Could not open file'
                    cols=dataset.RasterXSize
                    rows=dataset.RasterYSize
                    band = dataset.GetRasterBand(1)
                    data = band.ReadAsArray(0, 0, cols, rows)
                    data1 = np.where(data == band.GetNoDataValue(),np.nan,data)
                    c1=data1.copy()      #for copying histogram value
                    data2=np.isfinite(data1)  #true-false matrix 
                    data3=data1[data2]    #get value of true value
                    if self.comboBox.currentIndex()==0:
                        maxlist.append(amax(data)) #create list of maximum data
                        minlist.append(amin(data))      #create list of minimum data
                        self.maxdata=max(maxlist)       #set max  value from max list 
                        self.mindata=min(minlist)           #set min value from min list
                    if self.comboBox.currentIndex()==2:
                        low=np.percentile(data3,25)   #calculate 1 iqr
                        high=np.percentile(data3,75)   # calculate 2 iqr
                        datal = np.where(data3 < low ,low,data3)    #set data equal to 1 iqr  which is lower to 1 iqr
                        datah = np.where(datal > high ,high,datal)       #set data equal to 2 iqr  which is higher to 2 iqr
                        np.place(c1,data2,datah)            # reshape matrix to original matrix
                        maxlist.append(nanmax(c1))
                        minlist.append(nanmin(c1))
                        self.maxdata=max(maxlist)
                        self.mindata=min(minlist)
            if self.comboBox.currentIndex()==4 or self.comboBox.currentIndex()==3:     #for SD/PC 
                if self.checkall_2():          # check for text in lineEdit value
                    for i in range (len(self.listoftif)):
                        dataset=gdal.Open(self.listoftif[i],GA_ReadOnly)
                        if dataset is None:
                            print'Could not open file'
                        cols=dataset.RasterXSize
                        rows=dataset.RasterYSize
                        band = dataset.GetRasterBand(1)
                        data = band.ReadAsArray(0, 0, cols, rows)
                        data1 = np.where(data == band.GetNoDataValue(),np.nan,data)
                        c1=data1.copy()      #for copying histogram value
                        data2=np.isfinite(data1)
                        data3=data1[data2]                     
                        if self.comboBox.currentIndex()==3:
                            mean=np.mean(data3)
                            sd=np.std(data3)
                            nn=str(self.lineEdit_4.text())  
                            b=nn.split(',')
                            if len(b)==1:
                                m=int(b[0])
                                n=int(b[0])
                            else:
                                m=int(b[0])
                                n=int(b[1])
                            low=mean-m*sd    #calculate lower SD value
                            high=mean+n*sd   #calculate higher sd value
                            datal = np.where(data3 < low ,low,data3)
                            datah = np.where(datal > high ,high,datal)
                            np.place(c1,data2,datah)
                            maxlist.append(nanmax(c1))
                            minlist.append(nanmin(c1))
                            self.maxdata=max(maxlist)
                            self.mindata=min(minlist)
                        
                        if self.comboBox.currentIndex()==4:
                            nn=str(self.lineEdit_4.text())
                            b=nn.split(',')
                            if len(b)==1:
                                m=int(b[0])
                                n=int(b[0])
                            else:
                                m=int(b[0])
                                n=int(b[1])
                            dmax=nanmax(data3)
                            dmin=nanmin(data3)
                            total=dmax-dmin
                            low=dmin+(total*m)/100    #calculate lower PC value
                            high=dmax-(total*n)/100             #calculate higher PC value
                            datal = np.where(data3 < low ,low,data3)
                            datah = np.where(datal > high ,high,datal)
                            np.place(c1,data2,datah)
                            maxlist.append(nanmax(c1))
                            minlist.append(nanmin(c1))
                            self.maxdata=max(maxlist)
                            self.mindata=min(minlist)

    def extent(self):
        oxlist=[]
        oylist=[]
        lxlist=[]
        lylist=[]
        for i in range (len(self.listoftif)):
            dataset=gdal.Open(self.listoftif[self.i],GA_ReadOnly)            
            geotransform=dataset.GetGeoTransform()
            cols=dataset.RasterXSize
            rows=dataset.RasterYSize
            originX=geotransform[0]
            originY=geotransform[3]
            pW=geotransform[1]
            pH=geotransform[5]            
            lastX=originX+(rows*pW)  #last value of X axis
            lastY=originY+(cols*pH) #Last valu of Y axis
            oxlist.append(originX)  # create list of axis value
            oylist.append(originY)
            lxlist.append(lastX)
            lylist.append(lastY)
        self.eox=min(oxlist)   # set min/max value of axis
        self.elx=max(lxlist)
        self.eoy=min(oylist)
        self.ely=max(lylist)
        self.colstring=[self.eox,self.elx,self.ely,self.eoy]  # set color String
            

    def doprepare_show(self):
        self.dataset=gdal.Open(self.listoftif[self.i],GA_ReadOnly)
        if self.dataset is None:
            print'Could not open file'
        cols=self.dataset.RasterXSize
        rows=self.dataset.RasterYSize
        bands=self.dataset.RasterCount
        

        #for oringins
        geotransform=self.dataset.GetGeoTransform()
        self.originX=geotransform[0]
        self.originY=geotransform[3]
        pW=geotransform[1]
        pH=geotransform[5]
        self.lastX=self.originX+(rows*pW)
        self.lastY=self.originY+(cols*pH) #for origins   
        band = self.dataset.GetRasterBand(1)
        self.data = band.ReadAsArray(0, 0, cols, rows)
        nn=str(self.lineEdit_3.text())
        if nn=='':                      # if NoDataValue is empty
            self.data1 = np.where(self.data == band.GetNoDataValue(),np.nan,self.data)
        else: 
            b=nn.split(',')         # if NoDataValue is not empty , place nan to those place 
            for i in range(len(b)):
                if b[i][0]=='<' or b[i][0]=='>':                    
                    if b[i][0]=='<':
                        self.data1 = np.where(self.data < int(b[i][1:]),np.nan,self.data)
                    if b[i][0]=='>':
                        self.data1 = np.where(self.data > int(b[i][1:]),np.nan,self.data)
                else:
                    self.data1 = np.where(self.data == int(b[i]),np.nan,self.data)

        self.image1=os.path.basename(self.listoftif[self.i])[:-4]   #image name
        self.getdate()   # Date COnversion Function
        
        if self.strech==0 or self.doBoth==1:   #if Min-Max selected or Dual Mode Selected
            self.normalprint()
        
        if self.strech==1:  # if Histogram mode is selected
            self.makehist()
            self.histprint()

        if self.strech==2:          # if IQR  mode is selected
            self.iqrprint()

        if self.strech==3:          # if SD mode is selected
             self.sdprint()

        if self.strech==4:          # if PC mode is selected
             self.pcprint()      

        self.fig.canvas.draw()
        show()
        
    def getdate(self):           #let s=2003009
        a=int(self.image1[:4])    #get first four value EX: 2003
        b=int(self.image1[4:])     #get last three value EX: 009
        arr=gcal2jd(a,1,1)    # convert to (2400000.5, 52640.0)
        y1=arr[0]-.5+b       #get 2400000+009
        y2=arr[1]           #get 52640
        d=jd2gcal(y1,y2)    #(2003, 1, 9, 0.5)
        
        e=str(d[0])  #'2003'
        f=str(d[1]) #'1'
        g=str(d[2]) #'9'

        h=[g,f,e]   # get ['9', '1', '2003']
        self.image='-'.join(h)    #get '9-1-2003'

    def normalprint(self):
        if self.doBoth==1:
            subplot(1,2,1)   # subplotting in dual mode 
            fs=12               #set font size of image name
        else:
            fs=15

        if self.checkBox.isChecked():       # if fix-legend is selected , copy min-max value in first two cells
            self.data1[0][0]=self.maxdata
            self.data1[0][1]=self.mindata
        if self.checkBox_3.isChecked():   # if extent is selected
            plt.imshow(self.data1,cmap=get_cmap(self.colormap),extent=self.colstring)   
        else:
            plt.imshow(self.data1,cmap=get_cmap(self.colormap),extent=[self.originX,self.lastX,self.lastY,self.originY])
        plt.text(79.1,31,self.image,fontsize=fs)
        plt.title('Original Data')
        plt.colorbar()
        

    def makehist(self):
        self.c1=self.data1.copy()      #for copying histogram value
        data2=np.isfinite(self.data1)     #True/False Matrix
        data3=self.data1[data2]      # only true values of c
        im2,cdf=imtools.histeq(data3)   # hitogram equalization
        np.place(self.c1,data2,im2)     #placing data at the place of True in copy
        
        
    def histprint(self):
        if self.doBoth==1:
            subplot(1,2,2)
            fs=12
        else:
            fs=15
        plt.imshow(self.c1,cmap=get_cmap(self.colormap),extent=[self.originX,self.lastX,self.lastY,self.originY])
        plt.text(79.1,31,self.image,fontsize=fs)
        plt.title('After Histogram')
        plt.colorbar()                 #for colorbar
        
        
    def iqrprint(self):
        if self.doBoth==1:
            subplot(1,2,2)
            fs=12
        else:
            fs=15
        self.c1=self.data1.copy()      #for copying histogram value
        data2=np.isfinite(self.data1)
        data3=self.data1[data2] 
        low=np.percentile(data3,25)
        high=np.percentile(data3,75)
        datal = np.where(data3 < low ,low,data3)
        datah = np.where(datal > high ,high,datal)  # calculate iqr values
        np.place(self.c1,data2,datah)
        if self.checkBox.isChecked():   # for fix-legend
            self.c1[0][0]=self.maxdata
            self.c1[0][1]=self.mindata
        plt.imshow(self.c1,cmap=get_cmap(self.colormap),extent=[self.originX,self.lastX,self.lastY,self.originY])
        plt.text(79.2,31,self.image,fontsize=fs)
        plt.title('2 Interquartile')
        plt.colorbar()
        

    def sdprint(self):
        if self.doBoth==1:
            subplot(1,2,2)
            fs=12
        else:
            fs=15
        self.c1=self.data1.copy()      #for copying histogram value
        data2=np.isfinite(self.data1)
        data3=self.data1[data2]
        mean=np.mean(data3)
        sd=np.std(data3)
        nn=str(self.lineEdit_4.text())  
        b=nn.split(',')
        if len(b)==1:
            m=int(b[0])
            n=int(b[0])
        else:
            m=int(b[0])
            n=int(b[1])
        low=mean-m*sd
        high=mean+n*sd
##        print sd,mean,low,high
        datal = np.where(data3 < low ,low,data3)
        datah = np.where(datal > high ,high,datal)
        np.place(self.c1,data2,datah)
        if self.checkBox.isChecked():       # for Fix-Legend
            self.c1[0][0]=self.maxdata
            self.c1[0][1]=self.mindata
        plt.imshow(self.c1,cmap=get_cmap(self.colormap),extent=[self.originX,self.lastX,self.lastY,self.originY])
        plt.text(79.2,31,self.image,fontsize=fs)
        plt.title('Standard Deviation')
        plt.colorbar()
        

    def pcprint(self):
        if self.doBoth==1:
            subplot(1,2,2)
            fs=12
        else:
            fs=15
        self.c1=self.data1.copy()      #for copying histogram value
        data2=np.isfinite(self.data1)
        data3=self.data1[data2]
        nn=str(self.lineEdit_4.text())
        b=nn.split(',')
        if len(b)==1:
            m=int(b[0])
            n=int(b[0])
        else:
            m=int(b[0])
            n=int(b[1])
        dmax=nanmax(data3)
        dmin=nanmin(data3)
        total=dmax-dmin
        low=dmin+(total*m)/100
        high=dmax-(total*n)/100
        datal = np.where(data3 < low ,low,data3)
        datah = np.where(datal > high ,high,datal)
        if self.checkBox.isChecked():   # for fix Legend
            self.c1[0][0]=self.maxdata
            self.c1[0][1]=self.mindata
        np.place(self.c1,data2,datah)
        plt.imshow(self.c1,cmap=get_cmap(self.colormap),extent=[self.originX,self.lastX,self.lastY,self.originY])
        plt.text(79.2,31,self.image,fontsize=fs)
        plt.title('Percentile Clipped')
        plt.colorbar()
        
        
       
    def manprint(self):  # manual mode 
        
        self.i=self.index
        if self.flag>0:     # already plotted , clear plot window
            plt.clf()
            
        self.flag=self.flag+1        #increase flag of plot window
        self.doprepare_show()       # data prepration
   
    def checkall(self):   
        f=0
        self.dirname=str(self.lineEdit.text())
        if self.dirname=='':        # for checking Folder path 
            self.msgBox1=QtGui.QMessageBox()
            self.msgBox1.setWindowTitle("    Alert   ")
            self.msgBox1.setWindowIcon(self.icon)
            self.msgBox1.setText("Enter Folder path")
            self.msgBox1.exec_()
            f=1
        else:
            pass
            
        if self.radioButton.isChecked() or self.radioButton_2.isChecked():      # for checking controls 
            pass
        else:
            self.msgBox2=QtGui.QMessageBox()            
            self.msgBox2.setWindowTitle("    Alert   ")
            self.msgBox2.setWindowIcon(self.icon)
            self.msgBox2.setText("Select Controls")
            self.msgBox2.exec_()
            f=1
        
        if self.radioButton_3.isChecked() or self.radioButton_4.isChecked():  # for checking View
            pass
        else:
            self.msgBox3=QtGui.QMessageBox()
            self.msgBox3.setWindowTitle("    Alert   ")
            self.msgBox3.setWindowIcon(self.icon)
            self.msgBox3.setText("Select View")
            self.msgBox3.exec_()
            f=1
                   
        if f==0:
            return True
        else:
            return False
        

    def checkall_2(self):
        f=0
        if self.doBoth==1 and self.comboBox.currentIndex()==0:              # for checking 2nd Stretching
            self.msgBox5=QtGui.QMessageBox()
            self.msgBox5.setWindowTitle("    Alert   ")
            self.msgBox5.setWindowIcon(self.icon)
            self.msgBox5.setText("Select 2nd Stretching \n   to be Displayed")
            self.msgBox5.exec_()
            f=1
            
        if self.lineEdit_4.text()=='' and self.comboBox.currentIndex()==3:          # for checking Text box of SD
            self.msgBox6=QtGui.QMessageBox()            
            self.msgBox6.setWindowTitle("    Alert   ")
            self.msgBox6.setWindowIcon(self.icon)
            self.msgBox6.setText("Enter the Mutliplier of\n Standard Deviation")
            self.msgBox6.exec_()
            f=1
            
        if self.lineEdit_4.text()=='' and self.comboBox.currentIndex()==4:          # for checking Text box of PC
            self.msgBox7=QtGui.QMessageBox()            
            self.msgBox7.setWindowTitle("    Alert   ")
            self.msgBox7.setWindowIcon(self.icon)
            self.msgBox7.setText("Enter the Percentage\n     to be clipped")
            self.msgBox7.exec_()
            f=1          
        
        if f==0:
            return True
        else:
            return False

    def checkfolder(self):                  # for checking Folder Path/Is there any tif file or not?
        if self.folderflag==0:
            self.fulldirname=self.dirname+'\*.tif'
            self.listoftif=glob.glob(self.fulldirname)
        else:
            self.dirname=str(self.lineEdit.text())
            self.fulldirname=self.dirname+'\*.tif'
            self.listoftif=glob.glob(self.fulldirname)
        
        if len(self.listoftif)==0:
            self.msgBox4=QtGui.QMessageBox()            
            self.msgBox4.setWindowTitle("    Alert   ")
            self.msgBox4.setWindowIcon(self.icon)
            self.msgBox4.setText("No Tif File in current directory   ")
            self.msgBox4.exec_()
            return False
        else:
            return True

    def shapefile(self):
        self.shapefilename=str(self.lineEdit_2.text())
        a=self.shapefilename.split('/')
        self.shapename='\\'.join(a)
        dname=os.path.dirname(self.listoftif[0])
        gdal='C:\\Program Files\\GDAL\\gdalwarp.exe -cutline '
        newfoldername=str(uuid.uuid4())
        new=dname+ '\\' + newfoldername
        os.mkdir(new)
        for i in range(len(self.listoftif)):
            bname=os.path.basename(self.listoftif[i])
            newcutfile=new+'\\'+bname
            mystring=gdal+'"'+self.shapename+'"'+' '+'"'+self.listoftif[i]+'"'+' '+'"'+newcutfile+'"'
            subprocess.check_output(mystring)

        nnew=dname+'\\'+newfoldername+'\\*.tif'
        self.listoftif=glob.glob(nnew)
                
               
    
    def pushme(self):
        plt.close()
        self.buttonindicate=1

        if self.checkall():          # for folder text,view,controls
            if self.checkfolder():         # for folder path
                if self.checkall_2():           # for 2nd stretch,text box of sd/pc
                    if str(self.lineEdit_2.text())[-4:]=='.shp':                                         
                        self.shapefile()                        
                    
                    if self.checkBox.isChecked():   #for fix legend
                        self.fixlegend()
                        
                    if self.checkBox_3.isChecked():  # for set axis values
                        self.extent()
                    self.index=0            #for !st image
                    self.fig=plt.figure()  # for plotting window
                    plt.ion()           #for making plot window interactive 
                    
                    if self.doAnimate==1:  #for automatic 
                        for self.i in range (len(self.listoftif)):
                            self.doprepare_show()
                            time.sleep(0.05)
                            plt.clf()

                    if self.doAnimate==0:  # for manual control
                        self.manual()
                        self.flag=0
                        self.manprint()
            
                
app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
