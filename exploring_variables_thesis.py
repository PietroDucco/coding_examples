import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path
import os
from scipy import stats
from tecnico import read_csv, to_csv, less_mem, carica_tutto_sample, map_prof, make_db_OB
from math import log,exp
import seaborn as sns
from statsmodels.stats.oaxaca import OaxacaBlinder,OaxacaResults
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col

def pop_ed():
    url=Path.home()/'Downloads/true_ed_level4.csv'
    ed=pd.read_csv(url)
    ed['time_type']=ed.TIME.str.count('Q').map({0:'A',1:'Q'})
    ed=ed[ed.time_type=='A']
    ed=ed[ed.ETA1=='Y15-64']
    ed['ANNO']=ed.TIME.astype('int16')
    ed['SESSO']=ed.Sesso.map({'femmine':2,'maschi':1})
    ed['stud']=ed['Titolo di studio'].map({'licenza di scuola elementare, nessun titolo di studio':'bupps','licenza di scuola media':'bupps',
                                           'diploma 2-3 anni (qualifica professionale)':'bupps','diploma 4-5 anni (maturità)':'upps','laurea e post-laurea':'ter','totale':'tot','diploma':'diploma'
                                           })
    ed['RIP3']=ed.Territorio.map({'Nord':1,'Centro':2,'Mezzogiorno':3})
    ed['TOT']=ed.stud.map({'tot':1,'upps':0,'bupps':0,'ter':0,'diploma':0})
    
    ed1=ed[ed.TOT==0].loc[:,['SESSO','ANNO','RIP3','Value','stud']]
    ed2=ed[ed.TOT==1].loc[:,['SESSO','ANNO','RIP3','Value','stud']]
    
    tab1=pd.pivot_table(ed1, 'Value',['SESSO','ANNO','RIP3'],'stud','sum')
    tab2= pd.pivot_table(ed2, 'Value',['SESSO','ANNO','RIP3'], 'stud','sum')
    tab=tab1/tab2.values
    
    tab.columns=[1,3,2]
    tab.columns.name='ed_lvl'
    tab.index.names=['SESSO','ANNO','RIP3']
    tab=tab.stack('ed_lvl').unstack('SESSO')
    #tab.columns=[2,1]
    tab=tab.sort_index()
    #tab=tab.reindex(sorted(tab.columns),axis=1)
    tab.columns.name='SESSO'
    return tab.stack('SESSO').unstack(['ANNO','SESSO'])
    #return tab

    
    

def plot():
    plt.style.use('Solarize_Light2')
    
    plt.rcParams['figure.facecolor']='#f1ebd8'
    
def wages_gap(dati, DIV3=False):
    
    if DIV3:
        tab=pd.pivot_table(dati, values='RETRIC', index=['ANNO','TRIM','RIP3'], columns='SESSO', aggfunc='median')
        result=(1- tab.loc[:,2]/tab.loc[:,1]).unstack()
    else:
        tab=pd.pivot_table(dati, values='RETRIC', index=['ANNO','TRIM'], columns='SESSO', aggfunc='median')
        result=1- (tab.loc[:,2]/tab.loc[:,1])
    return result


def get_quantile_med_women(dati):
    value=dati[dati.SESSO==2].RETRIC.median()
    
    a = dati[dati.SESSO==1].RETRIC.quantile(np.arange(0,1,0.0001))
    return a.loc[a.values==int(value)].index.values.mean()


def get_avg_quant_women(dati1,dati2,mean=False, logit=False):
   
    #da finire
    #secondo input di dati che mi da la distribuzione della wage structure con cui mi confronto
    #preso il quantile dalla prima lo mettiamo sulla seconda e otteniamo uno stipendio
    #con lo stipendio facciamo una media che confrontiamo con la media degli uomini di quella distribuzione
    
    
    if dati1 is dati2:
        if mean:
            return dati2[dati2.SESSO==2].RETRIC.mean()/dati2[dati2.SESSO==1].RETRIC.mean()
        if logit:
            return exp(dati2[dati2.SESSO==2].log_hwage.mean() - dati2[dati2.SESSO==1].log_hwage.mean())
        return dati2[dati2.SESSO==2].RETRIC.median()/dati2[dati2.SESSO==1].RETRIC.median()
        
    value=pd.DataFrame(dati1[dati1.SESSO==2].log_hwage, columns=['log_hwage'])
    
    
    get_quant = lambda x: stats.percentileofscore(dati1[dati1.SESSO==1].log_hwage,x)
    
    perc = pd.DataFrame(dati1[dati1.SESSO==2].log_hwage.unique(), index= dati1[dati1.SESSO==2].log_hwage.unique(), columns=['quant'])
    perc.quant=perc.quant.apply(get_quant)
        
    
    #use perc
    get_wage = lambda x: np.quantile(dati2[dati2.SESSO==1].log_hwage,x/100)
    #fai l'opposto di perc sull'altra distr
    #wage = pd.DataFrame(perc.quant.unique())
    
    perc['att_wage']=perc.quant.apply(get_wage)
    
    get_att_wage = lambda x: perc.loc[x,'att_wage']
    
    #usa get_wage e computa result
    value['att_wage']=value.log_hwage.apply(get_att_wage)
    if mean:
        return  value.att_wage.mean()/dati2[dati2.SESSO==1].log_hwage.mean()
    if logit:
        return  exp(value.att_wage.mean() - dati2[dati2.SESSO==1].log_hwage.mean())
    return  value.att_wage.median()/dati2[dati2.SESSO==1].RETRIC.median() #np.quantile(dati2[dati2.SESSO==1].RETRIC,value.quant.mean()/100)/dati2[dati2.SESSO==1].RETRIC.mean() #value.att_wage.mean()/dati2[dati2.SESSO==1].RETRIC.mean()
        
        
    

