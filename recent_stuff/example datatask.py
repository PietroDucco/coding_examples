#Northwestern task 1

#import packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder
import os
from itertools import product
from math import sqrt


#importing datasets
d_2009=pd.read_csv('Red_Sox/Red_Sox/red_sox_2009.csv')
d_2009['year']=2009
d_2010=pd.read_csv('Red_Sox/Red_Sox/red_sox_2010.csv')
d_2010['year']=2010
d_2011=pd.read_csv('Red_Sox/Red_Sox/red_sox_2011.csv')
d_2011['year']=2011
d_2012=pd.read_csv('Red_Sox/Red_Sox/red_sox_2012.csv')
d_2012['year']=2012

#Yes a small cycle could have been written, but time is limited
df=pd.concat([d_2009,d_2010,d_2011,d_2012],axis=0)
df=df.reset_index().drop(['index'],axis=1)

#let's look at the dataset
df.describe()
df.info()

#convert dates to datetime
df['transaction_date']=df.year.astype(str) + '_' + df['transaction_date']
df['transaction_date']=pd.to_datetime(df.transaction_date, format='%Y_%m_%d')
df['gamemonth']=pd.to_datetime(df.gamemonth,format='%b').dt.month
df['gamedate']=df.year.astype(str) + ' ' + df.gamedate
df['gamedate']=pd.to_datetime(df.gamedate, format='%Y %b %d')



#the column created using game month is a count of the number of observation for each day
mean_price=df.groupby(['days_from_transaction_until_game']).agg({'price_per_ticket':'mean','gamemonth':'count'})


#PLOT
#plot price_per_ticket by days from transaction_until game
mean_price.price_per_ticket.plot()
mean_price[mean_price.gamemonth>300].price_per_ticket.plot()
plt.ylabel('price')
plt.title('price per ticket by days until game, median')
plt.legend(['all','more than 300 observations'])
plt.savefig('days_till_game_median.png')
plt.close()

#PLOT
#same as before but by year.
mean_price_year=df.groupby(['days_from_transaction_until_game','year']).agg({'price_per_ticket':'mean','gamemonth':'count'})
mean_price_year.price_per_ticket.unstack('year').plot()
plt.ylabel('price')
plt.title('Mean price per ticket by days until game by year')
plt.savefig('days_till_game_median_by_year.png')
plt.close()

#PLOT
#zoomed in the last 50 days before game, plot
mean_price_year.unstack('year').loc[:50].iloc[:,:4].plot()
plt.legend(title='')
plt.savefig('50days.png')
plt.close()


#PLOT
#plot the distribution of tickets by days_from_transaction_until_game
tickets=df.groupby(['days_from_transaction_until_game']).agg({'number_of_tickets':'sum','transaction_date':'count'})
tickets.columns=['tickets','transactions']
t_to_plot=tickets.sort_index(ascending=False).cumsum()
#transform in percentages
tickets_perc=t_to_plot/t_to_plot.loc[0]
tickets_perc.plot()
plt.ylabel('percentage')
plt.title('cumulative distribution of buys')
plt.savefig('cumdistr.png')
plt.close()

#percentiles
#day_n, the furthest date from the game when the n_amount of ticket has been sold.
day_50=tickets_perc[tickets_perc.transactions>=0.5].idxmin()
day_25=tickets_perc[tickets_perc.transactions>=0.25].idxmin()
day_75=tickets_perc[tickets_perc.transactions>=0.75].idxmin()
day_80=tickets_perc[tickets_perc.transactions>=0.80].idxmin()
day_90=tickets_perc[tickets_perc.transactions>=0.90].idxmin()
day_10=tickets_perc[tickets_perc.transactions>=0.10].idxmin()
day_60=tickets_perc[tickets_perc.transactions>=0.60].idxmin()
#report them in a table, copied by hand


