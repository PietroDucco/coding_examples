import pandas as pd
from pathlib import Path
import selenium
import time
import random
import re
from selenium.common.exceptions import TimeoutException
import os
import winsound
import numpy as np

url=url to access orbis from Bocconi

bocconi={'nome':username, 'psw':psw} #censored
orbis={'nome':username, 'psw':psw} #censored

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def LoginBocconi(driver,bocconi):
    xpath_id='//*[@id="extpatid"]'
    xpath_psw='//*[@id="extpatpw"]'
    
    driver.find_element_by_xpath(xpath_id).send_keys(bocconi['nome'])
    driver.find_element_by_xpath(xpath_psw).send_keys(bocconi['psw'])
    
    #clicca pulsante
    driver.find_element_by_xpath('//*[@id="fm1"]/div[6]/a/div').click()
    
    print('loggato')
#go to the next page, click on th ebutton
pass

#def login VdB
def LoginOrbis(driver,orbis):
    
    #while driver.title!=
    assert driver.title =='Orbis Intellectual Property | | BvD'
    
    driver.find_element_by_xpath('//*[@id="user"]').send_keys(orbis['nome'])
    driver.find_element_by_xpath('//*[@id="pw"]').send_keys(orbis['psw'])
    
    driver.find_element_by_xpath('//*[@id="loginPage"]/div[2]/div[3]/button').click()
    
    #wait till assert not true
    
    driver.find_element_by_xpath('//*[@id="LoginForm"]/div/div[2]/input').click()
    
    print('loggato in Orbis')
    
    
def wait_find(driver,xpath,time=10,click=False,xpath2=''):
    if xpath2=='':
        xpath2=xpath
    
    el=WebDriverWait(driver,time).until(lambda d: d.find_element_by_xpath(xpath2))
    if click:
        driver.find_element_by_xpath(xpath).click()
    else:
        return driver.find_element_by_xpath(xpath)
        
    
def Company_id_Search(driver,nome):
    url='https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search/By/CompanyName'
    driver.get(url)
    #write name
    driver.find_element_by_xpath('//*[@id="main-content"]/div/div[2]/div[1]/div[1]/div/input').send_keys(nome)
    
    # dynamic loading
    
    el=wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[2]/ul/li/div[1]/span[3]',100,False)
    
    if 'No results' not in el.text: 
    # no result xpath '//*[@id="main-content"]/div/div[2]/div[2]/ul/li/div[1]/span[3]/text()'
    #wait for the 'X' button to be loaded, then it is possible to continue (deleting the search or saving it)
    
        wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[2]/ul/li/div[2]/div[1]/span[1]/a[1]',100,True,'//*[@id="main-content"]/div/div[2]/div[2]/ul/li/div[1]/span[1]/span')
    #loading, wait for the button to be blue
        time.sleep((8+ abs(random.random())))
    #dynamic loading, time.sleep
        wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[3]/div/a[2]',10,True)
    
        print('search fatta')
        return True
    else:
        print('NO RESULTS')
        return False

def Filter_world(driver):
    #go to the filter page
    driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search/By/CountryRegion')
    
    #click on Geography filtering
    wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div[1]/div/div[3]/div/ul/li[1]/div/span',5,True)
    
    time.sleep(2)
    #click on north america
    wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[1]/div/div/div[1]/div/div[3]/div/ul/li[1]/ul/li[1]/div/span[2]',10,True)
    #dynamic loading, click on the ok button when finally become blue
    time.sleep(20)
    wait_find(driver,'//*[@id="main-content"]/div/div[1]/div[2]/div/a[2]',10,True)
    
    #time.sleep(5)
    
    
    
    
def Company_save_search(driver,nome):
    #check if there are filtered companies
    el1=wait_find(driver, '//*[@id="summaryCompanyCount"]')
    #filtered companies need to be more than 0
    if el1.text=='0 company':
        return False
    #click on if not False
    driver.find_element_by_xpath('//*[@id="search-summary"]/div/div/div[3]/a/img').click()
    #wait for the charging of the table    
    el=WebDriverWait(driver,20).until(lambda d: d.find_element_by_xpath('//*[@id="resultsTable"]/tbody/tr/td[1]/div/table/tbody/tr[1]/td[4]/span/a'))
    #once charged click on Export
    driver.find_element_by_xpath('/html/body/section[4]/div[1]/div[2]/div[2]/div[1]/ul/li[2]/a').click()
    #wait for the window to appear
    el=WebDriverWait(driver,30).until(lambda d: d.find_element_by_xpath('//*[@id="component_FileName"]'))
    
    #write name for the export file
    driver.find_element_by_xpath('//*[@id="component_FileName"]').send_keys(nome)
    
    
    #click on the export button
    driver.find_element_by_xpath('//*[@id="exportDialogForm"]/div[2]/a[2]').click()
    #wait for the window that shows the download to come and then clikc on the 'X'
    wait_find(driver, '/html/body/section[4]/div[6]/div[1]/img',40,True)
    
    print('export fatto')
    
    #back to search
    
    driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search')
    return True
    
    