def get_quant_tab(dati,RIP3=False,mean=False, logit=False):
    
    
    if RIP3:
        result=pd.DataFrame(columns=['ANNO','TRIM','RIP3','quant'])
        for a in dati.ANNO.unique():
            
            for t in dati.TRIM.unique():
                print('done, ANNO:',a,' trim :',t)
                for r in dati.RIP3.unique():
                    x=pd.DataFrame(columns=['ANNO','TRIM','RIP3','quant'])
                    x.loc[0,:]=[a,t,r,get_avg_quant_women(dati[(dati.TRIM==t) & (dati.ANNO==a) & (dati.RIP3==r)],dati[(dati.TRIM==t) & (dati.ANNO==a) & (dati.RIP3==1)], mean,logit)]
                    result=result.append(x, ignore_index=True)
    
        result=result.sort_values(['ANNO','TRIM','RIP3'], axis=0)
    else:
        result=pd.DataFrame(columns=['ANNO','TRIM','quant'])
        for a in dati.ANNO.unique():
           
            for t in dati.TRIM.unique():
                print('done, ANNO:',a,' trim :',t)
                x=pd.DataFrame(columns=['ANNO','TRIM','quant'])
                x.loc[0,:]=[a,t,get_avg_quant_women(dati[(dati.TRIM==t) & (dati.ANNO==a)],dati[(dati.TRIM==t) & (dati.ANNO==a)], mean,log)]
                result=result.append(x, ignore_index=True)
    
        result=result.sort_values(['ANNO','TRIM'], axis=0)
        
    result.index=pd.MultiIndex.from_frame(result.iloc[:,:-1])
    result=result.drop(result.columns[:-1].values,axis=1)
    
    if RIP3:
        result=result.unstack()
    return result
    

def line_plot(dati,rolling=1,title='', ylabel='',text='',salva=False, nome='', div=False ):
    plot()
    if div:
        for i in dati.columns:
            dati.loc[:,i].rolling(rolling).mean().plot(label=i)
        plt.legend(['NORTH','CENTER','SOUTH'])
    else:
        dati.rolling(rolling).mean().plot(legend=None)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.figtext(0.02, 0.03, text,color='k')
    plt.xlabel('YEAR')
    if salva:
        plt.savefig('immagini/{nome}.png', facecolor='#f1ebd8')
    
    
def get_partition(dati):
    #stipendi
    tab=pd.pivot_table(dati, 'hourly_wage', ['ANNO','RIP3'], ['SESSO','PRIVPUBL'], 'mean')
    tot=pd.pivot_table(dati, 'hourly_wage', ['ANNO','RIP3'], 'SESSO', 'mean')
    stipendi=pd.concat([tab,tot],axis=1)
    stipendi.columns=['MEN-PRIV','MEN-PUBL','WOMEN-PRIV','WOMEN-PUBL','TOT MEN','TOT WOMEN']
    stipendi=stipendi.stack().unstack('RIP3').unstack()
    del tab,tot
    tab=pd.pivot_table(dati, 'log_hwage', ['ANNO','RIP3'], ['SESSO','PRIVPUBL'], 'count')
    tot=tab.copy()
    omini=tot.iloc[:,:2].T.sum()
    donne=tot.iloc[:,2:].T.sum()
    tot.iloc[:,0]=omini
    tot.iloc[:,1]=omini
    tot.iloc[:,2]=donne
    tot.iloc[:,3]=donne
    share=tab/tot
    share=share.unstack('RIP3')
    share=share.stack().stack().stack().unstack('RIP3').unstack('SESSO').unstack('PRIVPUBL')
    del omini,donne,tot,tab
    
    
    tab=pd.pivot_table(dati, 'log_hwage', ['ANNO','TRIM','RIP3'], ['SESSO','PRIVPUBL'], 'mean')
    tot=pd.pivot_table(dati, 'log_hwage', ['ANNO','TRIM','RIP3'], 'SESSO', 'mean')
    stipendi2=pd.concat([tab,tot],axis=1)
    stipendi2.columns=['MEN-PRIV','MEN-PUBL','WOMEN-PRIV','WOMEN-PUBL','TOT MEN','TOT WOMEN']
    stipendi2=stipendi2.stack().unstack('RIP3').unstack()
    del tab,tot
    
    
    to_use=stipendi2.stack('RIP3')
    to_use2=stipendi.stack('RIP3')
    ratios_general= pd.concat([(to_use2.iloc[:,1]/to_use2.iloc[:,0]),(to_use2.iloc[:,5]/to_use2.iloc[:,4])],axis=1)
    wage_ratios=(to_use.iloc[:,3]-to_use.iloc[:,2]).apply(exp)
    ratios_general.columns=['MEN publpriv ratio','WOMEN publpriv ratio']
    ratios_general=ratios_general.unstack()
    wage_ratios=wage_ratios.unstack()
    del to_use,to_use2,stipendi2
    return (stipendi, share, ratios_general,wage_ratios)
    

