"""
1) Uncomment the corresponing line in data input section.
2) Put data and script in the same folder.
@author: Sushil Silwal, ssilwal@ucsd.edu 
"""
import datetime,time
import pandas as pd
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
t = time.time()
#----------------Uncomment the correspond line---------------------------------
#data_in=pd.read_csv('TradeStreetPV.csv',parse_dates=['DateTime'])
data_in=pd.read_csv('BioEngineeringPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('CSC_BuildingPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('BSB_LibraryPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('BSB_BuildingPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('CUP_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('EBU2_A_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('EBU2_B_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('ElectricShopPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('GarageFleetsPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('GilmanParkingPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('HopkinsParkingPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('KeelingA_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('KeelingB_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('KyoceraSkylinePV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('LeichtagPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('MayerHallPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('MESOM_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('OslerParkingPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('PriceCenterA_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('PriceCenterB_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('SDSC_PV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('SME_SolarPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('PowellPV.csv',parse_dates=['DateTime'])
#data_in=pd.read_csv('StephenBirchPV.csv',parse_dates=['DateTime'])
#------------------------------------------------------------------------------
        
#------------------------------------------------------------------------------
#separating datetime and power data
TimeStamp=data_in[data_in.columns.values[0]]
RealPower=data_in[data_in.columns.values[1]]

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
print('Number of missing datapoints: '+str(len(TimeMiss))+'\n')   
print('Equivalent missing days: '+str(len(TimeMiss)/96)+'\n')

#Adding missing data point with zero power
df_miss=pd.DataFrame()
df_miss['DateTime']=TimeMiss
df_miss['RealPower']=0
data_in=data_in.append(df_miss)
data_in.sort_values('DateTime', ascending=True, inplace=True,ignore_index=True)
data_smooth=data_in.copy()
data_smooth.RealPower=gaussian_filter1d(data_smooth.RealPower,1)
pMax=max(data_smooth.RealPower)   #maximum power generation

#Replace error data with suitable data
error_data=pd.DataFrame()

#First day correction
for i in range(1,96): #skipping the first datapoint
    if data_in.RealPower[i]<-3 or data_in.RealPower[i]>1.1*pMax: 
        error_data=error_data.append(data_in.loc[i])  
        data_in.RealPower[i]=data_in.RealPower[i-1]             
    if data_in.RealPower[i]>1 and data_in.DateTime[i].hour in [21, 22,23,0, 1, 2, 3, 4]:     
        error_data=error_data.append(data_in.loc[i])
        data_in.RealPower[i]=data_in.RealPower[i-1]        
    #if data_in.DateTime[i] in TimeMiss:
     #   data_in.RealPower[i]=data_in.RealPower[i-1]              

#Other day error correction
for i in range(97,len(data_in.RealPower)):    
    if data_in.RealPower[i]<-3 or data_in.RealPower[i]>1.1*pMax:      
        error_data=error_data.append(data_in.loc[i])
        data_in.RealPower[i]=data_in.RealPower[i-96]        
    if data_in.RealPower[i]>1 and data_in.DateTime[i].hour in [21, 22,23,0, 1, 2, 3, 4]: 
        error_data=error_data.append(data_in.loc[i])
        data_in.RealPower[i]=data_in.RealPower[i-96]        
    #if data_in.DateTime[i] in TimeMiss:
     #   data_in.RealPower[i]=data_in.RealPower[i-96]   
    if  data_in.DateTime[i].hour==0 and data_in.DateTime[i].minute==0:
        if max(data_in.RealPower[i-96:i])<=0.1 and i>96*2:
           data_in.RealPower[i-96:i]=data_in.RealPower[i-96*2:i-96] 

data_in.to_csv('Processed.csv',index = False, header=True)     
#error_data.to_csv('ErrorData.csv',index = False, header=True)        

plt.plot(data_in.DateTime, data_in.RealPower)  
if len(error_data)>0:
    plt.plot(error_data.DateTime, error_data.RealPower, '*')

print('Number of error datapoints replaced: '+str(len(error_data))+'\n')      
print('Time take to process data: '+str(time.time()-t))