def Clean_Search(driver,level=1):
    '''
    driver is the browser obj, level indicate the first search term, usually the filter
    or the second, usually the search term, in the cycle is used as the 2.
    '''
    if level==1:
        driver.find_element_by_xpath('//*[@id="search-summary"]/div/table/tbody/tr/td[2]/img').click()
    else:
        wait_find(driver, '//*[@id="search-summary"]/div/table/tbody/tr[2]/td[2]/img', 10,True)
    time.sleep(2)
    try:    
        wait_find(driver,'/html/body/section[3]/div[6]/div[3]/a[2]',30,True)
    except TimeoutError:
        driver.refresh()
        wait_find(driver, '//*[@id="search-summary"]/div/table/tbody/tr[2]/td[2]/img', 10,True)
        time.sleep(2)
        wait_find(driver,'/html/body/section[3]/div[6]/div[3]/a[2]',30,True)
    print('cancellato')
    

    
def Logout_orbis(driver):
    '''
    

    Parameters
    ----------
    driver : webdriver obj.

    Returns
    -------
    None.

    '''
    
    #click on the top right side of the page
    driver.find_element_by_xpath('/html/body/section[1]/ul/li[2]/img[2]').click()
    #wait window to come
    time.sleep(3)
    #click Logout
    wait_find(driver,'//*[@id="header-user-menu"]/section[1]/div[1]/div[2]/a',10,True)
    
def close(driver):
    driver.quit()
    
    
    
def company_cycle_ID(driver,nome, nome2,level):
    '''
    nome, is the search term es: "IBM"
    nome2: is the name we add in the export file
    level indicate the one that we need to delete
    '''
    if level==1:
        Filter_world(driver)
        time.sleep(5)
    time.sleep(1)
    a=Company_id_Search(driver, nome)
    time.sleep(5)
    
    if a:
        
        
        b=Company_save_search(driver, nome2)
        time.sleep(5)
        Clean_Search(driver,2) #troppo rischioso pulire entrambi 2 volte
    #Clean_Search(driver)
        time.sleep(3)
        if b:
            print(f'{nome}, fatto')
            return True
        else:
            print(f'{nome}, VUOTO, NO IN NA')
            return False
    else:
        print(f'{nome}, vuoto')
        return False


def transform_csv_excel(starting_url, end_url): #controlla se NAME2 ha sempre lo spazio alla fine, toglilo
    '''
    it is a first filtering of the document, create the search term columns "NAME2"
    Save starting_url (csv file) as an excel file in end_url
    excel file because they are easier to be modified, usually some search term in NAME2 need to be corrected
    '''

    columns=['NEW_ID','COMPANY','TOWN','STATE_CORRECTED','FOUNDED_YEAR','YEAR']
    
    file=pd.read_csv(starting_url, engine='python')
    file=file.drop('Unnamed: 0',axis=1)
    file.columns=columns
    file['COMPANY']=file.COMPANY.astype(str) + ' '
    file['DIVISION']=file.COMPANY.str.extract(r'(_[\S ]*)')
    file['NAME']=file.COMPANY.str.extract(r'([^_]*)_')
    file.loc[file['NAME'].isna(),'NAME']=file[file['NAME'].isna()].COMPANY
    file['INC']=file.COMPANY.str.contains(r'[^a-zA-Z]+(INC)[^a-zA-Z]+',flags=re.IGNORECASE, regex=True)
    file['CORP']=file.COMPANY.str.contains(r'[^a-zA-Z]+(CORP)[^a-zA-Z]+',flags=re.IGNORECASE, regex=True)
    
    file['SEE']=file.COMPANY.str.extract(r'[\S ]*SEE: ([\S ]*)')
    file.loc[file.SEE.notna(),'NAME']= file[file.SEE.notna()].COMPANY.str.extract(r'([\S ]*)SEE:').iloc[:,0]
    
    file['FORMERLY']=file.COMPANY.str.extract(r'[\S ]*FORMERLY ([a-zA-Z ]*)')
    file.loc[file.FORMERLY.notna(),'NAME']=file[file.FORMERLY.notna()].COMPANY.str.extract(r'([a-zA-Z,._ ]*)[^a-zA-Z]*FORMERLY ').iloc[:,0]
    
    file['BACK']=file.SEE
    file.loc[file.SEE.isna(),'BACK']=file.loc[file.SEE.isna(),'FORMERLY']
    
    file['NAME2']=file.NAME.str.replace(',','')
    file.loc[file.INC==True,'NAME2']=file[file.INC==True].NAME2.str.replace('INC','')
    #file.loc[file.INC==True,'NAME2']=file[file.INC==True].NAME2.str.replace('INC.','')
    file.loc[file.CORP==True,'NAME2']=file.loc[file.CORP==True,'NAME2'].str.replace(' CORP','')
    file['NAME2']=file.NAME2.str.replace('-',' ')
    file['NAME2']=file.NAME2.str.replace('_','')
    file['NAME2']=file.NAME2.str.replace('/',' ')
    file['NAME2']=file.NAME2.str.replace(':','')
    file['NAME2']=file.NAME2.str.replace('.','')
    file['NAME2']=file.NAME2.str.replace("'",' ')
    file['NAME2']=file.NAME2.str.replace('CORPORATION','')
    file['NAME2']=file.NAME2.str.replace('DIVISION','')
    file['NAME2']=file.NAME2.str.replace('INCORPORATED','')
    file['NAME2']=file.NAME2.str.replace('LTD','')
    file['NAME2']=file.NAME2.str.strip()
    
    file['FATTO']=''
    col=['NEW_ID','COMPANY','NAME2','TOWN','STATE_CORRECTED','FOUNDED_YEAR','YEAR','FATTO']
    #return file.loc[:,col]
    file=file.sort_values('COMPANY')
    file.loc[:,col].to_excel(end_url)

