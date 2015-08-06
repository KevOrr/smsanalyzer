#!/usr/bin/env python3

import argparse

from smsanalyzer import TextraDatabase
from smsanalyzer.tools import analysis_funcs

def main():
    args = parse_args()
    tdb = TextraDatabase(args.path_or_uri, is_uri=args.is_uri)
    while True:
        convo = select_convo(tdb.convos)
        if convo is False:
            return
        while True:
            func = select_analysis_func()
            if func is False:
                break
            func(convo)

def parse_args():
    parser = argparse.ArgumentParser(description='Analyze a Textra messaging.db database')
    parser.add_argument('-u', '--is-uri', dest='is_uri', action='store_const',
                        const=True, default=False,
                        help='path_or_uri is a url (http://www.sqlite.org/uri.html)')
    parser.add_argument('-f', '--is-file', dest='is_file', action='store_const',
                        const=True, default=None,
                        help='path_or_uri is a path to a file (default)')
    parser.add_argument('path_or_uri', default=None, nargs='?')
    args = parser.parse_args()

    if args.is_file and args.is_uri:
        e = ValueError('Please only supply either -u or -f, not both')
        raise e
    return args

def select_convo(convos):
    for convo in convos.values():
        print('{:>4} {}'.format(convo._id, convo.display_name))
    print()
    while True:
        try:
            convo_id = int(input('Select a conversation (0 to exit): '))
            print()
        except ValueError:
            print('Please enter an integer\n')
            continue
        if convo_id == 0:
            return False
        elif convo_id < 0 or convo_id not in convos:
            print('Please enter either 0 or a valid conversation id number')
        else:
            return convos[convo_id]

def select_analysis_func():
    for i, func in enumerate(analysis_funcs):
        print('{:>2} {}'.format(i+1, func.__name__))
    print()
    while True:
        try:
            func_id = int(input('Select a function (0 to return to conversation selection): '))
            print()
        except ValueError:
            print('Please enter an integer\n')
            continue
        if func_id == 0:
            return False
        elif func_id < 0 or func_id > len(analysis_funcs):
            print('Please enter either 0 or a valid function number')
        else:
            return analysis_funcs[func_id-1]

main()
