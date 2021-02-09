"""
Please read the following instruction befor using the code:
    1) Keep the data file in the same folder as this script.
    2) Uncomment only the corresponding line from 18-33.
       
@author: Sushil Silwal, ssilwal@ucsd.edu 
"""
import datetime, time
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from bdateutil import isbday
import holidays

#------------------------------------------------------------------------------
""" Uncomment the line below for corresponding building file"""
#data_in=pd.read_csv('RobinsonHall.csv',parse_dates=['DateTime']); cal_real=0.4; cal_reactive=0.4;  #Robinson Hall
data_in=pd.read_csv('CenterHall.csv',parse_dates=['DateTime']); cal_real=0.5; cal_reactive=1;  #Center Hall
#data_in=pd.read_csv('EastCampus.csv',parse_dates=['DateTime']); cal_real=1; cal_reactive=1; #East Campus Office
#data_in=pd.read_csv('GalbraithHall.csv',parse_dates=['DateTime']); cal_real=0.5; cal_reactive=0.5; #Galbriath Hall
#data_in=pd.read_csv('GeiselLibrary.csv',parse_dates=['DateTime']); cal_real=0.3; cal_reactive=1; #Geisel Library
#data_in=pd.read_csv('GilmanBuilding.csv',parse_dates=['DateTime']); cal_real=1; cal_reactive=1; #Gilman Parking
#data_in=pd.read_csv('HopkinsBuilding.csv',parse_dates=['DateTime']); cal_real=0.35; cal_reactive=0.5; #Hopkins Parking
#data_in=pd.read_csv('OttersonHall.csv',parse_dates=['DateTime']); cal_real=0.35; cal_reactive=0.5; #Otterson Hall
#data_in=pd.read_csv('Mandeville.csv',parse_dates=['DateTime']); cal_real=0.75; cal_reactive=1; #Mandeville Center
#data_in=pd.read_csv('PepperCanyon.csv',parse_dates=['DateTime']); cal_real=0.7; cal_reactive=1; #Paper Canyon Hall
#data_in=pd.read_csv('PoliceBuilding.csv',parse_dates=['DateTime']); cal_real=0.4; cal_reactive=0.7; #Police Department
#data_in=pd.read_csv('RadyHall.csv',parse_dates=['DateTime']); cal_real=0.7; cal_reactive=1; #Rady Hall
#data_in=pd.read_csv('SocialScience.csv',parse_dates=['DateTime']); cal_real=0.7; cal_reactive=1; #Social Science Research Building
#data_in=pd.read_csv('StudentServices.csv',parse_dates=['DateTime']); cal_real=0.5; cal_reactive=1; #Student Service Center
#data_in=pd.read_csv('MusicBuilding.csv',parse_dates=['DateTime']); cal_real=0.6; cal_reactive=1; #Music Building
#ata_in=pd.read_csv('TradeStreet.csv',parse_dates=['DateTime']); cal_real=3.5; cal_reactive=1; #Trade Street Warehouse


#------------------------------------------------------------------------------
#function to find replacing position-------------------------------------------
def ReplaceWith(x,y):
    """ x is position of data, and y is corresponding date"""      
    #first day replace with t-1  #first week replace with t-96 
    # all other t-n*96,n is earlier day of same type (business or holiday) 
    if x==1:
        return 1
    elif x>1 and x<96:
        return x-1
    elif x>=96 and x<=96*7:
        return x-96
    else:
        sim_day=1
        nday=datetime.timedelta(days=1)
        while isbday(y, holidays=holidays.US())!=isbday(y-sim_day*nday, holidays=holidays.US()):
            sim_day=sim_day+1
        return x-96*sim_day 
#------------------------------------------------------------------------------    
t = time.time()               
#------------Find Missing Data Dates-------------------------------------------
TimeStamp=data_in[data_in.columns.values[0]]   
StartTime=min(TimeStamp[1],TimeStamp[len(TimeStamp)-1])
EndTime=max(TimeStamp[1],TimeStamp[len(TimeStamp)-1])
tDelta=datetime.timedelta(minutes=15)
TimeAll=[]
current=StartTime
#getting all the time space within data range
while current<=EndTime:
    TimeAll.append(current)
    current=current+tDelta
TimeMiss=list(set(TimeAll)-set(TimeStamp))      
df_miss=pd.DataFrame()
df_miss[data_in.columns.values[0]]=TimeMiss    #time
print('Number of missing datapoints: '+str(len(TimeMiss))+'\n') 
#---------------------Real Power Only------------------------------------------
data_len=len(data_in)
error_real=pd.DataFrame()
error_reactive=pd.DataFrame()

