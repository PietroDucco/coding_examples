
#######################

# IMPORT PACKAGES

########################

import os
import openai

import pandas as pd

from pathlib import Path

import time

import numpy as np

import sys

sys.path.append('C:\\Users\\ducco\\OneDrive\\Desktop\\work\\Roth\\GPTauto')

from GPT_SCRIPT import more_together, label_data, label_text_dict, label_hall_2

###########################

# DATA

###########################

#implement example and platform
openai.api_key=#

prompt_no_plat='''You will be supplied with a list of responses. The responses refer to the usage of different platforms, the platform will be indicated in parentheses at the end of the response. Please classify responses based on the coding scheme below. Please note that each open-ended response can fall into multiple categories or even none. 

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
    v. return the results in the format requested at iii'''

categories_no_plat={
    'FOMO':'FOMO',
    'Entertainment':'Entertainment',
    'Addiction':'Addiction',
    'Information':'Information',
    'Productivity/Convenience':'Productivity/Convenience','Productivity':'Productivity/Convenience','Convenience':'Productivity/Convenience',
        
    }


prompt_feel='''You will be supplied with a list of responses. The responses refer to the usage of different platforms, the platform will be indicated in parentheses at the end of the response. Please classify responses based on the coding scheme below. Please note that each open-ended response can fall into multiple categories or even none. 

FOMO: Respondent mentions fear of feeling missing out, left out, or being out of the loop. Examples: "I would probably feel somewhat out of the loop when it comes to trends, with a consistent feeling of FOMO." (TikTok); "I would feel really left out since a lot of people use it to communicate about events and parties and with one another" (Instagram); "I would feel a bit isolated, maybe excluded from certain conversations involving travel plans, etc" (Maps).

Unfair: Respondent mentions unfairness.
Impractical: Respondent mentions impracticality.
Inferior: Respondent feels inferior.
Dependent: Respondent feels dependent.
Bad: Respondent feels bad.
Stressed: Respondent feels stressed.
Lost: Respondent feels lost.
    

Indifferent: Respondent states that they would not be particularly affected. Examples: "No different, because I don’t use tiktok often anyway";  (TikTok); "I would be fine. I don't really post on Instagram. It wouldn't be much of a change."  (Instagram);  ""Wouldn’t mind as long as knew my way around" (Maps).

Challenge: Respondent expresses it would be a nice challenge for them.
Good: Respondent mentions it would be good for them.
Unpressured: Respondent mentions she would feel relieved, unpressured, or free.
Self-improvement: Respondent mentions she would feel good.

Indifferent given payment: (self-explanatory).
Indifferent given study: Respondent states indifference mentioning being part of a study or deactivating for only a limited time.
Substitute: Respondent mentions she would substitute the platform with another one. 
Martyr: Respondent mentions she would rather be the only one who has to quit platform, since it is an inconvenience to others.
Independent: Respondent either directly mentions independence or doing something different than 'the rest'.    



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
    v. return the results in the format requested at iii'''
    
categories_feel={
'FOMO':'FOMO',

'Negative':'Negative',
'Unfair': 'Negative',
'Impractical': 'Negative',
'Inferior': 'Negative',
'Dependent': 'Negative',
'Bad': 'Negative',
'Stressed': 'Negative',
'Lost': 'Negative',

'Indifferent':'Indifferent',

'Beneficial':'Beneficial',
'Challenge':'Beneficial',
'Good':'Beneficial',
'Unpressured':'Beneficial',
'Self-improvement':'Beneficial',

'Other':'Other',
'Indifferent given payment':'Other',
'Indifferent given study':'Other',
'Substitute':'Other',
'Martyr':'Other',
'Independent':'Other',
}



#loading data

#active

path_tiktok= Path.home()/'Downloads/categorised_tiktok.xlsx' #upload your file


df_tiktok=pd.read_excel(path_tiktok)

