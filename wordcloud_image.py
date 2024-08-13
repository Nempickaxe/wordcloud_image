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
import dateparser

def rawToDf(file):
    """
    Convert a raw text file into a pandas DataFrame.

    Args:
        file (str): Path to the raw text file.

    Returns:
        pd.DataFrame: A DataFrame with 'date_time' and 'user_msg' columns.
    """
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
    messages = []
    for i in range(len(user_msg)):
        username = re.split(', \d{1,2}/\d{1,2}/\d{2,4}, \d:\d{2} .{2} - ', user_msg[i])[0]
        message = re.split(', \d{1,2}/\d{1,2}/\d{2,4}, \d:\d{2} .{2} - ', user_msg[i])[1]
        usernames.append(username)
        messages.append(message)

    df['user'] = usernames
    df['msg'] = messages

    return df

def clean_df(df):
    """
    Clean the DataFrame by removing group notifications and images.

    Args:
        df (pd.DataFrame): The DataFrame to be cleaned.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    grp_notif = df[df['user']=="grp_notif"] #no. of grp notifications
    images = df[df['msg']=="<Media omitted> "] #no. of images, images are represented by <media omitted>
    df.drop(images.index, inplace=True) #removing images
    df.drop(grp_notif.index, inplace=True) #removing grp_notif
    return df


def create_user_wordcloud(messages, image_path, user, save_path):
    """
    Create a word cloud for a given user.

    Args:
        messages (pd.DataFrame): The DataFrame with 'user' and 'msg' columns.
        image_path (str): Path to the image used as a mask.
        user (str): The username for which the word cloud is created.
        save_path (str): Path where the word cloud will be saved.

    Returns:
        None
    """
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
    """
    Create a word cloud for a given user from WhatsApp messages.

    Args:
        file (str): Path to the raw text file.
        image_path (str): Path to the image used as a mask.
        user (str): The username for which the word cloud is created.
        save_path (str): Path where the word cloud will be saved.

    Returns:
        None
    """
    df = rawToDf(file)
    messages = clean_df(df)
    pillow_wc = create_user_wordcloud(messages, image_path, user, save_path)
    return pillow_wc

if __name__== "__main__":
    create_wordcloud_user_whatsapp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