#PLOT
#plot cumulative distribution by year
tickets_year=df.groupby(['days_from_transaction_until_game','year']).agg({'number_of_tickets':'sum','transaction_date':'count'})
tickets_year.columns=['tickets','transactions']
t_to_plot=tickets_year.unstack('year').sort_index(ascending=False).cumsum()
#transform in percentages
tickets_perc_year=t_to_plot/t_to_plot.loc[0]
tickets_perc_year.iloc[:,:4].plot()
plt.ylabel('percentage')
plt.title('cumulative distribution of ticket-buys, by year')
plt.legend(title='')
plt.savefig('cumdistr_year.png')
plt.close()


#comparison OAKLAND ATHLETIC and NYY
comp=df[df.team.isin(['OAK','NYY'])]

#PLOT
#plot ticket price by team and days_from_transaction_until_game
price_team=comp.groupby(['team','days_from_transaction_until_game'])['price_per_ticket'].mean().unstack().T
price_team.plot()
plt.ylabel('price_tickets')
plt.title('comparison mean ticket price, by team')
plt.savefig('team_price.png')
plt.close()

#PLOT
#cumulative distribution by team
tickets_team=comp.groupby(['team','days_from_transaction_until_game'])['number_of_tickets'].sum()
tickets_team=tickets_team.unstack('team').sort_index(ascending=False).cumsum()
#convert to percentages
tickets_perc_team=tickets_team/tickets_team.loc[0]
tickets_perc_team.plot()
plt.ylabel('share of ticket sold')
plt.title('cumulative distribution of tickets sold, by team')
plt.savefig('team_distr.png')
plt.close()


#REGRESSION


#create bins by time
bin_edges = [-1, 0,1, 2, 5, 10, 25, 50,100,150,300]


#prepare data
# Create bins for var1
df['until_bins'] = pd.cut(df['days_from_transaction_until_game'], bins=bin_edges)
df['number_of_tickets_2']=df['number_of_tickets']-1  #additional tickets
df['week_game']=(df.weekend_game-1).apply(abs)


#create bins dummies using bin_edges, excluding the first one
bins_dummies=pd.get_dummies(df.until_bins,drop_first=True).astype(float) #(-1,1] has been dropped

#create section_dummies
section_dummies=pd.get_dummies(df.sectiontype,drop_first=True).astype(float)   # DUGOUTBOX has been dropped

#create year dummies
year_dummies=pd.get_dummies(df.year,drop_first=True).astype(float) #2009 dropped

#create team dummies
team_dummies=pd.get_dummies(df.team,drop_first=True).astype(float) #ATL dropped

#create month dummies
month_dummies=pd.get_dummies(df.gamemonth).astype(float) #NOne dropped
month_dummies.columns=['April','May','June','July','August','September','October']
month_dummies=month_dummies.drop(['June'],axis=1) #drop June

#create ineraction between bins and years dummies
column_combinations = list(product(bins_dummies.columns, year_dummies.columns))


interaction_bins_year = pd.DataFrame()

for col1, col2 in column_combinations:
    #create interaction_bins_year
    interaction_bins_year[f'{col1}_{col2}'] = bins_dummies[col1] * year_dummies[col2]

#prepare for regression
df_reg=pd.concat([bins_dummies,section_dummies,month_dummies,year_dummies,interaction_bins_year,team_dummies,df.loc[:,['logprice','day_game','week_game','number_of_tickets_2']]], axis=1 )

#drop NA
df_reg=df_reg.dropna()
Y=df_reg.logprice
X=df_reg.drop('logprice',axis=1)
#add constant
X=sm.add_constant(X)

#fit regression
OLS_res=sm.OLS(Y,X).fit()

#print summary to latex
print(OLS_res.summary().as_latex())


#prepare chart and table using results
parameters=OLS_res.params.copy()
parameters.index=parameters.index.astype(str)


