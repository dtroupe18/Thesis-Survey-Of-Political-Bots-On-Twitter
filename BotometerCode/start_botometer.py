from DataCollection import botometer, constants
from botometer import NoTimelineError
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import ReadTimeoutError, ProtocolError, SSLError
import tweepy
import sys
import os
import glob
import csv
import pandas as pd
import smtplib
import random
import time


class BotometerClient:

    def __init__(self, filename, continuing=False):

        self.bot_meter = botometer.Botometer(wait_on_ratelimit=True,
                                             mashape_key=constants.mashape_key,
                                             **constants.botometer_auth)

        self.master_file_name = 'MasterIDs.csv'
        # Store all the ids we get an error on so they aren't checked again
        self.error_ids_file_name = 'ErrorIDs.csv'
        self.unique_ids_file_name = 'UniqueIDs.csv'

        # Time so we can take how long it takes to scrape all these ids
        self.start_time = time.time()

        if filename.startswith('StreamIDs'):
            self.stream_ids_file_name = filename
            self.streaming_file_name = filename.replace('StreamIDs', 'StreamData')
            self.timeline_file_name = filename.replace('StreamIDs', 'TimelineData')
            self.mentions_file_name = filename.replace('StreamIDs', 'MentionsData')

        elif filename.startswith('StreamData'):
            self.streaming_file_name = filename
            self.stream_ids_file_name = filename.replace('StreamData', 'StreamIDs')
            self.timeline_file_name = filename.replace('StreamData', 'TimelineData')
            self.mentions_file_name = filename.replace('StreamData', 'MentionsData')

        elif filename.startswith('MERGED-StreamData'):
            self.streaming_file_name = filename
            self.stream_ids_file_name = filename.replace('MERGED-StreamData', 'StreamIDs')
            self.timeline_file_name = filename.replace('MERGED-StreamData', 'TimelineData')
            self.mentions_file_name = filename.replace('MERGED-StreamData', 'MentionsData')

        else:
            print('\nERROR: FILE NAME PROVIDED MUST BE FOR STREAMING, MERGED, OR SCRAPED-IDS CSV!!!')
            return

        self.create_master_file()
        self.create_stream_ids_file()
        self.create_error_file()
        self.create_timeline_file()
        self.create_mentions_file()
        self.tweepy_api = constants.api

        if continuing:
            self.df = BotometerClient.get_remaining_ids(self.stream_ids_file_name,
                                                        self.streaming_file_name,
                                                        self.error_ids_file_name)

            self.stream_ids_df = BotometerClient.load_stream_ids_df(self.stream_ids_file_name)

        else:
            self.df = BotometerClient.get_all_ids(self.streaming_file_name, self.master_file_name)

        self.error_df = BotometerClient.load_error_ids_df(self.error_ids_file_name)
        self.master_df = BotometerClient.load_master_ids_df(self.master_file_name)

    def start_bot_collection(self):
        # Get botometer scores for every id in the stream
        print('Starting Client....')
        number_of_accounts_to_check = len(self.df)

        for index, row in self.df.iterrows():
            print('On index: ', index, ' out of ', number_of_accounts_to_check)
            print('row: ', row)
            tweet_text = row['status_text']
            tweet_time = row['status_created_at']
            user_id = row['user_id']
            tweet_count = row['stream_tweet_count']

            if user_id not in self.error_df.user_id.values:

                if user_id in self.master_df.user_id.values:
                    print('UserID already in master using existing bot score value!')
                    master_row = self.master_df.loc[self.master_df['user_id'] == user_id]
                    user = BotometerClient.get_user_data_as_dict(master_row)
                    cap = master_row.iloc[0]['cap']
                    bot_score = master_row.iloc[0]['bot_score']
                    self.save_to_stream_ids(user_id, bot_score, cap, tweet_count, tweet_time, tweet_text, user)

                else:
                    try:
                        result, payload = self.bot_meter.check_account(user_id,
                                                                       full_user_object=True,
                                                                       return_user_data=True)
                        cap = result['cap']['universal']
                        bot_score = result['display_scores']['universal']
                        print('cap: ', cap)
                        print('bot score: ', bot_score)

                        if cap > 0.70:
                            self.send_tweet(payload['user']['screen_name'], cap)

                        # Save to Master, Mentions, and Timeline
                        self.save_to_master(user_id, bot_score, cap, tweet_count,
                                            tweet_time, tweet_text, payload['user'])

                        self.save_to_stream_ids(user_id, bot_score, cap, tweet_count,
                                                tweet_time, tweet_text, payload['user'])

                        self.save_to_mentions(payload['mentions'])
                        self.save_to_timeline(payload['timeline'], cap, bot_score)

                    except tweepy.TweepError as exc:
                        # Save this user_id so we don't check it again
                        self.save_to_error_ids(user_id)
                        print('Error encountered for ', user_id)
                        print('Error response: ', exc.response)
                        print('Error reason: ', exc.reason)
                        print('Error api code: ', exc.api_code)
                        print('\n')

                    except NoTimelineError as err:
                        self.save_to_error_ids(user_id)
                        print('No Timeline error caught: ', err)
                        print('\n')

                    except (ConnectionError, HTTPError, Timeout, ReadTimeoutError, ProtocolError, SSLError) as exc:
                        print("New exception: ", exc)
                        time.sleep(120)

        print('\n\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print('Finished! :)')
        time_diff = int(time.time() - self.start_time)
        num_ids = str(len(self.df))
        print('It look {:02d}:{:02d}:{:02d} time to collect ' + num_ids
              + ' bot scores!'.format(time_diff // 3600, (time_diff % 3600 // 60), time_diff % 60))
        BotometerClient.send_notification_email()
        return

    def send_tweet(self, user, cap):

        low_start_options = ['Beep, Beep, I think I found another bot... {0}'.format(user),
                             'R2 says {0}'.format(user),
                             'It looks like {0}'.format(user),
                             'I\'ve calculated that {}'.format(user)
                             ]

        high_start_options = ['I spy a bot... {0}'.format(user),
                              'Danger Will Robinson I\'ve found another political bot {0}'.format(user),
                              'Robot in disguise {0}'.format(user),
                              'Looks like {0} is breaking the first law: A robot may not injure a human being or, '
                              'through inaction, allow a human being to come to harm. {1}'.format(user, user),
                              'I guess {0} doesn\'t know the Zeroth Law: A robot may not harm humanity, or, by '
                              'inaction, allow humanity to come to harm. {1}'.format(user, user)
                              ]

        cap *= 100
        cap = round(cap, 2)

        if cap < 90:
            start = random.choice(low_start_options)
            ending = ' has a botometer score of {0}%, suggesting it could be a bot or bot assisted. ' \
                     '#politicalbots'.format(cap)
        else:
            start = random.choice(high_start_options)
            ending = ' has a botometer score of {0}%, suggesting it is probably a bot. #politicalbots'.format(cap)

        tweet_text = "{0}{1}".format(start, ending)
        self.tweepy_api.update_status(tweet_text)

        return

    def save_to_error_ids(self, user_id):
        error_ids_file = open(self.error_ids_file_name, 'a')
        error_writer = csv.writer(error_ids_file)

        try:
            error_writer.writerow([user_id])

        except Exception as exc:
            print(exc)
            pass

        error_ids_file.close()
        return

    def save_to_stream_ids(self, user_id, bot_score, cap, tweet_count, tweet_time, tweet_text, user_dict):
        # Open the csv file created previously
        file = open(self.stream_ids_file_name, 'a')

        # Create a csv writer
        writer = csv.writer(file)

        try:
            writer.writerow([user_id,
                             bot_score,
                             cap,
                             tweet_count,
                             tweet_time,
                             tweet_text,
                             user_dict['favourites_count'],
                             user_dict['statuses_count'],
                             user_dict['description'],
                             user_dict['location'],
                             user_dict['created_at'],
                             user_dict['verified'],
                             user_dict['following'],
                             user_dict['url'],
                             user_dict['listed_count'],
                             user_dict['followers_count'],
                             user_dict['default_profile_image'],
                             user_dict['utc_offset'],
                             user_dict['friends_count'],
                             user_dict['default_profile'],
                             user_dict['name'],
                             user_dict['lang'],
                             user_dict['screen_name'],
                             user_dict['geo_enabled'],
                             user_dict['profile_background_color'],
                             user_dict['profile_image_url'],
                             user_dict['time_zone'],
                             user_dict['listed_count']
                             ])

        except Exception as exc:
            print(exc)
            pass

        # Close the csv file
        file.close()
        return

    def save_to_master(self, user_id, bot_score, cap, tweet_count, tweet_time, tweet_text, user_dict):
        # Open the csv file created previously
        master_file = open(self.master_file_name, 'a')

        # Create a csv writer
        master_writer = csv.writer(master_file)

        try:
            master_writer.writerow([user_id,
                                    bot_score,
                                    cap,
                                    tweet_count,
                                    tweet_time,
                                    tweet_text,
                                    user_dict['favourites_count'],
                                    user_dict['statuses_count'],
                                    user_dict['description'],
                                    user_dict['location'],
                                    user_dict['created_at'],
                                    user_dict['verified'],
                                    user_dict['following'],
                                    user_dict['url'],
                                    user_dict['listed_count'],
                                    user_dict['followers_count'],
                                    user_dict['default_profile_image'],
                                    user_dict['utc_offset'],
                                    user_dict['friends_count'],
                                    user_dict['default_profile'],
                                    user_dict['name'],
                                    user_dict['lang'],
                                    user_dict['screen_name'],
                                    user_dict['geo_enabled'],
                                    user_dict['profile_background_color'],
                                    user_dict['profile_image_url'],
                                    user_dict['time_zone'],
                                    user_dict['listed_count']
                                    ])

        except Exception as exc:
            print(exc)
            pass

        # Close the csv file
        master_file.close()
        return

    def save_to_timeline(self, statuses, cap, bot_score):
        # Open the csv file created previously
        timeline_file = open(self.timeline_file_name, 'a')

        # Create a csv writer
        timeline_writer = csv.writer(timeline_file)

        for status in statuses:
            hashtags, mentions, urls = BotometerClient.parse_entities(status['entities'])

            try:
                # Write the tweet's information to the csv file
                timeline_writer.writerow([status['user']['id'],
                                          cap,
                                          bot_score,
                                          status['text'],
                                          status['created_at'],
                                          status['lang'],
                                          status['place'],
                                          status['coordinates'],
                                          status['id'],
                                          status['favorite_count'],
                                          status['retweeted'],
                                          status['source'],
                                          status['favorited'],
                                          status['retweet_count'],
                                          hashtags,
                                          len(status['entities']['hashtags']),
                                          mentions,
                                          len(status['entities']['user_mentions']),
                                          urls,
                                          len(status['entities']['urls']),
                                          status['entities']
                                          ])
            # If some error occurs
            except Exception as exc:
                print(exc)
                pass

        # Close the csv file
        timeline_file.close()

        # Return nothing
        return

    def save_to_mentions(self, statuses):
        # Open the csv file created previously
        mentions_file = open(self.mentions_file_name, 'a')

        # Create a csv writer
        mentions_writer = csv.writer(mentions_file)

        for status in statuses:
            hashtags, mentions, urls = BotometerClient.parse_entities(status['entities'])

            try:
                # Write the mention's information to the csv file
                mentions_writer.writerow([status['text'],
                                          status['created_at'],
                                          status['lang'],
                                          status['place'],
                                          status['coordinates'],
                                          status['id'],
                                          status['favorite_count'],
                                          status['retweeted'],
                                          status['source'],
                                          status['favorited'],
                                          status['retweet_count'],
                                          hashtags,
                                          len(status['entities']['hashtags']),
                                          mentions,
                                          len(status['entities']['user_mentions']),
                                          urls,
                                          len(status['entities']['urls']),
                                          status['entities'],
                                          status['user']['favourites_count'],
                                          status['user']['statuses_count'],
                                          status['user']['description'],
                                          status['user']['location'],
                                          status['user']['id'],
                                          status['user']['created_at'],
                                          status['user']['verified'],
                                          status['user']['following'],
                                          status['user']['url'],
                                          status['user']['listed_count'],
                                          status['user']['followers_count'],
                                          status['user']['default_profile_image'],
                                          status['user']['utc_offset'],
                                          status['user']['friends_count'],
                                          status['user']['default_profile'],
                                          status['user']['name'],
                                          status['user']['lang'],
                                          status['user']['screen_name'],
                                          status['user']['geo_enabled'],
                                          status['user']['profile_background_color'],
                                          status['user']['profile_image_url'],
                                          status['user']['time_zone'],
                                          status['user']['listed_count']
                                          ])

            # If some error occurs
            except Exception as exc:
                print(exc)
                pass

        # Close the csv file
        mentions_file.close()
        return

    def create_error_file(self):
        if os.path.isfile(self.error_ids_file_name):
            print("Error file found")
            return

        else:
            error_file = open(self.error_ids_file_name, 'w')

            try:
                writer = csv.writer(error_file)
                writer.writerow(['user_id'])

            except Exception as exc:
                print(exc)
                pass

            error_file.close()
            return

    def create_master_file(self):
        if os.path.isfile(self.master_file_name):
            print('Master ID file found')
            return

        else:
            print('Creating master ID file...')
            csv_file = open(self.master_file_name, "w")

            try:
                writer = csv.writer(csv_file)

                writer.writerow(['user_id',
                                 'bot_score',
                                 'cap',
                                 'tweet_count',
                                 'tweet_time',
                                 'tweet_text',
                                 'user_favourites_count',
                                 'user_statuses_count',
                                 'user_description',
                                 'user_location',
                                 'user_created_at',
                                 'user_verified',
                                 'user_following',
                                 'user_url',
                                 'user_listed_count',
                                 'user_followers_count',
                                 'user_default_profile_image',
                                 'user_utc_offset',
                                 'user_friends_count',
                                 'user_default_profile',
                                 'user_name',
                                 'user_lang',
                                 'user_screen_name',
                                 'user_geo_enabled',
                                 'user_profile_background_color',
                                 'user_profile_image_url',
                                 'user_time_zone',
                                 'user_listed_count'
                                 ])

            except Exception as exc:
                print('Error writing to csv: ', exc)

            return

    def create_stream_ids_file(self):
        if os.path.isfile(self.stream_ids_file_name):
            print('StreamIDs file found!')
            return

        else:
            print('Creating stream ids file...')
            csv_file = open(self.stream_ids_file_name, "w")

            try:
                writer = csv.writer(csv_file)

                writer.writerow(['user_id',
                                 'bot_score',
                                 'cap',
                                 'tweet_count',
                                 'tweet_time',
                                 'tweet_text',
                                 'user_favourites_count',
                                 'user_statuses_count',
                                 'user_description',
                                 'user_location',
                                 'user_created_at',
                                 'user_verified',
                                 'user_following',
                                 'user_url',
                                 'user_listed_count',
                                 'user_followers_count',
                                 'user_default_profile_image',
                                 'user_utc_offset',
                                 'user_friends_count',
                                 'user_default_profile',
                                 'user_name',
                                 'user_lang',
                                 'user_screen_name',
                                 'user_geo_enabled',
                                 'user_profile_background_color',
                                 'user_profile_image_url',
                                 'user_time_zone',
                                 'user_listed_count'
                                 ])

            except Exception as exc:
                print('Error writing to csv: ', exc)

            return

    def create_timeline_file(self):
        if os.path.isfile(self.timeline_file_name):
            print('Timeline file found')
            return

        timeline_file = open(self.timeline_file_name, 'w')
        timeline_writer = csv.writer(timeline_file)

        try:
            # Write timeline header
            timeline_writer.writerow(['user_id',
                                      'user_cap',
                                      'user_bot_score',
                                      'status_text',
                                      'status_created_at',
                                      'status_lang',
                                      'status_place',
                                      'status_coordinates',
                                      'status_id',
                                      'status_favorite_count',
                                      'status_retweeted',
                                      'status_source',
                                      'status_favorited',
                                      'status_retweet_count',
                                      'status_hashtags',
                                      'status_hashtag_count',
                                      'status_mentions',
                                      'status_mentions_count',
                                      'status_urls',
                                      'status_url_count',
                                      'status_entities'
                                      ])
        except Exception as exc:
            print('Error writing to timeline csv: ', exc)

        return

    def create_mentions_file(self):
        if os.path.isfile(self.mentions_file_name):
            print('Mentions file found')
            return

        mentions_file = open(self.mentions_file_name, 'w')
        mentions_writer = csv.writer(mentions_file)

        try:
            # Write mentions header
            mentions_writer.writerow(['status_text',
                                      'status_created_at',
                                      'status_lang',
                                      'status_place',
                                      'status_coordinates',
                                      'status_id',
                                      'status_favorite_count',
                                      'status_retweeted',
                                      'status_source',
                                      'status_favorited',
                                      'status_retweet_count',
                                      'status_hashtags',
                                      'status_hashtag_count',
                                      'status_mentions',
                                      'status_mentions_count',
                                      'status_urls',
                                      'status_url_count',
                                      'status_entities',
                                      'user_favourites_count',
                                      'user_statuses_count',
                                      'user_description',
                                      'user_location',
                                      'user_id',
                                      'user_created_at',
                                      'user_verified',
                                      'user_following',
                                      'user_url',
                                      'user_listed_count',
                                      'user_followers_count',
                                      'user_default_profile_image',
                                      'user_utc_offset',
                                      'user_friends_count',
                                      'user_default_profile',
                                      'user_name',
                                      'user_lang',
                                      'user_screen_name',
                                      'user_geo_enabled',
                                      'user_profile_background_color',
                                      'user_profile_image_url',
                                      'user_time_zone',
                                      'user_listed_count'
                                      ])
        except Exception as exc:
            print('Error writing to csv: ', exc)

        return

    ###########################
    # Start of static methods #
    ###########################

    @staticmethod
    def get_user_data_as_dict(df):
        print(df)
        user_dict = {'favourites_count': df.iloc[0]['user_favourites_count'],
                     'statuses_count': df.iloc[0]['user_statuses_count'],
                     'description': df.iloc[0]['user_description'],
                     'location': df.iloc[0]['user_location'],
                     'created_at': df.iloc[0]['user_created_at'],
                     'verified': df.iloc[0]['user_verified'],
                     'following': df.iloc[0]['user_following'],
                     'url': df.iloc[0]['user_url'],
                     'listed_count': df.iloc[0]['user_listed_count'],
                     'followers_count': df.iloc[0]['user_followers_count'],
                     'default_profile_image': df.iloc[0]['user_default_profile_image'],
                     'utc_offset': df.iloc[0]['user_utc_offset'],
                     'friends_count': df.iloc[0]['user_friends_count'],
                     'default_profile': df.iloc[0]['user_default_profile'],
                     'name': df.iloc[0]['user_name'],
                     'lang': df.iloc[0]['user_lang'],
                     'screen_name': df.iloc[0]['user_screen_name'],
                     'geo_enabled': df.iloc[0]['user_geo_enabled'],
                     'profile_background_color': df.iloc[0]['user_profile_background_color'],
                     'profile_image_url': df.iloc[0]['user_profile_image_url'],
                     'time_zone': df.iloc[0]['user_time_zone']}

        return user_dict

    #########################################################
    # Load remaining IDs from a previously generated sample #
    #########################################################
    @staticmethod
    def get_remaining_ids(stream_ids_file_name, streaming_file_name, error_ids_filename):
        # Load streamingData from csv
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + streaming_file_name
        df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        # Calculate the tweet count for each user id
        df['stream_tweet_count'] = df.groupby('user_id')['user_id'].transform('count')

        # Drop all the columns we don't care about
        column_list = ['status_text', 'status_created_at', 'user_id', 'stream_tweet_count']
        df = df[column_list]
        original_size = len(df)

        # Drop duplicate ids since we only need to get the user data once
        df = df.drop_duplicates('user_id', keep='last')
        unique_size = len(df)
        print('Out of ', original_size, ' tweets there were ', (original_size - unique_size), ' duplicate ID\'s')

        # Drop any rows that are missing the required columns
        df.dropna(subset=['status_text', 'status_created_at', 'user_id', 'stream_tweet_count'])

        print('Dropped', (unique_size - len(df)), 'rows with missing data!')

        # Load sampledIds from csv
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + stream_ids_file_name
        stream_ids_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')
        all_stream_ids = stream_ids_df['user_id'].tolist()

        print('Total number of stream IDs already checked: ', len(stream_ids_df))

        df = df[~df['user_id'].isin(all_stream_ids)]
        print('After comparing with stream ids there are ', len(df), ' ids left!')

        # Read in Error IDs and remove any values already created
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + error_ids_filename
        error_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')
        error_ids = error_df['user_id'].tolist()

        print('ids in error ids: ', len(error_df))

        df = df[~df['user_id'].isin(error_ids)]
        print('After comparing with error ids there are ', len(df), ' ids left!')

        return df

    @staticmethod
    def get_all_ids(streaming_file_name, master_file_name):

        # Load streamingData from csv
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + streaming_file_name
        master_path = os.path.dirname(os.path.abspath(__file__)) + '/' + master_file_name

        df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')
        master_df = pd.read_csv(master_path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        # Calculate the tweet count for each user id
        df['stream_tweet_count'] = df.groupby('user_id')['user_id'].transform('count')

        # Drop all the columns we don't care about
        column_list = ['status_text', 'status_created_at', 'user_id', 'stream_tweet_count']
        df = df[column_list]
        original_size = len(df)

        # Drop duplicate ids since we only need to get the user data once
        df = df.drop_duplicates('user_id', keep='last')
        unique_size = len(df)
        print('Out of ', original_size, ' tweets there were ', (original_size - unique_size), ' duplicate ID\'s')

        # Drop all ids that are already in master_df
        master_id_list = master_df.user_id.tolist()
        df = df[~df.user_id.isin(master_id_list)]

        print('Out of ', unique_size, ' there were ', (unique_size - len(df)), ' ids that already have scores')
        print('Collecting bot scores for ', len(df), ' new ids')

        # print('Gathering bot scores for ', unique_size, ' user ids!')

        # Drop any rows that are missing the required columns
        df.dropna(subset=['status_text', 'status_created_at', 'user_id', 'stream_tweet_count'])

        print('Dropped', (unique_size - len(df)), 'rows with missing data!')

        return df

    #####################################
    # Load Data from Streaming CSV File #
    #####################################
    @staticmethod
    def load_master_ids_df(master_file_name):
        # Read in MasterIDs
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + master_file_name
        master_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        return master_df

    @staticmethod
    def load_error_ids_df(error_ids_file_name):
        # Read in Error IDs
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + error_ids_file_name
        error_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        return error_df

    @staticmethod
    def load_stream_ids_df(stream_ids_file_name):
        # Read in stream IDs
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + stream_ids_file_name
        stream_id_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        return stream_id_df

    #################################
    # One function to rule them all #
    #################################
    @staticmethod
    def start_mining(file_name):
        print('\nStarting Botometer mining...')

        # Check if the desired csv file exists
        if os.path.isfile(file_name):
            if file_name.startswith('StreamIDs'):
                print('\nFound SampledIDs file. Continuing to mine...')
                client = BotometerClient(file_name, continuing=True)
            else:
                print('\nStreaming data found')
                client = BotometerClient(file_name)

            # Start it up
            client.start_bot_collection()

        else:
            print('Error: requested csv file does not exist!')
            return

    @staticmethod
    def show_csv_files():
        print("\nI found the following csv files...")

        path = os.path.dirname(os.path.abspath(__file__))
        extension = 'csv'
        os.chdir(path)
        results = [i for i in glob.glob('*.{}'.format(extension))]
        results.sort()

        for result in results:
            print(result)

        return

    ###################
    # Parsing Methods #
    ###################

    @staticmethod
    def parse_entities(entities):
        hashtag_key = 'hashtags'
        mentions_key = 'user_mentions'
        url_key = 'urls'

        if hashtag_key in entities:
            hashtag_dict = entities[hashtag_key]
            hashtag_text = BotometerClient.parse_hashtags(hashtag_dict)
        else:
            hashtag_text = ''

        if mentions_key in entities:
            mentions_dict = entities[mentions_key]
            mentions_text = BotometerClient.parse_mentions(mentions_dict)
        else:
            mentions_text = ''

        if url_key in entities:
            url_dict = entities[url_key]
            url_text = BotometerClient.parse_urls(url_dict)
        else:
            url_text = ''

        return hashtag_text, mentions_text, url_text

    @staticmethod
    def parse_hashtags(hashtag_dict):
        hashtag_text = ''
        for dictionary in hashtag_dict:
            if 'text' in dictionary:
                if hashtag_text != '':
                    hashtag_text += ' ' + dictionary['text']
                else:
                    hashtag_text += dictionary['text']

        return hashtag_text

    @staticmethod
    def parse_mentions(mentions_dict):
        mentions_text = ''
        for dictionary in mentions_dict:
            if 'id_str' in dictionary:
                if mentions_text != '':
                    mentions_text += ' ' + dictionary['id_str']
                else:
                    mentions_text += dictionary['id_str']

        return mentions_text

    @staticmethod
    def parse_urls(url_dict):
        url_text = ''
        for dictionary in url_dict:
            if 'url' in dictionary:
                if url_text != '':
                    url_text += ' ' + dictionary['url']
                else:
                    url_text += dictionary['url']

        return url_text

    ######################
    # Email Notification #
    ######################
    @staticmethod
    def send_notification_email():
        # Email myself when the script finishes so I can start on the next set of data
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(constants.email_address, constants.password)

        subject = 'Botometer Script'
        text = 'Botometer Script Finished!'
        message = 'Subject: {}\n\n{}'.format(subject, text)
        server.sendmail(constants.email_address, constants.real_email, message)
        server.quit()

        return


length = len(sys.argv)
if length == 1:
    print('Error: please provide csv file name or type \'showCSVs\' to see the available files or type help for '
          'more information')
elif length == 2:
    arg = sys.argv[1]
    if arg == 'showCSVs':
        BotometerClient.show_csv_files()
    elif arg == 'help':
        print('Type showCSVs to see a list of the csv files in this directory that can be passed as a parameter')
        print('Sample call: python3 start_botometer.py StreamData-#maga-#qanon-#roseanne-20180531-105244.csv')
    else:
        try:
            BotometerClient.start_mining(arg)
        except Exception as e:
            print('Outer exception', e)
            print('Botometer exception caught')
            BotometerClient.send_notification_email()
