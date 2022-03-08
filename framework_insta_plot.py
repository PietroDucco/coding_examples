from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib as mpl
from numpy.random import randn
import os
from matplotlib import font_manager as fm
import matplotlib.image as image
import matplotlib.cbook as cbook
from pathlib import Path


#caricamento e inserimento dati
#inserisci fonte e titolo
fonte=''
titolo=''
logo= #indirizzo logo locale
with cbook.get_sample_data(logo) as file:
    im=image.imread(file)
urlfile=''
foglio_excel=''


#caricamento dati con pandas, varia da database a database
dati=pd.read_excel(urlfile, sheet_name=foglio_excel) #va scelto il file
dati=dati.drop(['Unnamed: 0', 'Unnamed: 3'], axis=1)  #le colonne da droppare possono variare e vanno scelte
dati=dati.dropna()


# caricamento font e colori
fpath=os.path.join('Roboto (1)/Roboto-Regular.ttf')
roboto=fm.FontProperties(fname=fpath)
titoli=fm.FontProperties(fname=os.path.join('font.ttf'))
blue='#1c1e42'
orange='#e47c4c'
bianco='#ffffff'
mpl.rcParams['axes.linewidth']=0
mpl.rcParams['grid.linewidth']=0.3
mpl.rcParams['savefig.facecolor']=blue


#definizione cycler colori
default_cycler = (cycler(color=['#c9ddff', '#ecb0e1' , '#2cf6b3' ,
        '#fde74c','#a40606' , '#9368b7' , '#aa3e98', '#f7f06d']))


#inizializzazione figura
fig, ax = plt.subplots(1,1)
fig.set_dpi(120)
fig.set_size_inches(640/120,640/120)
ax.set_prop_cycle(default_cycler)
fig.set_facecolor(blue)
ax.set_facecolor(blue)
plt.grid(color='#ffffff')
plt.grid(axis='x')


#plotting
#ax.scatter(randn(4), randn(4))
#ax.scatter(randn(9), randn(9))
#ax.scatter(randn(19), randn(19))


#tick's setting, y e x
testi = [] # inserire i testi
ax.set_xticklabels(testi, rotation=60) 
ax.set_xticks(np.arange(7))
ax.tick_params(color='#ffffff60',labelcolor='#ffffff')
leg=ax.legend(labels=['1','2','3'], framealpha=0.1)
for text in leg.get_texts():
    plt.setp(text, color='w')


#titolo e testi, x0,y0 vanno aggiustate per ogni grafico in base alla lunghezza dei testi
fig.text(0.02,0.9,titolo, color=orange, fontproperties=titoli, size=25) 
fig.text(0.02,0.02, f'Source: {fonte}', color=orange,  fontproperties=roboto, size=10)


#inserimento immagine-logo
newax = fig.add_axes([0.70, 0.76, 0.35, 0.35], anchor='NE', zorder=1, alpha=1)
newax.imshow(im)
newax.axis('off')

newax.set_facecolor(blue)


# aggiustamento assi, allargarli manualmente dall'editor di matplotlib
fig.subplots_adjust(bottom=0.225, top=0.85, left=0.085, right=0.965)


#salva figura, spesso salva di merda (non so perché, ma dalla command line (iPython) non crea questi problemi)
#fig.savefig('fig_num.png',dpi=120,facecolor=blue)