def GWR_age(dati):
    
    inf=dati[(dati.CLETAS>5) & (dati.CLETAS<15)]
    tab=pd.pivot_table(inf, 'hourly_wage', ['ANNO','RIP3','CLETAS'],'SESSO','mean')
    wage_rt=tab.iloc[:,1].apply(log) - tab.iloc[:,0].apply(log)
    wage_rt=wage_rt.apply(exp)
    tab2=pd.pivot_table(inf, 'hourly_wage', ['ANNO','CLETAS'],'SESSO','mean')
    tab2['RIP3']=4
    tab2['ANNO']=tab2.index.get_level_values(0).values
    tab2['CLETAS']=tab2.index.get_level_values(1).values
    tab2.index=pd.MultiIndex.from_frame(tab2.loc[:,['ANNO','RIP3','CLETAS']])
    tab2=tab2.drop(['ANNO','RIP3','CLETAS'],axis=1)
    tot=tab2.iloc[:,1].apply(log) - tab2.iloc[:,0].apply(log)
    tot=tot.apply(exp)
    result=pd.concat([wage_rt,tot])
    
    result=result.unstack('RIP3').unstack('ANNO')
    result.index=result.index.map(mappa_CLETAS)
    return result

def log_ratio(dati):
    
    #dati['log_RETRIC']= dati.RETRIC.apply(log)
   
    tot=pd.pivot_table(dati, 'log_hwage', ['ANNO','TRIM'], 'SESSO', 'mean')
    
    result= tot.iloc[:,1] - tot.iloc[:,0]
    
    return result.apply(exp)
    
def age_publ(dati):
    inf=dati[(dati.CLETAS>5) & (dati.CLETAS<15)]
    inf['CLETAS']=inf.CLETAS.map(mappa_CLETAS)
    public=pd.pivot_table(inf, 'PRIVPUBL', ['RIP3','SESSO'], 'CLETAS','mean')
    
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['RIP3','SESSO'], 'CLETAS','count')
    
    stipendi=pd.pivot_table(inf, 'hourly_wage', ['RIP3','SESSO'], 'CLETAS','mean')
    tab2=tab2.T
    
    distr=tab2/tab2.sum()
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['ANNO','RIP3','SESSO'], 'CLETAS','count')
    tab2=tab2.T
    #distr_anno=tab2/tab2.sum()
    
    var=[distr.iloc[:,:2].diff(1,axis=1).iloc[:,1].var(),distr.iloc[:,2:4].diff(1,axis=1).iloc[:,1].var() , distr.iloc[:,4:].diff(1,axis=1).iloc[:,1].var()]
    distr_anno=(tab2/tab2.sum()).stack('RIP3').unstack('CLETAS').stack('CLETAS')
    omini_diff=distr_anno.iloc[:,-2] - distr_anno.iloc[:,0] 
    donne_diff=distr_anno.iloc[:,-1] - distr_anno.iloc[:,1]
    diff_8_20=pd.concat([omini_diff,donne_diff],axis=1)
    
    
    return public,stipendi,distr,var, distr_anno, diff_8_20
#distr_anno.stack().loc[:,[2008,2020]].unstack().unstack('RIP3').cumsum()   
    

mappa_CLETAS={1:'0-2',2:'3-5',3:'6-10',4:'11-14',
              5:'15-19',6:'20-24',7:'25-29',8:'30-34',
              9:'35-39',10:'40-44',11:'45-49',12:'50-54',
              13:'55-59',14:'60-64',15:'60-69',16:'70-74',17:'75+'}

mappa_titolo_di_studio={ 1:1,2:1,3:1,4:1,5:2,6:2,7:2,8:3,9:3,10:3,11:3
                        }
map_2={1:'bupps',2:'upps',3:'ter'}


def ed_lvl(inf):
    
    inf['ed_lvl']= inf.titolo_di_studio.map(mappa_titolo_di_studio)
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['RIP3','SESSO'], 'ed_lvl','count')
    stipendi=pd.pivot_table(inf, 'hourly_wage', ['RIP3','SESSO'], 'titolo_di_studio','mean')
    tab2=tab2.T
    distr=tab2/tab2.sum()
    var=[distr.iloc[:,:2].diff(1,axis=1).iloc[:,1].var(),distr.iloc[:,2:4].diff(1,axis=1).iloc[:,1].var() , distr.iloc[:,4:].diff(1,axis=1).iloc[:,1].var()]
    distr_big=pd.pivot_table(inf[(inf.tipo_titolo_studio>0) & (inf.titolo_di_studio>4)], 'hourly_wage', ['RIP3','SESSO','titolo_di_studio'], 'tipo_titolo_studio','count')
    stip_big=pd.pivot_table(inf[(inf.tipo_titolo_studio>0)& (inf.titolo_di_studio>4)], 'hourly_wage', ['RIP3','SESSO','titolo_di_studio'], 'tipo_titolo_studio','mean')
    
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['ANNO','RIP3','SESSO'], 'ed_lvl','count')
    tab2=tab2.T
    distr_anno=(tab2/tab2.sum()).stack('RIP3').unstack('ed_lvl').stack('ed_lvl')
    omini_diff=distr_anno.iloc[:,-2] - distr_anno.iloc[:,0] 
    donne_diff=distr_anno.iloc[:,-1] - distr_anno.iloc[:,1]
    diff_8_20=pd.concat([omini_diff,donne_diff],axis=1)
    return stipendi,distr,var, distr_big,stip_big, distr_anno, diff_8_20

