import time
import random
import re, openpyxl
import requests
import bs4, lxml, pprint

from pathlib import Path


'''questo file si propone di costruire diversi metodi in grado di raccogliere e-mail da
TripAdvisor
-input tripadvisor + bar/ristoranti/caffe + città fare una ricerca su google cazzo e aprire il primo link return link fatto.
-ottenere una lista degli url di tutti i ristoranti in una pagina di tripadvisor, bs4 fatto!
-aprire gli url e ottenere le e-mail, input (lista url), request e bs4
-input link inziale pagina cambiare pagina, prendere l'url e compiere le operazioni di sopra per tutte le pagine
e per tutte le città return link di ogni pagina di quei bar ristoranti in quellà città #
-scrivere tutte le e-mail, nome, numero di cellulare, città, in una tabella di excel
-mandare automaticamente le n k mail con inclusa lo script html dentro funzionante e se possibile un nome del ristorante, nello script 
 '''
#listatipo=['bar&pubs', 'coffee&Tea', 'ristoranti']
#listacittà=['milano', 'torino', 'roma', 'bologna', 'brescia', 'biella', 'bergamo', 'firenze', 'padova', 'verona', 'varese', 'monza', 'vicenza', 'venezia', 'genova', 'bari', 'napoli', 'salerno', 'perugia', 'messina', 'foggia' ,'como', 'cuneo', 'pavia', 'trento', 'reggiocalabria', ' bolzano', 'reggioemilia', 'udine', 'trieste', 'sassari', 'rimini', 'cagliari', 'vercelli', 'asti', 'mantova', 'alessandria', 'novara', 'verbania', 'parma', 'cremona', 'piacenza', 'ferrara', 'treviso', 'ravenna', 'cesena']
#listadef=['catania', 'caserta', 'lecce', 'modena', 'cosenza', 'taranto', 'bolzano', 'frosinone', 'ancona', 'agrigento', 'trapani', 'pisa', 'avellino', 'siracusa', 'lucca', 'brindisi', 'trani', 'chieti', 'potenza', 'catanzaro', 'pesaro', 'urbino', 'arezzo', 'ragusa', 'livorno', 'pescara', 'viterbo', 'pordenone', 'teramo', 'macerata', "l'aquila", 'pistoia', 'savona', 'benevento', 'prato', 'lodi', 'terni', 'grosseto', 'la spezia', 'imperia', 'nuoro', 'sondrio', 'oristano', 'rieti', 'gorizia', 'aosta', 'campobasso', 'isernia', 'carpi', 'imola', 'lamezia terme', 'massa', 'carrara', 'vigevano', 'matera', 'legnano', 'olbia']
def tripAdLink(nomecittà, tipo):
# input = nome città, return url della città su ristorazione o altri tipi
    res = requests.get(f'https://www.google.it/search?q={nomecittà}+{tipo}+tripadvisor')
    
    linkSoup = bs4.BeautifulSoup(res.content, 'lxml')
    scavo= linkSoup.find_all('a')
    
    for i in scavo:
        
        if "https://www.tripadvisor.com/" in i['href'] or "https://www.tripadvisor.it/" in i['href'] :
            link=i['href']
            res.close()
            return link
            break
      
    
    
    res.close()
    link='vuoto'
    return link


def listaUrlristoranti(url):
    lista=[]
    risultato={}
    headerino={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en,it-IT;q=0.9,it;q=0.8,en-US;q=0.7", 
    "Host": "httpbin.org", 
    "Referer": "https://www.google.com/", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "none", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-5f183236-b9bb16485b8ede302efe5738"
     }
    try:
        res=requests.get(url, headerino)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        elementi= soup.find_all('div', class_="_1llCuDZj")
        soup=bs4.BeautifulSoup(res.text, 'lxml')
        dato=soup.find(class_='nav next rndBtn ui_button primary taLnk')
        for i in elementi:
            link= i.find_all('a')
            #print(link[0]['href'])
            fin='https://www.tripadvisor.it' + link[0]['href']
            lista.append(fin)
        if dato!=None:
            linkiniz=dato['href']
            linkiniz=linkiniz[:linkiniz.index('#')]
            link='https://www.tripadvisor.it' + linkiniz
            risultato['next']=link
        res.close()
        #print(lista)
        risultato['ristoranti']=lista
    
        return risultato
    except requests.exceptions.MissingSchema():
        print('errorino')

