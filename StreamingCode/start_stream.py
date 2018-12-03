from DataCollection import streaming # TwitterStreamListener
import sys

# Sample call python3 start_stream.py '#maga' '#qanon' '#roseanne'
# Sample call python3 start_stream.py

# Arguments passed in
hashtags = sys.argv[1:]
if hashtags:
    # Filter the stream on the provided hashtags
    if hashtags[0] == 'help':
        print('You can start streaming tweets on hashtags by making the following call with your desired hashtags:')
        print('Sample call python3 start_stream.py \'#maga\' \'#qanon\' \'#roseanne\'')
        print('\n')
        print("You can start streaming tweets without a filter by making the following call:")
        print('Sample call: \'python3 start_stream.py\'')
        print('\n')
        print("You can also pass in an optional time limit in seconds as the last argument:")
        print('Sample call: \'python3 start_stream.py 86400\'')
        print('\n')
    else:
        try:
            time_limit = int(hashtags[-1])
            del hashtags[-1]  # remove time limit from hashtags so it doesn't get put in the file name
            streaming.TwitterStreamListener.start_mining(hashtags, time_limit=time_limit)
            print('Starting stream with ', time_limit, ' second limit!')
        except ValueError:
            # Not an int so no time limit was passed in
            streaming.TwitterStreamListener.start_mining(hashtags)
            print('Starting stream without a time limit!')
else:
    # Take a sample with no filtering
    streaming.TwitterStreamListener.start_mining()