def get_DONE(url,file):
    '''
    

    Parameters
    ----------
    url : Directory where all the exports are.
    file : file from which we extracted the exports, NAME2
        

    Returns
    -------
    None, but modifiy the FATTO (DONE) column in the file to understand which search sorted results and which not.

    '''
    
    a=os.listdir(url)
    a.remove('fatto')
    a=pd.DataFrame(a)
    a.columns=['res']
    a['extracted']=a.res.str.extract(r'_\d+_([a-zA-Z \S]+).xlsx')
    df=pd.read_excel(file)
    
    df['FATTO']=[ c in a['extracted'].values for c in df.NAME2.values]
    df.drop('Unnamed: 0',axis=1)
    df.to_excel(file)
    


def sub_routine(file,num=0):  #fare in modo di non fare due volte la stessa cosa
    
    '''
    
    Parameters
    ----------
    file : is the excel file from which we extract, from the NAME2 column, the search terms
    
    num : indicate the index number from which we want to start, usually, the subroutine crash after 20~120 cycles and the number at which we get is plotted on the console.   
    
    Returns
    -------
    None, create exports in Orbis, emit sound in most of crash cases
    
    '''

    driver=Chrome()
    driver.get(url)
    
    LoginBocconi(driver,bocconi)
    
    LoginOrbis(driver,orbis)
    
    file=pd.read_excel(file,sheet_name='Sheet1')
    file=file.drop('Unnamed: 0',axis=1)
    nm1=file.iloc[num,:].NAME2
    
    company_cycle_ID(driver, nm1, f'{num}_{nm1}',1)
    print(f'fatto: {num} {nm1}\n')
    
    c=0
    nm2=''
    try:  
        for i in range(num+1,file.shape[0]):
            nm=file.iloc[i,:].NAME2
            if i!=0:
                nm2=file.iloc[i-1,:].NAME2
            if nm==nm2:
                continue
            try:
                a=company_cycle_ID(driver, nm,f'{i}_{nm}',2)
                #file.iloc[i,-1]=a
                print(f'fatto: {i} {nm}\n')
            except TimeoutException: 
                file.to_excel('1980 2.xlsx')
                winsound.Beep(400,2000)
                c=1
                driver.refresh()
                Logout_orbis(driver)
                driver.quit()
    finally:
        if c==0:
            file.to_excel('1980 2.xlsx')
            winsound.Beep(400,2000)
            c=1
            driver.refresh()
            Logout_orbis(driver)
            driver.quit()
        
    if c==0:
        winsound.Beep(400,2000)
        file.to_excel('1981 2.xlsx')
        driver.refresh()
        Logout_orbis(driver)
        driver.quit()
        
    