#obsoleto
def getNewPage(url):
    res=requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'lxml')
    dato=soup.find(class_='nav next rndBtn ui_button primary taLnk')
    #print(dato)
    res.close()
    if dato!=None:
        linkiniz=dato['href']
        linkiniz=linkiniz[:linkiniz.index('#')]
        link='https://www.tripadvisor.it' + linkiniz
        print(link)
        return link
    else:
        print('è None')
    #return link


def getInfo(url):
    info={}
    headerino={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "en,it-IT;q=0.9,it;q=0.8,en-US;q=0.7", 
    "Host": "httpbin.org", 
    "Referer": "https://www.google.com/", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "none", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-5f183236-b9bb16485b8ede302efe5738"
     }
    res=requests.get(url, headerino)
    soup=bs4.BeautifulSoup(res.text, 'lxml')
    regexEmail=re.compile(r'mailto:\w+@')
        
    try:
        step=soup.find_all(class_="_1XLfiSsv")
        #print(soup.find_all(class_="_1XLfiSsv"))
        try:
            prezzo=step[0].text
            regexprezzo=re.compile(r'\d+')
            prezzo=regexprezzo.findall(prezzo)
            
            if len(prezzo)==0:
                prezzo='vuoto'
                info['prezzomax']='vuoto'
                info['prezzomin']='vuoto'
            elif len(prezzo)==1:
                prezzo=prezzo[0]
                info['prezzomin']=prezzo
                info['prezzomax']='vuoto'
            else:
                prezzo=f'{prezzo[0]}-{prezzo[1]}'
                prezzo=prezzo.split('-')
                info['prezzomin']=prezzo[0]
                info['prezzomax']=prezzo[1]      
        
        except IndexError:
            info['categoria']='vuoto'
            info['prezzomax']='vuoto'
            info['prezzomin']='vuoto'
        try:
            categoria=step[1].text
            info['categoria']=categoria
        except IndexError:
            info['categoria']='vuoto'
    except TypeError:
        info['categoria']='vuoto'
        info['prezzo']='vuoto'
     
    try:
        dato=soup.find(href=regexEmail)
        email=dato['href']
        email=email[7:]
        #print(email)
        regexFiltro=re.compile('\w+\d*@\w+\.\w+')
        email=regexFiltro.search(email)
        #print(email.group())
        try: 
            email=email.group()
            info['email']=email
        except AttributeError:
            info['email']='vuoto'
    except TypeError:
        #print('no mail')
        email='vuoto'
        info['email']=email
    try:
        nome=soup.find(class_='_3a1XQ88S').text
        info['nome']=nome
    except AttributeError:
        info['nome']='vuoto'
    #print(nome)
    #numero
    regexNumero= re.compile(r'tel:\+\d')
    try:
        phoneNumber=soup.find(class_='_3S6pHEQs', href=regexNumero).text
        info['phonenumber']=phoneNumber
    except AttributeError:
        phoneNumber='vuoto'
        info['phonenumber']='vuoto'
    #print(phoneNumber)
    #indirizzo
    try:
        indirizzo=soup.find(href='#MAPVIEW').text
        
        info['città']=indirizzo
        
    except AttributeError:
        
        info['città']='vuoto'
        
    res.close()
    info['url']=url
    
    return info
