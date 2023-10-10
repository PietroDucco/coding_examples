

#for questions duccopietro@gmail.com

import os
import openai

import pandas as pd

from pathlib import Path

import time

import numpy as np



def more_together(series,index,amount,prompt):
    '''
    the method aims to instruct the GPT with a prompt and then paste texts to label
    series is a pandas series
    index is a point where to start from
    amount is the number of texts that we want to bundle together (these needs to be restricted by looking at the behavior of the GPT and the token limit.)
    prompt is the instruction for the GPT
    
    example: index=10 and amount=10 --> analyse 10 texts [10-20) 
    
                                                          
    EXAMPLE OF A SCRIPT
        You will be supplied with a list of responses. The responses refer to the usage of different platforms, the platform will be indicated in parentheses at the end of the response. Please classify responses based on the coding scheme below. Please note that each open-ended response can fall into multiple categories or even none. 

        FOMO: Respondent mentions fear of missing out, feeling out of the loop, their wish to stay connected, or justifies usage through others' usage. Examples: "I feel compelled to keep `in touch' with what I perceive as being the culturally relevant `thing' at the moment. It breeds a sense of FOMO when you don’t use it." (TikTok); "Everyone else uses it so I feel that I will be missing out if I don’t." (Instagram); "I still use navigation maps because it is what everyone uses ..." (Maps).
        Entertainment: Respondent mentions they use it to be entertained. Examples: "It’s a very good source of entertainment and it’s always something to do when bored." (TikTok); "It’s a default way to pass time when I’m bored." (Instagram).
        Addiction: Respondent mentions inability to let go or directly mentions addiction. Examples: "I use TikTok as a habit. I hate TikTok and know that I have other things I need to do, but I subconsciously click on it, then scroll for hours. It's very hard to control it." (TikTok); "Because I am addicted to the scrolling and tired of wasting valuable time on the app." (Instagram).
        Information: Respondent mentions informational purposes such as following the news, keeping abreast of college events, or getting directions. Examples: "for information on current events because i do not watch the news" (TikTok); "I use it to keep inform about my university events and news" (Instagram); "I don't know where to go" (Maps).
        Productivity/Convenience: Respondent mentions convenience of use or states to use platform for productive/business purposes. Examples: "It’s easy to see stuff I like (art, new art news, movie reviews, etc)." (TikTok); "I still use instagram for business purposes."; (Instagram); "It's more convenient than pulling out a map and I have a terrible sense of direction" (Maps).

        Let's think step by step. In order to complete this task you should follow these steps:
            i. For each of the answers go through each category one by one. For each category label as YES if the the response is likely to fit the content of the category and NO if it does not.
            ii. For each of the answers group all the categories (using the name in parenthesis) that you labeled as YES.
            iii. Arrange your classification in the format:
                1. [categories] 
                2. [categories] 
                3. [categories] 
                4. [categories] 
                5. [categories] 
                6. [categories] 
                7. [categories] 
                8. [categories] 
                9. [categories] 
                10. [categories] 
            
            iv. check that the results are 10 as the answers I asked you to label. 
            v. return the results in the format requested at iii
    
    '''
    di=series.iloc[index:index+amount].to_dict()
    text=''
    for i in di.keys():
        t=di[i]
        if type(t) is float:
            continue
        t=t.replace("\n"," ")
        
        text=text + f'{i}. {t}.'+'\n\n'
        
    print(text)
    chat=openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
        ],
  temperature=0
  )

    return chat['choices'][0]['message'].content
    


    
def label_data(dataset,text_col,cat_col,prompt,amount=10,t=0):
    '''
    

    Parameters
    ----------
    dataset : Pandas dataframe that possess a text_col and cat_col.
    text_col : dataset's column of the text we want to label.
    cat_col :  dataset's column of the output
        DESCRIPTION.
    prompt : Prompt used to label.
    amount : TYPE, optional
        DESCRIPTION. The default is 10.
    t : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    df : labeled dataset.

    '''
    df=dataset.copy()
    for i in range(t,df.shape[0],amount):
        if i+amount>=df.shape[0]:
            a=more_together(df[text_col],df.shape[0]-10,amount,prompt).split('\n')
            df.iloc[df.shape[0]-10:df.shape[0],df.columns.get_loc(cat_col)]=a
            break
        
        a=more_together(df[text_col],i,amount,prompt).split('\n')
        a=list(filter(lambda x: x!='',a))
        while len(a)!=amount:
            if i+amount>=df.shape[0] and len(a)==df.iloc[i:].shape[0]:
                df.iloc[i:i+amount,df.columns.get_loc(cat_col)]=a
                break
            a=more_together(df[text_col],i,amount,prompt).split('\n')
            a=list(filter(lambda x: x!='',a))
        df.iloc[i:i+amount,df.columns.get_loc(cat_col)]=a
    return df
    
 



