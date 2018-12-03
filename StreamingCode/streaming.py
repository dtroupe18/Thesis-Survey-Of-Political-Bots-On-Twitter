from DataCollection import constants
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import csv
import sys
import smtplib


# Create a streamer object
class TwitterStreamListener(StreamListener):

    # Define a function that is initialized when the miner is called
    def __init__(self, hashtags, time_limit=None, api=None):
        super(TwitterStreamListener, self).__init__()
        # That sets the api
        self.api = api

        if time_limit is not None:
            self.has_time_limit = True
            self.start_time = time.time()
            self.time_limit = time_limit
        else:
            self.has_time_limit = False

        hashtag_string = ''

        if hashtags is not None:
            for hashtag in hashtags:
                if hashtag != hashtags[-1]:
                    hashtag_string += '-'
                    hashtag_string += hashtag
                else:
                    hashtag_string += '-'
                    hashtag_string += hashtag
                    hashtag_string += '-'

        # Create a file with 'StreamData' hashtags and the current time
        self.stream_filename = 'StreamData' + hashtag_string + time.strftime('%Y%m%d-%H%M%S') + '.csv'

        # Create a new file with that filename
        stream_file = open(self.stream_filename, 'w')

        # Create a csv writer
        stream_writer = csv.writer(stream_file)

        # Write a single row with the headers of the columns
        stream_writer.writerow(['status_text',
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
                                'user_time_zone'
                                ])

    # When a tweet appears
    def on_status(self, status):

        # Check the time limit
        if self.has_time_limit and (time.time() - self.start_time) > self.time_limit:
            print('Shutting down stream after ', self.time_limit, ' seconds!')
            TwitterStreamListener.send_notification_email()
            # Returning False closes the stream
            return False

        # Open the csv file created previously
        stream_file = open(self.stream_filename, 'a')

        # Create a csv writer
        stream_writer = csv.writer(stream_file)

        hashtags = TwitterStreamListener.parse_hashtags(status.entities['hashtags'])

        try:
            # Write the tweet's information to the csv file
            stream_writer.writerow([status.text,
                                    status.created_at,
                                    status.lang,
                                    status.place,
                                    status.coordinates,
                                    status.id,
                                    status.favorite_count,
                                    status.retweeted,
                                    status.source,
                                    status.favorited,
                                    status.retweet_count,
                                    hashtags,
                                    len(status.entities['hashtags']),
                                    status.entities,
                                    status.user.favourites_count,
                                    status.user.statuses_count,
                                    status.user.description,
                                    status.user.location,
                                    status.user.id,
                                    status.user.created_at,
                                    status.user.verified,
                                    status.user.following,
                                    status.user.url,
                                    status.user.listed_count,
                                    status.user.followers_count,
                                    status.user.default_profile_image,
                                    status.user.utc_offset,
                                    status.user.friends_count,
                                    status.user.default_profile,
                                    status.user.name,
                                    status.user.lang,
                                    status.user.screen_name,
                                    status.user.geo_enabled,
                                    status.user.profile_background_color,
                                    status.user.profile_image_url,
                                    status.user.time_zone
                                    ])

            # print('Added streaming tweet: ', status.text, ' by: ', status.user.name)

        # If some error occurs
        except Exception as e:
            # Print the error
            print(e)
            # and continue
            pass

        # Close the csv file
        stream_file.close()

        return

    # When an error occurs
    def on_error(self, status_code):
        # Print the error code
        print('Encountered error with status code:', status_code)

        # If the error code is 401, which is the error for bad credentials
        if status_code == 401:
            # End the stream
            return False

    # When a deleted tweet appears
    def on_delete(self, status_id, user_id):

        # Print message
        print("Delete notice")

        # Return nothing
        return

    # When reach the rate limit
    def on_limit(self, track):

        # Print rate limiting error
        print("Rate limited, continuing")

        # Continue mining tweets
        return True

    # When timed out
    def on_timeout(self):

        # Print timeout message
        print(sys.stderr, 'Timeout...')

        # Wait 10 seconds
        time.sleep(10)

        # Return nothing
        return

    ####################
    # Static Functions #
    ####################

    @staticmethod
    def parse_hashtags(hashtag_dict):
        if len(hashtag_dict) > 0:
            hashtag_text = ''
            for dictionary in hashtag_dict:
                if 'text' in dictionary:
                    if hashtag_text != '':
                        hashtag_text += ' ' + dictionary['text']
                    else:
                        hashtag_text += dictionary['text']
        else:
            hashtag_text = ''

        return hashtag_text

    # Create a mining function
    @staticmethod
    def start_mining(hashtags=None, time_limit=None):
        """
        :param hashtags: list of strings
        :param time_limit: number of seconds until stream shuts down
        :return: Returns tweets containing those strings.
        """

        # Create a listener
        listener = TwitterStreamListener(hashtags, time_limit)

        # Create authorization info
        auth = OAuthHandler(constants.consumer_key, constants.consumer_secret)
        auth.set_access_token(constants.access_token, constants.access_token_secret)

        # Create a stream object with listener and authorization
        stream = Stream(auth, listener)

        # Run the stream object using the user defined queries
        if hashtags is not None:
            stream.filter(track=hashtags, stall_warnings=True, async=True)
        else:
            stream.sample()

    ######################
    # Email Notification #
    ######################

    @staticmethod
    def send_notification_email():
        # Email myself when the script finishes so I can start on the next set of data
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(constants.email_address, constants.password)

        subject = 'Twitter Stream'
        text = 'Streaming Script Finished!'
        message = 'Subject: {}\n\n{}'.format(subject, text)
        server.sendmail(constants.email_address, constants.real_email, message)
        server.quit()

        return