def filter_companies(start_url, end_url):
    '''
    

    Parameters
    ----------
    start_url : starting url, load.
    end_url : ending url, save.

    Returns
    -------
    None, Create a file in the end_url with all the companies with a BvD ID number from start_url (companies export from orbis)
    If there is not a single one BvD ID number in the start_url then nothing is created

    '''
    
    file=pd.read_excel(f'{start_url}','Results')
    x=file[file['BvD ID number'].notna()]
    if x.size>0:
        x=x.sort_values('Region in country',axis=0)
        x.to_excel(f'{end_url}')
    print('fatto')



def filter_all(direc):
    
    '''
    
    Parameters
    ----------
    
    direc: directory, do filter_companies for all the 
    export in a directory, the directory must contains exports only.
    
    '''
    
    lista=os.listdir(Path.home()/f'{direc}')
    if 'fatto' in lista:
        lista.remove('fatto')
    for i in lista:
        filter_companies(Path.home()/f'{direc}/{i}',Path.home()/f'{direc}/FILTER_{i}' )
    print('finito')



def NORESULT(file):
    '''
    

    Parameters
    ----------
    file : file with NAME2 columns.

    Returns
    -------
    df : pandas database with the unsearched companies, FATTO==FALSE.

    '''
    
    df=pd.read_excel(file)
    df=df[df.FATTO==0]
    return df

#to save file
#df.to_excel(url)



def databrutto(url):
    #used once with 1977 part2.csv file, unreadable with pandas
    
    
    file=pd.read_csv(url,engine='python')
    x=pd.DataFrame(file.iloc[:,0].str.split(','))
    colonna=x.columns
    x['new.id']=[i[1].replace('"','') for i in x.iloc[:,0]]
    x['Company']=[i[2].replace('"','') for i in x.iloc[:,0]]
    x['Town']=[i[3].replace('"','') for i in x.iloc[:,0]]
    x['state.corrected']= [i[4].replace('"','') for i in x.iloc[:,0]]
    x['founded']= [i[5].replace('"','') for i in x.iloc[:,0]]
    x['year']= [i[6].replace('"','') for i in x.iloc[:,0]]
    x.replace('NA','')
    return x.drop(colonna,axis=1)
    

def search_patents(driver,code):
    driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search/By/HydraBvDId')
    #write patents term
    wait_find(driver, '//*[@id="freetext"]')
    driver.find_element_by_xpath('//*[@id="freetext"]').send_keys(code)
    
    #search it
    wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[1]/div/div[1]/div[1]/div/p/a', 20,click=True)
    
    #check it
    wait_find(driver,'//*[@id="main-content"]/div/div[2]/div[1]/div/div[1]/div[2]/div/div/ul/li/div',10)
    
    time.sleep(2)
    #wait for dynamic loading
    wait_find(driver,'//*[@id="main-content"]/div/div[1]/div[1]/div/ul/li[1]/span/span[1]',100,False)
    time.sleep(4)
    #click OK button
    wait_find(driver,'//*[@id="main-content"]/div/div[1]/div[2]/div/a[2]',20,True)
    
    time.sleep(1)
    print('patent cercata')

def export(driver,name):
   #export patents
    
    wait_find(driver,'//*[@id="component_FileName"]',20,False)
    driver.find_element_by_xpath('//*[@id="component_FileName"]').send_keys(name)
    
    wait_find(driver,'//*[@id="exportDialogForm"]/div[2]/a[2]',20,True)
    time.sleep(0.5)
    wait_find(driver, '/html/body/section[4]/div[6]/div[1]/img',40,True)


def export_patents(driver,name):
    #export patents revised
    patents=wait_find(driver,'//*[@id="search-summary"]/div/div/div[2]/a/span').text
    patents=patents.split(' ')[0]
    patents=int(patents.replace(',',''))
    if patents==0:
        driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search')
    
        return False
    
    
    
    driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/List')
    #loading
    wait_find(driver,'//*[@id="resultsTable"]/tbody/tr/td[1]/div/table/tbody/tr[1]/td[3]',100,False)
    
    
    #get number of patents and act as a consequence
    a=0
    if patents>80000:
        a=patents/80000
        if a>int(a):
            a=int(a+1)
        else:
            a=int(a)
        _,bins=pd.cut(np.arange(patents+1),a,retbins=True)
        for i in range(a):
            minimo=int(bins[i])
            if i==0:
                minimo=1
            massimo=int(bins[i+1])
            if i==a-1:
                massimo=patents
            #open export window
            wait_find(driver,'/html/body/section[4]/div[1]/div[2]/div[2]/div[1]/ul/li[3]/a/img',10,True)   
            
            #set the range
            wait_find(driver,'//*[@id="component_RangeOptionSelectedId"]/option[4]',10,True)
            
            #set the minimunm
            driver.find_element_by_xpath('//*[@id="export-component-range"]/fieldset/input[1]').send_keys(minimo)
            #set the maximum
            
            driver.find_element_by_xpath('//*[@id="export-component-range"]/fieldset/input[2]').send_keys(massimo)
                                  
            
            export(driver,f'{name}_{i}')
        
    #click export
    else:
        wait_find(driver,'/html/body/section[4]/div[1]/div[2]/div[2]/div[1]/ul/li[3]/a/img',10,True)
        export(driver,name)
    
    time.sleep(1)
    print('export fatto')
    
    #back to search
    
    driver.get('https://0-orbisintellectualproperty-bvdinfo-com.lib.unibocconi.it/version-2021624/orbispatents/1/Patents/Search')
    return True
    