'''
 Parameters
 ----------
 df : Input dataset.
 col : Desired column that you want to treat (only ONE).
 dictionary : Formatted in the same way as categories_active given a prompt at prompt_active
 ordinal : could also be left 1, useful if you have multiple coding schemes with names that overlap

 Returns
 -------
 res : dataset with the new columns encoded in a specific way given the dictionary.
 
 IT IS IMPORTANT TO CHECK THAT THE DICTIONARY KEYS DON'T LEAD TO A MULTIPLE AND OVERLAPPING LABELING, example 'Info':'Info','NO Public-info':'NOPUBL'
 since the method is case insensitive, is using x.lower(), all the output from GPT containing "NoPublic-Info" will also lead to the "Info" label besides the "NOPUBL", cases could checked by hand later.

'''

def label_text_dict(df,col,dictionary,ordinal):
   
    res=df.copy()
    cols=list(set(dictionary.values()))
    
    for i in cols:
        keys=[ k for k,v in dictionary.items() if v==i]
        
        res[f'{i}{ordinal}']=0
        
        for k in keys:
            res[f'{i}{ordinal}']=res[f'{i}{ordinal}'] + res.loc[:,col].apply(lambda x: k.lower() in x.lower()).map({True:1,False:0})
        res.loc[res[f'{i}{ordinal}']>0,f'{i}{ordinal}']=1
    return res
    


def label_hall(df,col,categories):
    '''
    

    Parameters
    ----------
    df : dataset to input.
    col : Column to inspect, 1 column only.
    categories : the mapping using for the categories.

    Returns
    -------
    res : It prints to screen the percentage of hallucinated entries. 
    In case you have a labeling that could return no categories (None), and the no categories (None, '', NONE) would be considered hallucinated cases.
    Returns a dataset with the wrong column, wrong_words column added.

    '''
    
    res=df.copy()
    res['text_2']=df[col].apply(lambda x: x[3:]).str.replace('.','').str.strip().str.replace('[','').str.replace(']','').str.replace('(','').str.replace(')','').str.replace(', ',',').str.split(',')
    ser_cat=df[col].apply(lambda x: x[3:]).str.replace('.','').str.strip()
    end=','.join(ser_cat.to_list())
    lista=end.replace('[','').replace(']','').replace('(','').replace(')','')
    c= set(lista.replace(', ',',').split(','))
    labels=pd.DataFrame(c,columns=['text'])
    labels['res']=labels.text.map(categories)
    labels=label_text_dict(labels,'text',categories,'')
    labels['sum']=labels.iloc[:,2:].T.sum()
    wrong_labels=labels[labels['sum']==0].text.to_list()
    
    res['wrong']=0
    res['wrong_words']=''
    for i in wrong_labels:
        
        res['wrong']=res['wrong'] + res.loc[:,'text_2'].apply(lambda x: i in x).map({True:1,False:0})
        res['wrong_words']=res['wrong_words'] + res.loc[:,'text_2'].apply(lambda x: i in x).map({True:f' {i}',False:''})
    
    print(f'ratio of affected rows: {res[res.wrong>0].shape[0]/res.shape[0]}')
    
    return res




#it prints comparison in terms of hallucination
def create_comparison(df,df2,cols):
    
    
    diff=df.loc[:,cols] - df2.loc[:,cols]
    print(f'hall df:{df[df.wrong>0].shape[0]/df.shape[0]}')
    print(f'hall df2:{df2[df2.wrong>0].shape[0]/df2.shape[0]}')
    print(f'hall df1 in df2 perc:{df2[df.wrong>0].wrong.mean()}')
    print(f'hall df2 in df1 perc:{df[df2.wrong>0].wrong.mean()}')
    print(f'mean distance by response in terms of cat: {diff.T.abs().sum().mean()}')
    print(f'mean distance by response (in terms of categories) on prompt 2 hall. {diff[df2.wrong>0].T.abs().sum().mean()}')
    print(f'mean distance by response (in terms of categories) on prompt 1 hall.{diff[df.wrong>0].T.abs().sum().mean()}')
    print(f'hall prompt 1: {df[df.wrong>0].shape[0]}')
    print(f'hall prompt 2: {df2[df2.wrong>0].shape[0]}')
    print(f'size:{df.shape[0]}')


