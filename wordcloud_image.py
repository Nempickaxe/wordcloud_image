#!/usr/bin/env python
# coding: utf-8

import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import emoji
from collections import Counter
import PIL

def rawToDf(file):
    with open(file, 'r',encoding='utf8') as raw_data:
        raw_string = ' '.join(raw_data.read().split('\n')) # converting the list split by newline char. as one whole string as there can be multi-line messages
        user_msg = re.split('\d{1,2}/\d{1,2}/\d{2,4}, \d:\d{2} .{2} - ', raw_string) [1:] # splits at all the date-time pattern, resulting in list of all the messages with user names
        date_time = re.findall('\d{1,2}/\d{1,2}/\d{2,4}, \d:\d{2} .{2} - ', raw_string) # finds all the date-time patterns

        df = pd.DataFrame({'date_time': date_time, 'user_msg': user_msg}) # exporting it to a df
    # converting date-time pattern which is of type String to type datetime, format is to be specified for the whole string where the placeholders are extracted by the method
    try:
        df['date_time'] = df['date_time'].apply(lambda x: dateparser.parse(x))
    except:
        print("oo")
        try:
            df['date_time'] = pd.to_datetime(df['date_time'].str.strip(' -'), format='%m/%d/%y, %H:%M %p') #10/20/19, 10:24 pm -
        except:
            df['date_time'] = pd.to_datetime(df['date_time'].str.strip(' -'), format='%d/%m/%y, %H:%M %p') #20/10/2019, 10:24 pm -

    # split user and msg
    usernames = []
    msgs = []
    for i in df['user_msg']:
        a = re.split('([\w\W]+?):\s', i) # lazy pattern match to first {user_name}: pattern and spliting it aka each msg from a user
        if(a[1:]): # user typed messages
            usernames.append(a[1])
            msgs.append(a[2])
        else: # other notifications in the group(eg: someone was added, some left ...)
            usernames.append("grp_notif")
            msgs.append(a[0])

    # creating new columns

    df['user'] = usernames
    df['msg'] = msgs

    # dropping the old user_msg col.
    df.drop('user_msg', axis=1, inplace=True)

    return df

def clean_df(df):
    grp_notif = df[df['user']=="grp_notif"] #no. of grp notifications
    images = df[df['msg']=="<Media omitted> "] #no. of images, images are represented by <media omitted>
    df.drop(images.index, inplace=True) #removing images
    df.drop(grp_notif.index, inplace=True) #removing grp_notif
    return df


def create_user_wordcloud(messages, image_path, user, save_path):
    char_mask = np.array(PIL.Image.open(image_path))
    char_mask[char_mask == 0] = 255 #convert no background to white
    image_colors = ImageColorGenerator(char_mask)

    if user:
        filter_messages = messages.loc[messages['user']==user]['msg']
    else:
        filter_messages = messages.copy()
    filter_messages = filter_messages.str.lower().str.split()
    comment_words = ' '.join(filter_messages.apply(lambda x: ' '.join(x)).tolist())

    wc = WordCloud(background_color="white", max_words=300, width=800, height=800, mask=char_mask, random_state=1).generate(comment_words)
    # to recolour the image
    pil_wc = wc.recolor(color_func=image_colors)
    plt.imshow(pil_wc, interpolation="bilinear")
    pil_wc.to_file(save_path)
    
    layer1 = PIL.Image.open(save_path)
    layer2 = PIL.Image.open(image_path)
    blended = PIL.Image.blend(layer2, layer1, alpha=0.7)
    blended.save(save_path.split('.')[0]+"_blended.png")
    return pil_wc


def create_wordcloud_user_whatsapp(file, image_path, user, save_path):
    df = rawToDf(file)
    messages = clean_df(df)
    pillow_wc = create_user_wordcloud(messages, image_path, user, save_path)
    return pillow_wc

if __name__== "__main__":
    create_wordcloud_user_whatsapp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