if len(data_in.columns)==2:     
    print('The file has only the real power consumption data.\n')  
    real_power=data_in.columns.values[1]    
             
    #Adding missing data point with nan power
    df_miss[data_in.columns.values[1]]=float('nan')  #
    data_in=data_in.append(df_miss)
    data_in.sort_values('DateTime', ascending=False, inplace=True,ignore_index=True)
    TimeStampNew=data_in[data_in.columns.values[0]]
    
    for i in range(2,data_len):        
        if np.isnan(data_in[real_power][i]):            
            data_in[real_power][i]=data_in[real_power][ReplaceWith(i,TimeStampNew[i])]  
            
    # Data smoothing using gaussian filter
    data_smooth=data_in.copy()
    data_smooth[real_power]=gaussian_filter1d(data_smooth[real_power],2)  
    #Replace error data with suitable data    
    for j in range(len(data_in)):        
        if j<data_len-672:
            avgPower=np.mean(abs(data_in[real_power][j:j+672]))
        if abs(data_in[real_power][j]-data_smooth[real_power][j])>cal_real*avgPower:
            error_real=error_real.append(data_in.loc[j])
            data_in[real_power][j]=data_in[real_power][ReplaceWith(j,TimeStampNew[j])]            
    plt.figure()
    plt.plot(data_in.DateTime, data_in.RealPower)    
    if len(error_real)>0:
        plt.plot(error_real.DateTime, error_real.RealPower,'*')
    plt.title('Real Power')            
        
           
#----------------Both Real and Reactive Power----------------------------------        
if len(data_in.columns)==3:      
    print('The file has both real and reactive power consumption data.\n')  
    real_power=data_in.columns.values[1]
    reactive_power=data_in.columns.values[2]   
    df_miss[data_in.columns.values[1]]=float('nan')
    df_miss[data_in.columns.values[2]]=float('nan')
    data_in=data_in.append(df_miss)
    data_in.sort_values('DateTime', ascending=True, inplace=True,ignore_index=True)
    TimeStampNew=data_in[data_in.columns.values[0]]    
    
    #------------Replace nan power --------------------------------------------
    for i in range(data_len):        
        if np.isnan(data_in[real_power][i]):           
            data_in[real_power][i]=data_in[real_power][ReplaceWith(i,TimeStampNew[i])]      
 
    for i in range(data_len):                
        if np.isnan(data_in[reactive_power][i]):               
            data_in[reactive_power][i]=data_in[reactive_power][ReplaceWith(i,TimeStampNew[i])]           
    #------------Replace erroneous power---------------------------------        
    # Data smoothing using gaussian filter
    data_smooth=data_in.copy()
    data_smooth.RealPower=gaussian_filter1d(data_smooth.RealPower,2)  
    data_smooth.ReactivePower=gaussian_filter1d(data_smooth.ReactivePower,2)           
    for j in range(len(data_in)):
        if j<data_len-672:
            avgReal=np.mean(data_in[real_power][j:j+672])  
        if abs(data_in[real_power][j]-data_smooth[real_power][j])>cal_real*avgReal:            
            error_real=error_real.append(data_in.loc[j])
            data_in[real_power][j]=data_in[real_power][ReplaceWith(j,TimeStampNew[j])]             
    for j in range(1,len(data_in)):        
        if j<data_len-672:
            avgReactive=np.mean(abs(data_in[reactive_power][j:j+672]))
            if avgReactive<10:  #to accomodate low and negative reactive power in Hopkins load
                avgReactive=10;                
        if abs(data_in[reactive_power][j]-data_smooth[reactive_power][j])>cal_reactive*avgReactive:
            error_reactive=error_reactive.append(data_in.loc[j])
            data_in[reactive_power][j]=data_in[reactive_power][ReplaceWith(j,TimeStampNew[j])]         
    plt.figure()
    plt.plot(data_in.DateTime, data_in.RealPower)
    if len(error_real)!=0:
        plt.plot(error_real.DateTime, error_real.RealPower,'*')
    plt.title('Real Power')
    plt.figure()
    plt.plot(data_in.DateTime, data_in.ReactivePower)  
    if len(error_reactive)!=0:
        plt.plot(error_reactive.DateTime, error_reactive.ReactivePower,'*')
    plt.title('Reactive Power')        
#------------------Write Data to File------------------------------------------    
data_in.to_csv('ProcessedData.csv',index = False, header=True)     
#error_real.to_csv('ErrorReal.csv',index = False, header=True)   
#error_reactive.to_csv('ErrorReactive.csv',index = False, header=True)     
#------------------------------------------------------------------------------
print('Number of error datapoints replaced: '+str(len(error_real)+len(error_reactive))+'\n')      
print('Time take to process data: '+str(time.time()-t))