df_tiktok=df_tiktok[(df_tiktok['1 Bot']==0) & (df_tiktok['2 Bot']==0)].loc[:,['responseid','why_no_sm','feel_only_one']]
#df_tiktok.columns=['responseid','text_1','text_2']
df_tiktok['cat_plat']=''
df_tiktok['cat_feel']=''
df_tiktok['platform']='tiktok'

df_tiktok['why_no_sm_2']= df_tiktok['why_no_sm'] + '. (' + df_tiktok['platform'] +')'

df_tiktok['feel_only_one_2']= df_tiktok['feel_only_one'] + '. (' + df_tiktok['platform'] +')'

#[(df_tiktok['1 Bot']==0) & (df_tiktok['2 Bot']==0)]
#passive

path_ig= Path.home()/'Downloads/categorised_ig_maps.xlsx' #upload your file

df_ig=pd.read_excel(path_ig)
df_ig['2 Bot']=df_ig['2 Bot'].fillna(0)
df_ig=df_ig[(df_ig['1 Bot']==0) & (df_ig['2 Bot']==0)].loc[:,['responseid','platform','why_no_platform','feel_only_one']]

#[(df_ig['1 Bot']==0) & (df_ig['2 Bot']==0)]

df_ig['cat_plat']=''
df_ig['cat_feel']=''


df_ig['why_no_platform_2']= df_ig['why_no_platform'] + '. (' + df_ig['platform'] +')'

df_ig['feel_only_one_2']= df_ig['feel_only_one'] + '. (' + df_ig['platform'] +')'


df_ig_plat=df_ig[df_ig.why_no_platform.notna()]


#############################

# LABELING

#############################

#extracting categories

#tiktok
df_tiktok_v1=label_data(df_tiktok,'why_no_sm_2','cat_plat',prompt_no_plat)
df_tiktok_v2=label_data(df_tiktok_v1,'feel_only_one_2','cat_feel',prompt_feel)



#igmaps
df_ig_plat_v1=label_data(df_ig_plat,'why_no_platform_2','cat_plat',prompt_no_plat)
df_ig_v2=label_data(df_ig,'feel_only_one_2','cat_feel',prompt_feel)


#create matrix with categories

df_tiktok_lab=label_text_dict(df_tiktok_v2,'cat_plat',categories_no_plat,'_plat')
df_tiktok_lab=label_text_dict(df_tiktok_lab,'cat_feel',categories_feel,'_feel')

df_ig_plat_lab=label_text_dict(df_ig_plat_v1,'cat_plat',categories_no_plat,'_plat')
df_ig_v2_lab=label_text_dict(df_ig_v2, 'cat_feel', categories_feel, '_feel')



###########

# HALLUCINATION

########


# will print to screen hallucination %


label_hall(df_tiktok_lab,'cat_plat',categories_no_plat)

label_hall(df_tiktok_lab,'cat_feel',categories_feel)

label_hall(df_ig_plat_lab,'cat_plat',categories_no_plat)

label_hall(df_ig_v2_lab,'cat_feel',categories_feel)



#################

#save_data

#################

#merge back
df_ig_plat_lab= df_ig_plat_lab.drop(['feel_only_one','cat_feel'],axis=1)
df_ig_v2_lab= df_ig_v2_lab.drop(['why_no_platform','cat_plat'],axis=1)


df_ig_final=df_ig_v2_lab.merge(df_ig_plat_lab,'outer',on='responseid')


#bot
#df_ig_bot=pd.read_excel(path_ig)
#df_ig_bot=df_ig_bot[(df_ig_bot['1 Bot']==1) | (df_ig_bot['2 Bot']==1)]

#df_tt_bot=pd.read_excel(path_tiktok)
#df_tt_bot=df_tt_bot[(df_tt_bot['1 Bot']==1) | (df_tt_bot['2 Bot']==1)]


#SAVE
#df_ig_final.to_csv('categorised_GPT_ig_maps_v21.csv')
#df_tiktok_lab.to_csv('categorised_GPT_tiktok_v21.csv')