'''

path=Path.home()/'OneDrive/Desktop/linkpagine.xlsx'
wb=openpyxl.load_workbook(path)
linkutili=wb['Tranche6']
#linkutili2=wb['Tranche5']
lista=[]
for i in list(linkutili.columns)[0]:
    lista.append(i.value)
#for zi in list(linkutili2.columns)[0]:
 #   lista.append(zi.value)
#pprint.pprint(lista)
wb.close()
wb=openpyxl.Workbook()
wb.create_sheet('info')
sheet=wb['info']
risultati=[]
#email, phonenumber, nome, città, cap, indirizzo, url
fi=1
for i in lista:
    print('..', end='')
    risultati.append(getInfo(i))
    time.sleep(random.random())
    print(fi)
    fi=fi+1
    
pathfinale=Path.home()/'OneDrive/Desktop/info.xlsx' 


##########################
for n in range(1,len(risultati)):
    sheet.cell(n, 1).value=risultati[n-1]['nome']
    sheet.cell(n, 2).value=risultati[n-1]['email']
    sheet.cell(n, 3).value=risultati[n-1]['phonenumber']
    sheet.cell(n, 4).value=risultati[n-1]['città']
    sheet.cell(n, 5).value=risultati[n-1]['url']
wb.save(pathfinale)
wb.close()
     '''
#fare un ciclo while così che il next lo faccia in automatico e io non debba reimmettere, finisce quando la lista è [], termine del ciclo è una lista che cambia, ciclo break con dentro un for
'''
lista=[]
path=Path.home()/'OneDrive/Desktop/urlinizio.xlsx'
wb=openpyxl.load_workbook(path)
sheet=wb['urliniziali']
for i in list(sheet.columns)[0]:
    lista.append(i.value)
risultati=[]
urlpagina=[]
linkfinali=[]
wb.close()
x=True
u=0
while x:
    linkfinali=[]
    print(f'ciclo {u+1} iniziato', end=' ')
    for i in lista:
        try:
            x=listaUrlristoranti(i)
            print('..',  end=' ')
        
            for tiuz in x['ristoranti']:
                urlpagina.append(tiuz)
        except TypeError:
            fiu=1
        try:
            linkfinali.append(x['next'])
        except KeyError:
            fiu=0
    u=u+1
    print(f'ciclo {u} finito\n')
    lista=[]
    for z in linkfinali:
        lista.append(z)
    
    if len(lista)==0:
        x=False

wb=openpyxl.Workbook()
wb.create_sheet('urlristoranti')
sheet=wb['urlristoranti']

for n in range(1, len(urlpagina)):
    sheet.cell(n,1).value=urlpagina[n-1]
wb.save(path)
wb.close()
'''


path=Path.home()/'OneDrive/Desktop/progetti/Dati non BeU/excel2.xlsx'
wb=openpyxl.load_workbook(path)
sheet1=wb['Foglio1']

nome=[]
mail=[]
numero=[]
indirizzo=[]
url=[]

prezzomin=[]
prezzomax=[]    
categorie=[]
for t in list(sheet1.columns)[0]:       
       
    nome.append(t.value)

for x in list(sheet1.columns)[3]:
    indirizzo.append(x)
    
for y in list(sheet1.columns)[1]:
    mail.append(y)


    
wb.close()
pathissimo=Path.home()/'OneDrive/Desktop/progetti/Dati non BeU/excel2.xlsx'    
wb=openpyxl.Workbook()
wb.create_sheet('InfoBig')
foglio=wb['InfoBig']
vix=0
for fi in url:
    x=getInfo(fi)
    nome.append(x['nome'])
    prezzomin.append(x['prezzomin'])
    prezzomax.append(x['prezzomax'])
    categorie.append(x['categoria'])
    mail.append(x['email'])
    numero.append(x['phonenumber'])
    url.append(x['url'])
    indirizzo.append(x['città'])
    vix=vix+1
    print(f'{vix}..')
    
    
for zi in range(1,25785):
    foglio.cell(zi, 1).value=nome[zi-1]
    foglio.cell(zi, 2).value=mail[zi-1]
    foglio.cell(zi, 3).value=numero[zi-1]
    foglio.cell(zi, 4).value=indirizzo[zi-1]
    foglio.cell(zi, 5).value=url[zi-1]
    foglio.cell(zi, 6).value=categorie[zi-1]
    foglio.cell(zi, 7).value=prezzomin[zi-1]
    foglio.cell(zi, 8).value=prezzomax[zi-1]
    
wb.save(pathissimo)
wb.close()
print('finito')