#fare tab di distr_anno filtered only 2008-2020 dove vediamo la distribuzione uomini e donne, magari prima 
# prima di farla aggiusta i labels così non smaroni dopo

# fare una mappa per titolo di studio nei vari cosi, da fare una partizione aggregata.

def get_pos(inf):
    #inf=dati[dati.titolo_di_studio.notna()].copy()
    #inf['ed_lvl']= inf.titolo_di_studio.map(mappa_titolo_di_studio)
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['RIP3','SESSO'], 'POSPRO','count')
    stipendi=pd.pivot_table(inf, 'hourly_wage', ['RIP3','SESSO'], 'POSPRO','mean')
    tab2=tab2.T
    distr=tab2/tab2.sum()
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['ANNO','RIP3','SESSO'], 'POSPRO','count')
    tab2=tab2.T
    distr_anno=tab2/tab2.sum()
    var=[distr.iloc[:,:2].diff(1,axis=1).iloc[:,1].var(),distr.iloc[:,2:4].diff(1,axis=1).iloc[:,1].var() , distr.iloc[:,4:].diff(1,axis=1).iloc[:,1].var()]
    
    diff_8_20= (- distr_anno.stack().stack().iloc[:,0] + distr_anno.stack().stack().iloc[:,-1]).unstack('SESSO')
    diff_8_20=diff_8_20.unstack('POSPRO').stack('POSPRO')
    
    a=distr_anno.stack().stack().loc[:,[2008,2020]].unstack('SESSO').unstack('POSPRO').stack('POSPRO')
    gap=(a.stack('ANNO').iloc[:,0] - a.stack('ANNO').iloc[:,1])
    
    
    return stipendi, distr, var, distr_anno, diff_8_20.stack('SESSO').unstack('RIP3').unstack('SESSO'), gap.unstack('ANNO')


legenda=['Men North','Women North','Men Center','Women Center','Men South','Women South']


def get_duratt(dati):
    
    
    
    return dati.loc[:,['PRIVPUBL','DURATT','SESSO','RIP3']].groupby(['RIP3','SESSO','PRIVPUBL']).mean().unstack('RIP3'), 
    
def get_attr(inf, attr):
    #inf=dati[dati.titolo_di_studio.notna()].copy()
    #inf['ed_lvl']= inf.titolo_di_studio.map(mappa_titolo_di_studio)
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['RIP3','SESSO'], attr,'count')
    stipendi=pd.pivot_table(inf, 'hourly_wage', ['RIP3','SESSO'], attr,'mean')
    tab2=tab2.T
    distr=tab2/tab2.sum()
    tab2=pd.pivot_table(inf, 'PRIVPUBL', ['ANNO','RIP3','SESSO'], attr,'count')
    tab2=tab2.T
    distr_anno=tab2/tab2.sum()
    var=[distr.iloc[:,:2].diff(1,axis=1).iloc[:,1].var(),distr.iloc[:,2:4].diff(1,axis=1).iloc[:,1].var() , distr.iloc[:,4:].diff(1,axis=1).iloc[:,1].var()]
    
    diff_8_20= (- distr_anno.stack().stack().iloc[:,0] + distr_anno.stack().stack().iloc[:,-1]).unstack('SESSO')
    diff_8_20=diff_8_20.unstack(attr).stack(attr)
    
    a=distr_anno.stack().stack().loc[:,[2008,2020]].unstack('SESSO').unstack(attr).stack(attr)
    gap=(a.stack('ANNO').iloc[:,0] - a.stack('ANNO').iloc[:,1])
    
    
    return stipendi, distr, var, distr_anno, diff_8_20.stack('SESSO').unstack('RIP3').unstack('SESSO'), gap.unstack('ANNO')#, pd.pivot_table(inf, attr, ['RIP3','SESSO'],'ANNO','mean')

 


def ed_segr(dati):
    pass # unisci le distribuzioni e differenzia sulla base di lavoratori e popolazione, poi mettilo nel formato giusto per get_segregation
    _,_,_,_,_,distr_anno,_=ed_lvl(dati[dati.CLETAS<15])
    distr_anno=distr_anno.unstack(['RIP3','ed_lvl']).unstack(['SESSO','RIP3','ed_lvl']).T
    tab=pop_ed()
    tab=tab.unstack(['RIP3','ed_lvl']).unstack(['SESSO','RIP3','ed_lvl']).T
    tot=pd.concat([tab,distr_anno], keys=['pop','work'])
    tot.index.names=['type','SESSO','RIP3','ed_lvl']
    tot=tot.stack('ANNO').unstack(['SESSO','ed_lvl','ANNO','RIP3']).T
    #tot=tot.stack('ANNO').unstack(['RIP3','ANNO','ed_lvl']).T
    result=tot.diff(axis=1).iloc[:,-1].abs().unstack(['SESSO','ANNO','RIP3']).sum().unstack('ANNO').T*0.5
    
    t2= tot.diff(axis=1).iloc[:,-1].unstack(['SESSO','ANNO','RIP3']).T.sort_index().T
    return result.stack(['RIP3','SESSO']).unstack(['RIP3','SESSO']), t2.T.unstack('RIP3'),tot.sort_index()
    #omini=tot.iloc[:117,:].copy().droplevel('SESSO')
