import argparse

from smsanalyzer import TextraDatabase

parser = argparse.ArgumentParser(description='Analyze a Textra messaging.db database')
parser.add_argument('-u', '--is-uri', dest='is_uri', action='store_const',
                    const=True, default=False,
                    help='path_or_uri is a url (http://www.sqlite.org/uri.html)')
parser.add_argument('-f', '--is-file', dest='is_file', action='store_const',
                    const=True, default=None,
                    help='path_or_uri is a path to a file (default)')
parser.add_argument('path_or_uri')
args = parser.parse_args()

if args.is_file and args.is_uri:
    e = ValueError('Please only supply either -u or -f, not both')
    raise e

tdb = TextraDatabase(args.path_or_uri, uri=args.is_uri)

