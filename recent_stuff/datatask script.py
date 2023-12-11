#Northwestern task 2

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder
import os
from itertools import product

#load data
columns=['countyname','state','contract','healthplanname','typeofplan','countyssa','eligibles','enrollees','penetration','ABrate']
df=pd.read_csv('Medicare_Advantage/scp-1205.csv',names=columns, index_col=False)


#convert numeric data
df['ABrate']=pd.to_numeric(df.ABrate, errors='coerce') #NA? no guidance
df['eligibles']=pd.to_numeric(df.eligibles, errors='coerce').fillna(0)
df['enrollees']=pd.to_numeric(df.enrollees, errors='coerce').fillna(0)
df['penetration']=pd.to_numeric(df.penetration, errors='coerce').fillna(0)
#drop leading and trailing spaces in text columns
df['countyname']=df.countyname.str.strip()
df['healthplanname']=df.healthplanname.str.strip()
df['typeofplan']=df.typeofplan.str.strip()


## MANAGING odd entries
#after finding this very useful resource https://www.cms.gov/data-research/statistics-trends-and-reports/health-plans-reports-files-data/scp
#I understood that Unusual SCounty Code is given to counties outside of the US or a US protectorate and these are not distinguishable, since they all get the same countyssa code.
#Including them will result in an aggregate that is not of our interest

#Under-11 would be very useful, but not for our analysis at the county level, UNDER-11 includes an aggregate by state that we cannot divide to counties 

#I removed all the entries whith 'Unusual SCounty Code' and 'UNDER-11' in countyname and '99','  ' in state
df=df[df.countyname!='Unusual SCounty Code']
df=df[df.state!='99']
df=df[df.state!='  ']
df=df[df.countyname!='UNDER-11']

#strip state variable
df['state']=df.state.str.strip()

#excluded all the territories. But I kept DC
df=df[~df.state.isin(['AS','GU','VI','PR'])]



#check if countyssa and countyname, state make a bijection
bi=df.copy()
bi['county_state']= bi['countyname'] + bi['state']
bi=bi.drop_duplicates(subset=('county_state','countyssa'))

#if the number of the unique element in the first column is equal to the row of the dataset, it means that there is no repetition in the first column.
#For the second column is the above. If both have only unique values then it is a bijection.
is_bijection = len(bi['county_state'].unique()) == len(bi['countyssa'].unique()) == len(bi)


#DATASET CREATION


#I will create the variables of the final dataset one at a time and then concatenate over the index (that is unique)


#NUMBEROFPLANS1

#my interpretation of the numberofplans1 is that I should consider all the plans that have recorded more than 10 enrollees IN A COUNTY
#just by looking at df.drop_duplicates(subset=('countyname','state','healhtplanname')), it looks like some plans are repeated more than once per county
#I will need to groupby twice.

#aggregate over county, state, healhtplanname, sum enrollees
agg_1=df.groupby(['countyname','state','healthplanname'])['enrollees'].sum()
#then count how many unique plans are above 10 enrollees
numberofplans1 = agg_1.reset_index().groupby(['countyname','state']).apply(lambda group: len(group[group.enrollees>10]['healthplanname'].unique())).rename('numberofplans1')

#is the penetration of the plan singular for instance or not? I will do the total
#let's group over the plan's


#NUMBEROFPLANS2


#My interpretation is that I have to look for all the plans that had a penetration over 0.5% in a county. Not overall. This was my understanding
#compute penetration of plans
agg_1=df.groupby(['countyname','state','healthplanname']).agg({'eligibles':'mean','enrollees':'sum'})
#why eligibles mean?
#every county has always the same number of eligibles for any plan
# it can be checked by using df.groupby(['countyname','state'])['eligibles'].unique().apply(len).sum()

agg_1['penetration']=100*agg_1['enrollees']/agg_1['eligibles']
numberofplans2=agg_1.reset_index().groupby(['countyname','state']).apply(lambda group: len(group[group.penetration>0.5]['healthplanname'].unique())).rename('numberofplans2')



#COUNTYSSA

#since unique() fills the value with a list of 1, max will fill it with the maximum entry, the only one.
countyssa=df.groupby(['countyname','state'])['countyssa'].max()


#ELIGIBLES

#assuming they are all medicare eligible
#every county has always the same number of eligibles for any plan
# it can be checked by using df.groupby(['countyname','state'])['eligibles'].unique().apply(len).sum()
eligibles=df.groupby(['countyname','state'])['eligibles'].mean()



#I did not understand if all are MA plans or only some
#which plans are MA? 
# https://www.cms.gov/data-research/statistics-trends-and-reports/health-plans-reports-files-data/scp says that all are, so I will take this source
# precisely it doesn't talk about DEMC, however the dataset itself is about MA enrollees so I counted it as well.
totalenrollees=df.groupby(['countyname','state'])['enrollees'].sum().rename('totalenrollees')



#the definition of totalpenetration is not very clear, are all individuals that are eligible for a MA plan (so the ones in the list at row 81) or just any plan? I will consider any plan
totalpenetration=(100*totalenrollees/eligibles).rename('totalpenetration')

#concatenate all done above
dataset=pd.concat([numberofplans1,numberofplans2,countyssa,eligibles,totalenrollees,totalpenetration],axis=1)
#move index (countyname, state) to columns in the dataset and add numerical index
dataset=dataset.reset_index()

#sort columns in the desired order
dataset=dataset.loc[:,['countyname','state','numberofplans1','numberofplans2','countyssa','eligibles','totalenrollees','totalpenetration']]
#sort values in the desired order
dataset=dataset.sort_values(by=['state','countyname'])

#save dataset
dataset.to_csv('task2NW.csv')

print('dataset saved')

#I needed 1 hour and a half, of which 20 minutes were lost googling which plans are MA