#    donne=tot.iloc[117:,:].copy().droplevel('SESSO')
 #   omini=omini.unstack(['ANNO','RIP3']).stack('type').unstack('type')
  #  donne=donne.unstack(['ANNO','RIP3']).stack('type').unstack('type')
    
   # return (get_segregation(omini),get_segregation(donne))
    
    


def get_segregation(distr_anno):
    #asse x tieni sola la var
    distr_anno=distr_anno.fillna(0)
    return distr_anno.stack(['ANNO','RIP3']).diff(axis=1).iloc[:,-1].abs().unstack(['ANNO','RIP3']).sum().unstack('ANNO').T *0.5

def my0(g):
    return np.percentile(g,0)
def my01(g):
    return np.percentile(g,1)
def my05(g):
    return np.percentile(g,5)
def my10(g):
    return np.percentile(g,10)
def my15(g):
    return np.percentile(g,15)
def my20(g):
    return np.percentile(g,20)
def my25(g):
    return np.percentile(g,25)
def my30(g):
    return np.percentile(g,30)
def my35(g):
    return np.percentile(g,35)
def my40(g):
    return np.percentile(g,40)
def my45(g):
    return np.percentile(g,45)
def my50(g):
    return np.percentile(g,50)
def my55(g):
    return np.percentile(g,55)
def my60(g):
    return np.percentile(g,60)
def my65(g):
    return np.percentile(g,65)
def my70(g):
    return np.percentile(g,70)
def my75(g):
    return np.percentile(g,75)
def my80(g):
    return np.percentile(g,80)
def my85(g):
    return np.percentile(g,85)
def my90(g):
    return np.percentile(g,90)
def my95(g):
    return np.percentile(g,95)
def my99(g):
    return np.percentile(g,99)
def mycento(g):
    return np.percentile(g,100)


def get_quantile_GWR(dati):
    funcs=[my01,my05,my10,my15,my20,my25,my30,my35,my40,my45,my50,my55,my60,my65,my70,my75,my80,my85,my90,my95,my99]
    tab=pd.pivot_table(dati, 'hourly_wage', ['ANNO','RIP3'],'SESSO',funcs)
    tab.columns.names=['quantile','SESSO']
    tab=tab.stack().stack().unstack('SESSO')
    wage_rt=tab.iloc[:,1].apply(log) - tab.iloc[:,0].apply(log)
    wage_rt=wage_rt.apply(exp)
    tab2=pd.pivot_table(dati, 'hourly_wage', 'ANNO','SESSO',funcs)
    tab2.columns.names=['quantile','SESSO']
    tab2=tab2.stack().stack().unstack('SESSO')
    tot=tab2.iloc[:,1].apply(log) - tab2.iloc[:,0].apply(log)
    tot=tot.apply(exp)
    tot2=pd.DataFrame(tot)
    tot2['RIP3']=4
    tot2['ANNO']=tot2.index.get_level_values(0).values
    tot2['quantile']=tot2.index.get_level_values(1).values
    tot2.index=pd.MultiIndex.from_frame(tot2.loc[:,['ANNO','RIP3','quantile']])
    tot=tot2[0]
    return pd.concat([wage_rt,tot])
#fin=tab.unstack('RIP3').unstack('ANNO')


def Oaxaca_final():
    X,y=make_db_OB()
    db=pd.DataFrame(np.zeros([39,5]), columns=['ANNO','RIP3','GAP','EXPL','UNEXPL'])
    a=0
    for i in X.ANNO.unique():
        for t in X.RIP3.unique():
            model=OaxacaBlinder(y[(y.ANNO==i) & (y.RIP3==t)].log_hwage,X[(X.ANNO==i) & (X.RIP3==t)].drop(['ANNO','RIP3'],axis=1), bifurcate='SESSO', hasconst=False)
            print(model.two_fold().summary())
            db.loc[a,:]=[i,t, model.gap, model.explained, model.unexplained]
            a=a+1
            
    return db

def Oaxaca_final_AGE():
    X,y=make_db_OB(True)
    filtro=(X.CLETAS<10) & (X.CLETAS>0)
    X=X[filtro]
    y=y[filtro]
    db=pd.DataFrame(np.zeros([39,5]), columns=['CLETAS','RIP3','GAP','EXPL','UNEXPL'])
    a=0
    t='TOT'
    for i in X.CLETAS.unique():
        
        model=OaxacaBlinder(y[(y.CLETAS==i)].log_hwage,X[(X.CLETAS==i)].drop(['ANNO','RIP3'],axis=1), bifurcate='SESSO', hasconst=False)
        print(model.two_fold().summary())
        db.loc[a,:]=[i,t, model.gap, model.explained, model.unexplained]
        a=a+1
            
    return db
    
