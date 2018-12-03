import botometer, constants
import sys
import os
import pandas as pd


class BotometerClient:

    def __init__(self, filename):

        self.bot_meter = botometer.Botometer(wait_on_ratelimit=True,
                                             mashape_key=constants.mashape_key,
                                             **constants.botometer_auth)

        self.master_file_name = 'MasterIDs.csv'
        # Store all the ids we get an error on so they aren't checked again
        self.error_ids_file_name = 'ErrorIDs.csv'
        self.unique_ids_file_name = 'UniqueIDs.csv'

        self.streaming_file_name = filename
        self.tweepy_api = constants.api

        self.error_df = BotometerClient.load_error_ids_df(self.error_ids_file_name)
        self.master_df = BotometerClient.load_master_ids_df(self.master_file_name)
        self.get_new_ids()
        return

    def get_new_ids(self):
        if self.streaming_file_name is None or self.master_df is None or self.error_df is None:
            print("Streaming file name, master_df or error_df is NONE!")
            return

        # Load streamingData from csv
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + self.streaming_file_name

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

        # Drop all ids that are already in master_df
        master_id_list = self.master_df.user_id.tolist()
        df = df[~df.user_id.isin(master_id_list)]

        print('Out of ', unique_size, ' there were ', (unique_size - len(df)), ' ids that already have scores')

        print('Error DF cols: ', list(self.error_df.columns.values))

        error_id_list = self.error_df['user_id\r'].tolist()
        df = df[~df.user_id.isin(error_id_list)]

        print('After removing error ids we have ', len(df), ' ids to check!')

        # Drop any rows that are missing the required columns
        size_before_drop = len(df)
        df.dropna(subset=['status_text', 'status_created_at', 'user_id', 'stream_tweet_count'])

        print('Dropped', (size_before_drop - len(df)), 'rows with missing data!')
        print('Collecting bot scores for ', len(df), ' new ids')
        file_name = 'New-IDS-From-' + self.streaming_file_name + '.csv'
        df.to_csv(file_name, encoding='utf-8', index=False)
        return

    ###########################
    # Start of static methods #
    ###########################

    @staticmethod
    def load_master_ids_df(master_file_name):
        # Read in MasterIDs and remove any values in there from our data frame
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + master_file_name
        master_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        return master_df

    @staticmethod
    def load_error_ids_df(error_ids_file_name):
        # Read in Error IDs and remove any values already created
        path = os.path.dirname(os.path.abspath(__file__)) + '/' + error_ids_file_name
        error_df = pd.read_csv(path, header=0, low_memory=False, error_bad_lines=False, lineterminator='\n')

        return error_df

    #################################
    # One function to rule them all #
    #################################
    @staticmethod
    def start_mining(file_name):
        print('\nStarting Botometer mining...')

        # Check if the desired csv file exists
        if os.path.isfile(file_name):
            print('\nStreaming data found')
            BotometerClient(file_name)

        else:
            print('Error: requested csv file does not exist!')
            return


length = len(sys.argv)
if length != 2:
    print('Error: please provide a streaming csv file name')
elif length == 2:
    arg = sys.argv[1]
    try:
        BotometerClient.start_mining(arg)
    except Exception as e:
        print('outer exception', e)
        print('Botometer exception caught')