def Cicle_pat(driver,code,name):
    '''
    

    Parameters
    ----------
    driver : webdriver obj.
    code : patents code.
    name : name of the export.

    Returns
    -------
    None.

    '''
    search_patents(driver, code)
    a=export_patents(driver,name)
    Clean_Search(driver,1)

def sub_patent(file,num=0):
    '''
    

    Parameters
    ----------
    file : File with NAME2 and BvD ID number columns.
    num : index to start at.

    Returns
    -------
    None, Create patents export in Orbis IP

    '''
    driver=Chrome()
    driver.get(url)
    
    LoginBocconi(driver,bocconi)
    
    LoginOrbis(driver,orbis)
    
    file=pd.read_excel(file,sheet_name='Sheet1')
    file=file.drop('Unnamed: 0',axis=1)
    file=file[file['BvD ID number'].notna()].loc[:,['NAME2','BvD ID number']]
    c=0
    
    try:
        for i in range(num,file.shape[0]):
            if i>0 and (file.iloc[i,1]==file.iloc[(i-1),1]):
                continue
            
            time.sleep(0.5)
            Cicle_pat(driver,file.iloc[i,1],f'{i}_{file.iloc[i,0]}')
            print(f'fatto:{file.iloc[i,0]} {i}\n')

    except TimeoutException: 
        
        winsound.Beep(400,2000)
        c=1
        driver.refresh()
        Logout_orbis(driver)
        driver.quit()
    finally:
        if c==0:
            
            winsound.Beep(400,2000)
            c=1
            driver.refresh()
            Logout_orbis(driver)
            driver.quit()
        
    if c==0:
        winsound.Beep(400,2000)
        
        driver.refresh()
        Logout_orbis(driver)
        driver.quit()
            
    
def avvia_orbis():
    '''
    

    Returns
    -------
    driver : webdriver obj loaded in the Orbis IP.

    '''
    
    driver=Chrome()
    driver.get(url)
    LoginBocconi(driver,bocconi)
    LoginOrbis(driver,orbis)
    return driver  
    

def create_final(link,url,name):
    '''
    

    Parameters
    ----------
    link : directory with patents exports file only.
    url : file with NAME2 columns and BvD ID number from which we extract and join var.
    name : end_url, where we save the final big file with all patents jointed to company infos.

    Returns
    -------
    None.

    '''
    b=os.listdir(Path.home()/f'Downloads/{link}')
    tutto=pd.read_excel(Path.home()/f'Downloads/{link}/{b[0]}','Results')
    tutto=join_results(url,tutto)
    a=pd.read_excel(url)
    a=a[a['BvD ID number'].notna()].drop(['Unnamed: 0','FATTO','NAME2'],axis=1)
    colonne=a.columns.values
    #return tutto
    
    tutto[colonne]=tutto[colonne].fillna(method='ffill').fillna(method='bfill')
    
    for i in b[1:]:
        c=pd.read_excel(Path.home()/f'Downloads/{link}/{i}','Results')
        c=join_results(url,c)
        tutto=pd.concat([tutto,c])
        print(f'fatto {i}')
    
    
    tutto.drop('Unnamed: 0',axis=1).to_csv(f'{name}.csv')
    winsound.Beep(400,2000)


def join_results(url,tutto):
    #used to achieve the method above
    
    tutto2=tutto.copy()
    tutto2.columns.values[3]='BvD ID number'
    #tutto=tutto[tutto['BvD ID number'].notna()]
    a=pd.read_excel(url)
    a=a[a['BvD ID number'].notna()].drop(['Unnamed: 0','FATTO','NAME2'],axis=1)
    colonne=a.columns.values
    x=pd.merge(tutto2,a, 'left','BvD ID number')
    x[colonne]=x[colonne].fillna(method='ffill').fillna(method='bfill')
    return x
    #t
    
    
    
  
    
    #df.to_excel('pirirpir')
    
    
    #df.to_excel('1980NORESULTS.xlsx')

#THE END
