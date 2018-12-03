import sys
import glob
import os


def combine_csv_files(csv_file_names):
    header_saved = False
    output_filename = create_filename(csv_file_names)

    with open(output_filename, 'w') as fout:
        for filename in csv_file_names:
            with open(filename) as fin:
                header = next(fin)
                if not header_saved:
                    fout.write(header)
                    header_saved = True
                for line in fin:
                    fout.write(line)

    print('Successfully merged your csv files.\nYour files name is: ', output_filename)
    return


def create_filename(csv_file_names):
    if len(csv_file_names) > 1:
        csv_file_names.sort()
        # Get the starting time from the first file and last file
        first = csv_file_names[0]
        first = first[:-4]
        last = csv_file_names[-1]
        last = last[-19:]
        name = 'MERGED-' + first + '-to-' + last
    else:
        # Only one file prefix with COPY
        name = 'COPY-' + csv_file_names[0]

    return name


def get_csv_file_names(prefix=None):
    # File names to return
    file_names = []
    # Get the current directory
    path = os.path.dirname(os.path.abspath(__file__))
    extension = 'csv'
    os.chdir(path)
    # Grab all csv files
    results = [i for i in glob.glob('*.{}'.format(extension))]
    results.sort()

    if results:
        if prefix:
            print('\nI found the following csv files with prefix: ', prefix, 'to combine...')

            for result in results:
                if result.startswith(prefix):
                    file_names.append(result)
                    print(result)
        else:
            print("\nI found the following csv files to combine...")
            for result in results:
                file_names.append(result)
                print(result)
    else:
        if prefix:
            print('ERROR: no csv files with prefix: ', prefix, ' found!')
        else:
            print('ERROR: no csv files found!')

    return file_names


length = len(sys.argv)
if length != 2:
    file_names = get_csv_file_names()

    if file_names:
        response = input('This script will combine all of the above csv files.'
                         ' Is this what you want to do? [Yes] or [No] ?\n')
        if response == 'yes' or response == 'Yes' or response == 'y' or response == 'Y':
            print('Starting....')
            combine_csv_files(file_names)
        else:
            print('Stopping...')
    else:
        exit(1)
else:
    arg = sys.argv[1]
    print('You entered the prefix: ', arg)
    print('I found the following csv files with that prefix')
    # Find all the csv files with that prefix
    file_names = get_csv_file_names(arg)

    if file_names:
        variable = input('This script will combine all of the above csv files.'
                         ' Is this what you want to do? [Yes] or [No] ?\n')
        if variable == 'yes' or variable == 'Yes' or variable == 'y' or variable == 'Y':
            print('Starting....')
            combine_csv_files(file_names)
        else:
            print('Stopping...')
    else:
        exit(1)