#create years and bin cofficient estimate table
years_coeff=pd.DataFrame(parameters.loc[:'(150, 300]'],columns=['2009'])
years_coeff['2010']=parameters.loc[['2010','(0, 1]_2010','(1, 2]_2010','(2, 5]_2010', '(5, 10]_2010','(10, 25]_2010','(25, 50]_2010','(50, 100]_2010','(100, 150]_2010','(150, 300]_2010']].values
years_coeff['2011']=parameters.loc[['2011','(0, 1]_2011','(1, 2]_2011','(2, 5]_2011', '(5, 10]_2011','(10, 25]_2011','(25, 50]_2011','(50, 100]_2011','(100, 150]_2011','(150, 300]_2011']].values
years_coeff['2012']=parameters.loc[['2012','(0, 1]_2012','(1, 2]_2012','(2, 5]_2012', '(5, 10]_2012','(10, 25]_2012','(25, 50]_2012','(50, 100]_2012','(100, 150]_2012','(150, 300]_2012']].values

#these are interaction variables with 2009, (-1,0] in the intercept
# sum is needed since the constant includes 2009 while 2010 fixed effect is the difference with the values in 2009 and the same for the interaction terms
years_coeff['2010']=years_coeff['2010']+years_coeff['2009']
years_coeff['2011']=years_coeff['2011']+years_coeff['2009']
years_coeff['2012']=years_coeff['2012']+years_coeff['2009']

last_day=years_coeff.loc['const'].values
#need to add the constant to every row that is not (0, 1]
years_coeff=years_coeff.drop(['const'],axis=0)+years_coeff.loc['const']

years_coeff.loc['(-1, 0]']=last_day

years_coeff=years_coeff.loc[['(-1, 0]','(0, 1]','(1, 2]','(2, 5]', '(5, 10]','(10, 25]','(25, 50]','(50, 100]','(100, 150]','(150, 300]'],:]

#standard error
std_err=OLS_res.bse.copy()
std_err.index=std_err.index.astype(str)

#same for standard errors using the right formula

errors=pd.DataFrame(std_err.loc[:'(150, 300]'],columns=['2009'])
errors['2010']=std_err.loc[['2010','(0, 1]_2010','(1, 2]_2010','(2, 5]_2010', '(5, 10]_2010','(10, 25]_2010','(25, 50]_2010','(50, 100]_2010','(100, 150]_2010','(150, 300]_2010']].values
errors['2011']=std_err.loc[['2011','(0, 1]_2011','(1, 2]_2011','(2, 5]_2011', '(5, 10]_2011','(10, 25]_2011','(25, 50]_2011','(50, 100]_2011','(100, 150]_2011','(150, 300]_2011']].values
errors['2012']=std_err.loc[['2012','(0, 1]_2012','(1, 2]_2012','(2, 5]_2012', '(5, 10]_2012','(10, 25]_2012','(25, 50]_2012','(50, 100]_2012','(100, 150]_2012','(150, 300]_2012']].values

errors['2010']=(errors['2010']**2+errors['2009']**2)**0.5
errors['2011']=(errors['2011']**2+errors['2009']**2)**0.5
errors['2012']=(errors['2012']**2+errors['2009']**2)**0.5

errors_const=errors.loc['const'].values

errors=(errors.drop(['const'],axis=0)**2 + errors_const**2)**0.5

errors.loc['(-1, 0]']=errors_const

errors=errors.loc[['(-1, 0]','(0, 1]','(1, 2]','(2, 5]', '(5, 10]','(10, 25]','(25, 50]','(50, 100]','(100, 150]','(150, 300]'],:]

#PLOT ERRORBARS
x_values = np.arange(1, 11)

for year in errors.columns:
    y_values = years_coeff[year]
    error_values = 1.96 * errors[year]  # 1.96 corresponds to a 95% confidence interval
    
    #plot bars 
    plt.errorbar(x_values, y_values, yerr=error_values, label=year, marker='o', linestyle='-')



#save plot
plt.xlabel('days before the game')
plt.ylabel('effect on log_price')
plt.xticks(ticks=x_values,labels=errors.index, size=8)
plt.title('effect estimates of time variable, using bins')
plt.legend([2009,2010,2011,2012])
plt.savefig('coeff.png')
plt.close()


#effects table
effects=((years_coeff-years_coeff.loc['(-1, 0]']).apply('exp') -1)*100


#copy table to latex
print(effects.iloc[1:,:].to_latex())