def load_db_fin():
    db_fin=pd.read_csv('Oaxaca_and_Blinder_res.csv')
    db_fin.index=pd.MultiIndex.from_frame(db_fin.loc[:,['ANNO','RIP3']], names=['ANNO','RIP3'])
    db_fin=db_fin.drop(['ANNO','RIP3'],axis=1)
    db_fin=db_fin.drop(['Unnamed: 0'],axis=1)
    
    gap=db_fin.GAP.unstack('RIP3')
    expl=db_fin.EXPL.unstack('RIP3')
    unexpl=db_fin.UNEXPL.unstack('RIP3')
    return 1 - gap,expl,unexpl

def diff_O_B():
    X,y=make_db_OB()
    X['intercept']=1
    Xm=X[X.SESSO==0]
    Xf=X[X.SESSO==1]
    ym=y[y.SESSO==0]
    yf=y[y.SESSO==1]
    a=0
    C_men={}
    C_women={}
    diff_tot={}
    endowment={}
    unexp_tot={}
    summary_col_tot={}
    col=['ANNO','RIP3','sector','HC','gap','unexp_gap','end_gap','tot_end','tot_unexp']
    db=pd.DataFrame(np.zeros([39,9]),columns=col)
    for i in X.ANNO.unique():
        for t in X.RIP3.unique():
            men=sm.OLS(ym[(ym.RIP3==t) & (ym.ANNO==i)].log_hwage,Xm[(Xm.RIP3==t) & (Xm.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1)).fit()
            women=sm.OLS(yf[(yf.RIP3==t) & (yf.ANNO==i)].log_hwage,Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1)).fit()
            coef_men=men.params
            coef_women=women.params
            diff=Xm[(Xm.RIP3==t) & (Xm.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()-Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()
            end=coef_men*diff
            sector=end.sum() - end.loc[['CLETAS','DURATT','ED_2','ED_3']].sum()
            HC=end.sum()-sector
            unexp=Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()*(coef_men - coef_women)
            gap=unexp.sum() + end.sum()         
            
            db.loc[a,:]=[i,t,sector,HC,gap,unexp.sum()/gap, end.sum()/gap, end.sum(),unexp.sum()]                                              
            
            
            C_men[f'{i}_{t}']=coef_men
            C_women[f'{i}_{t}']=coef_women
            diff_tot[f'{i}_{t}']=diff
            endowment[f'{i}_{t}']=end
            unexp_tot[f'{i}_{t}']=unexp
            summary_col_tot[f'{i}_{t}']=summary_col(men,stars=True)
            
            a=a+1
            print(f'anno: {i} zona: {t} GAP:{gap}')
            
    db.index=pd.MultiIndex.from_frame(db.loc[:,['ANNO','RIP3']])
    db=db.drop(['ANNO','RIP3'],axis=1)
    db=db.sort_index()
    C_men=get_mean(pd.DataFrame(C_men).T, db.gap)
    C_women=get_mean(pd.DataFrame(C_women).T, db.gap)
    diff_tot=get_mean(pd.DataFrame(diff_tot).T, db.gap)
    endowment=get_mean(pd.DataFrame(endowment).T, db.gap)
    unexp_tot=get_mean(pd.DataFrame(unexp_tot).T, db.gap)
    db['GWR']=1-db.gap
    return db, C_men,C_women,diff_tot,endowment,unexp_tot, summary_col_tot
    

def reindex(data):
    lista=[]
    for i in data.index.values:
        lista.append(i.split('_'))
    lista=np.array(lista)
    data.index=pd.MultiIndex.from_arrays(np.array(lista).T)
    data.index.names=['ANNO','RIP3']
    
    
    return data.sort_index()

def get_mean(data,series):
    data=reindex(data)
    #data=data.div(series.values,axis=0)
    data=data.unstack('RIP3').mean().unstack('RIP3')
    
    data.loc['SECTOR_TOT',:]=data.loc[['PRIVPUBL', 'PUBL_10', 'PUBL_11', 'PRIV_2', 'PRIV_3', 'PRIV_4','PRIV_5', 'PRIV_6', 'PRIV_7', 'PRIV_8', 'PRIV_9'],:].sum()
    data.loc['PROF_TOT',:]=data.loc['PROF3_111':'PROF3_931',:].sum()
    #data.loc['PROF_TOT',:]=data.loc[[ 'PROF2_11','PROF2_12', 'PROF2_13', 'PROF2_21', 'PROF2_22', 'PROF2_23', 'PROF2_24','PROF2_25', 'PROF2_26', 'PROF2_31', 'PROF2_32', 'PROF2_33', 'PROF2_34','PROF2_41', 'PROF2_42', 'PROF2_43', 'PROF2_44', 'PROF2_51', 'PROF2_52','PROF2_53', 'PROF2_54', 'PROF2_55', 'PROF2_61', 'PROF2_62', 'PROF2_63','PROF2_65', 'PROF2_66', 'PROF2_71', 'PROF2_72', 'PROF2_73', 'PROF2_74','PROF2_81', 'PROF2_82', 'PROF2_83', 'PROF2_84', 'PROF2_85', 'PROF2_86','PROF2_90', 'PROF2_91', 'PROF2_92', 'PROF2_93'],:].sum()
    data.loc['POSITION',:]=data.loc[['POSPRO_1', 'POSPRO_2', 'POSPRO_3','POSPRO_5'],:].sum()
    data.loc['EDUCATION',:]=data.loc[['ED_2','ED_3'],:].sum()
    data.loc['AGE_DURATT',:]=data.loc[['CLETAS','DURATT'],:].sum()
    return data



def three_fold_O_B():
    X,y=make_db_OB(False,True)
    X['intercept']=1
    Xm=X[X.SESSO==0]
    Xf=X[X.SESSO==1]
    ym=y[y.SESSO==0]
    yf=y[y.SESSO==1]
    a=0
    C_men={}
    C_women={}
    diff_tot={}
    endowment={}
    unexp_men_tot={}
    unexp_women_tot={}
    summary_col_tot={}
    col=['ANNO','RIP3','sector','HC','gap','unexp_men_gap','unexp_women_gap','end_gap','tot_end','tot_unexp_men','tot_unexp_women']
    db=pd.DataFrame(np.zeros([39,11]),columns=col)
    for i in X.ANNO.unique():
        for t in X.RIP3.unique():
            men=sm.OLS(ym[(ym.RIP3==t) & (ym.ANNO==i)].log_hwage,Xm[(Xm.RIP3==t) & (Xm.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1)).fit()
            women=sm.OLS(yf[(yf.RIP3==t) & (yf.ANNO==i)].log_hwage,Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1)).fit()
            tot=sm.OLS(y[(y.RIP3==t) & (y.ANNO==i)].log_hwage,X[(X.RIP3==t) & (X.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1)).fit()
            coef_men=men.params
            coef_women=women.params
            coef_tot=tot.params
            diff=Xm[(Xm.RIP3==t) & (Xm.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()-Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()
            end=coef_tot*diff
            sector=end.sum() - end.loc[['CLETAS','DURATT','ED_2','ED_3']].sum()
            HC=end.sum()-sector
            #unexp=Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()*(coef_men - coef_women)
            unexp_men=Xm[(Xm.RIP3==t) & (Xm.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()*(coef_men - coef_tot)
            unexp_women=Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()*(coef_tot - coef_women)
            
            
            gap=end.sum() + unexp_men.sum() + unexp_women.sum()        
            
            db.loc[a,:]=[i,t,sector,HC,gap,unexp_men.sum()/gap,unexp_women.sum()/gap, end.sum()/gap, end.sum(),unexp_men.sum(),unexp_women.sum()]                                              
            
            
            C_men[f'{i}_{t}']=coef_men
            C_women[f'{i}_{t}']=coef_women
            diff_tot[f'{i}_{t}']=diff
            endowment[f'{i}_{t}']=end
            unexp_men_tot[f'{i}_{t}']=unexp_men
            unexp_women_tot[f'{i}_{t}']=unexp_women
            summary_col_tot[f'{i}_{t}']=summary_col(tot,stars=True)
            
            a=a+1
            print(f'anno: {i} zona: {t} GAP:{gap}')
            
    db.index=pd.MultiIndex.from_frame(db.loc[:,['ANNO','RIP3']])
    db=db.drop(['ANNO','RIP3'],axis=1)
    db=db.sort_index()
    C_men=get_mean(pd.DataFrame(C_men).T, db.gap)
    C_women=get_mean(pd.DataFrame(C_women).T, db.gap)
    diff_tot=get_mean(pd.DataFrame(diff_tot).T, db.gap)
    endowment=get_mean(pd.DataFrame(endowment).T, db.gap)
    unexp_women_tot=get_mean(pd.DataFrame(unexp_women_tot).T, db.gap)
    unexp_men_tot=get_mean(pd.DataFrame(unexp_men_tot).T, db.gap)
    db['GWR']=1-db.gap
    return db, C_men,C_women,diff_tot,endowment,unexp_men_tot, unexp_women_tot, summary_col_tot
    

def three_fold_O_B_AGE():
    X,y=make_db_OB(CLETAS=True)
    filtro=(X.CLETAS<10) & (X.CLETAS>0)
    X=X[filtro]
    y=y[filtro]
    X['intercept']=1
    Xm=X[X.SESSO==0]
    Xf=X[X.SESSO==1]
    ym=y[y.SESSO==0]
    yf=y[y.SESSO==1]
    a=0
    C_men={}
    C_women={}
    diff_tot={}
    endowment={}
    unexp_men_tot={}
    unexp_women_tot={}
    summary_col_tot={}
    col=['CLETAS','RIP3','sector','HC','gap','unexp_men_gap','unexp_women_gap','end_gap','tot_end','tot_unexp_men','tot_unexp_women']
    db=pd.DataFrame(np.zeros([27,11]),columns=col)
    for i in X.CLETAS.unique():
        for t in X.RIP3.unique():
            men=sm.OLS(ym[(ym.RIP3==t) & (ym.CLETAS==i)].log_hwage,Xm[(Xm.RIP3==t) & (Xm.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1)).fit()
            women=sm.OLS(yf[(yf.RIP3==t) & (yf.CLETAS==i)].log_hwage,Xf[(Xf.RIP3==t) & (Xf.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1)).fit()
            tot=sm.OLS(y[(y.RIP3==t) & (y.CLETAS==i)].log_hwage,X[(X.RIP3==t) & (X.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1)).fit()
            coef_men=men.params
            coef_women=women.params
            coef_tot=tot.params
            diff=Xm[(Xm.RIP3==t) & (Xm.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1).mean()-Xf[(Xf.RIP3==t) & (Xf.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1).mean()
            end=coef_tot*diff
            sector=end.sum() - end.loc[['DURATT','ED_2','ED_3']].sum()
            HC=end.sum()-sector
            #unexp=Xf[(Xf.RIP3==t) & (Xf.ANNO==i)].drop(['ANNO','SESSO','RIP3'],axis=1).mean()*(coef_men - coef_women)
            unexp_men=Xm[(Xm.RIP3==t) & (Xm.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1).mean()*(coef_men - coef_tot)
            unexp_women=Xf[(Xf.RIP3==t) & (Xf.CLETAS==i)].drop(['CLETAS','SESSO','RIP3'],axis=1).mean()*(coef_tot - coef_women)
            
            
            gap=end.sum() + unexp_men.sum() + unexp_women.sum()        
            
            db.loc[a,:]=[i,t,sector,HC,gap,unexp_men.sum()/gap,unexp_women.sum()/gap, end.sum()/gap, end.sum(),unexp_men.sum(),unexp_women.sum()]                                              
            
            
            C_men[f'{i}_{t}']=coef_men
            C_women[f'{i}_{t}']=coef_women
            diff_tot[f'{i}_{t}']=diff
            endowment[f'{i}_{t}']=end
            unexp_men_tot[f'{i}_{t}']=unexp_men
            unexp_women_tot[f'{i}_{t}']=unexp_women
            summary_col_tot[f'{i}_{t}']=summary_col(tot,stars=True)
            
            a=a+1
            print(f'age: {i} zona: {t} GAP:{gap}')
            
    db.index=pd.MultiIndex.from_frame(db.loc[:,['CLETAS','RIP3']])
    db=db.drop(['CLETAS','RIP3'],axis=1)
    db=db.sort_index()
    C_men=get_mean_AGE(pd.DataFrame(C_men).T, db.gap)
    C_women=get_mean_AGE(pd.DataFrame(C_women).T, db.gap)
    diff_tot=get_mean_AGE(pd.DataFrame(diff_tot).T, db.gap)
    endowment=get_mean_AGE(pd.DataFrame(endowment).T, db.gap)
    unexp_women_tot=get_mean_AGE(pd.DataFrame(unexp_women_tot).T, db.gap)
    unexp_men_tot=get_mean_AGE(pd.DataFrame(unexp_men_tot).T, db.gap)
    db['GWR']=1-db.gap
    return db, C_men,C_women,diff_tot,endowment,unexp_men_tot, unexp_women_tot, summary_col_tot
  
def reindex_AGE(data):
    lista=[]
    for i in data.index.values:
        lista.append(i.split('_'))
    lista=np.array(lista)
    data.index=pd.MultiIndex.from_arrays(np.array(lista).T)
    data.index.names=['CLETAS','RIP3']
    return data.sort_index()

def get_mean_AGE(data,series):
    data=reindex_AGE(data)
    #data=data.div(series.values,axis=0)
    data.columns.name='VALUE'
    data=data.T
    
    data.loc['SECTOR_TOT',:]=data.loc[['PRIVPUBL', 'PUBL_10', 'PUBL_11', 'PRIV_2', 'PRIV_3', 'PRIV_4','PRIV_5', 'PRIV_6', 'PRIV_7', 'PRIV_8', 'PRIV_9'],:].sum()
    data.loc['PROF_TOT',:]=data.loc['PROF3_111':'PROF3_931',:].sum()
    #data.loc['PROF_TOT',:]=data.loc[[ 'PROF2_11','PROF2_12', 'PROF2_13', 'PROF2_21', 'PROF2_22', 'PROF2_23', 'PROF2_24','PROF2_25', 'PROF2_26', 'PROF2_31', 'PROF2_32', 'PROF2_33', 'PROF2_34','PROF2_41', 'PROF2_42', 'PROF2_43', 'PROF2_44', 'PROF2_51', 'PROF2_52','PROF2_53', 'PROF2_54', 'PROF2_55', 'PROF2_61', 'PROF2_62', 'PROF2_63','PROF2_65', 'PROF2_66', 'PROF2_71', 'PROF2_72', 'PROF2_73', 'PROF2_74','PROF2_81', 'PROF2_82', 'PROF2_83', 'PROF2_84', 'PROF2_85', 'PROF2_64','PROF2_90', 'PROF2_91', 'PROF2_92', 'PROF2_93'],:].sum()
    data.loc['POSITION',:]=data.loc[['POSPRO_1', 'POSPRO_2', 'POSPRO_3','POSPRO_5'],:].sum()
    data.loc['EDUCATION',:]=data.loc[['ED_2','ED_3'],:].sum()
    
    data.stack('CLETAS').unstack('CLETAS')
    return data