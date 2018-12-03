from DataCollection import botometer, constants
from botometer import NoTimelineError
import tweepy
import sys
import os
import glob
import csv
import pandas as pd
import smtplib
import random
import time


def get_all_ids(streaming_file_name):
    # Load streamingData from csv
    path = os.path.dirname(os.path.abspath(__file__)) + '/' + streaming_file_name
    df = pd.read_csv(path, header=0)

    # Calculate the tweet count for each user id
    df['stream_tweet_count'] = df.groupby('user_id')['user_id'].transform('count')

    x = df['stream_tweet_count'].tolist()

    for i in range(100):
        print(x[i])


get_all_ids('StreamData-#maga-#qanon-#trump-86400-20180602-140803.csv')






