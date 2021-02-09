"""
Please read the following instruction befor using the code:
    1) Keep the data file in the same folder as this script.
    2) Uncomment the corresponding line in data input section.    
       
@author: Sushil Silwal, ssilwal@ucsd.edu 
"""
import datetime, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bdateutil import isbday
import holidays

#----------------------Data Input--------------------------------------------------------
#data_in=pd.read_csv('BatteryStorage.csv',parse_dates=['DateTime']); Rating=1800; 
data_in=pd.read_csv('TradeStreetBattery.csv',parse_dates=['DateTime']); Rating=200;

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
real_power=data_in.columns.values[1]                 
#Adding missing data point with nan power
df_miss[data_in.columns.values[1]]=float('nan') 
data_in=data_in.append(df_miss)
data_in.sort_values('DateTime', ascending=False, inplace=True,ignore_index=True)
TimeStampNew=data_in[data_in.columns.values[0]]    
for j in range(len(data_in)):       
    if np.isnan(data_in[real_power][j]):        
        data_in[real_power][j]=data_in[real_power][ReplaceWith(j,TimeStampNew[j])]   
Error=0
for j in range(len(data_in)):       
    if abs(data_in[real_power][j])>Rating:        
        data_in[real_power][j]=data_in[real_power][ReplaceWith(j,TimeStampNew[j])]   
        Error=Error+1        
plt.figure()
plt.plot(data_in.DateTime, data_in[real_power])          
            
#------------------Write Data to File------------------------------------------    
data_in.to_csv('ProcessedBatteryStorage.csv',index = False, header=True)     
   
print('Numbers of errors: '+str(Error))
print('Time take to process data: '+str(time.time()-t))