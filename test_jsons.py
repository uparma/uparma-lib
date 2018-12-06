#!/usr/bin/env python3
import json
import glob
import os


def main():
    for json_file in glob.glob(os.path.join('.','*.json')):
        print('Testing file: {0}'.format(json_file))
        try:
            json.load(open(json_file,'r'))
            print('\tReading file complete')
        except Exception as e: 
            print('\t[ WARNING ]')
            print('\tError message: {0}'.format(e))
            print('\tCould not read file!')
            print('\t[ WARNING ]')
    return

if __name__ == '__main__':
    main()
