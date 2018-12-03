import sys
import os.path
import pandas as pd
import time

length = len(sys.argv)

if length != 2:
    print('You must provide the file name for the csv you want to split!')
    exit(1)
else:
    file_name = sys.argv[1]
    print(file_name)

    if os.path.isfile(file_name):
        print('I found your csv file. Starting to spilt into smaller pieces...')
        time.sleep(1)
        for i, chunk in enumerate(pd.read_csv(file_name, chunksize=100000, header=0, error_bad_lines=False)):
            chunk.to_csv(file_name + '-Part-{}.csv'.format(i))

    else:
        print('I could not find your file. Please check to make sure you typed the name correctly.')
        exit(1)

