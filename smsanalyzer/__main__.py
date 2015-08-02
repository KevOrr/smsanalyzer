import argparse

import matplotlib.pyplot as plt

from smsanalyzer import TextraDatabase

analysis_funcs = []

def main():
    args = parse_args()
    tdb = TextraDatabase(args.path_or_uri, is_uri=args.is_uri)
    while True:
        for convo in tdb.convos.values():
            print('{:>4} {}'.format(convo._id, convo.display_name))
        print()
        while True:
            try:
                convo_id = int(input('Select a conversation (0 to exit): '))
            except ValueError:
                print('Please enter an integer')
                continue
            if convo_id == 0:
                return
            elif convo_id < 0 or convo_id not in tdb.convos:
                print('Please enter either 0 or a valid conversation id number')
            else:
                convo = tdb.convos[convo_id]
                break
        for i, func in enumerate(analysis_funcs):
            print('{:>2} {}'.format(i+1, func.__name__))
        print()
        while True:
            try:
                func_id = int(input('Select a function (0 to exit): '))
            except ValueError:
                print('Please enter an integer')
                continue
            if func_id == 0:
                return
            elif func_id < 0 or func_id > len(analysis_funcs):
                print('Please enter either 0 or a valid function number')
            else:
                func = analysis_funcs[i-1]
                break
        if func(convo):
            return
        
    
def parse_args():
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
    return args

def analysis(func):
    analysis_funcs.append(func)
    return func

@analysis
def analyze_response_times(convo, bins=50, lower=0, upper=None, histtype='bar', log=False,
                           colors=None, grid=True):
    inbound, outbound = [], []
    min_time = lambda a,b: a or b if not (a and b) else max(a,b)
    last_direction = convo.messages[0].direction
    #last_time =  max(convo.messages[0].ts, convo.messages[0].message_center_ts)
    last_time = convo.messages[0].ts
    for m in sorted(convo.messages[1:], key=lambda mess:mess.ts):
        if m.direction == last_direction:
            last_time = m.ts
            continue
        else:
            ts = max(m.ts, m.message_center_ts)
            [inbound, outbound][m.direction].append(m.ts - last_time)
            last_direction, last_time = m.direction, m.ts
    if lower is None:
        lower = min(inbound + outbound)
    if upper is None:
        upper = max(inbound + outbound)
    bins, edges, patches = plt.hist([inbound, outbound], bins, (lower, upper),
                                    histtype=histtype, log=log, color=colors,
                                    label=(convo.display_name[:20], 'You'))
    print(sorted(outbound)[:200])
    #print(bins)
    #print(edges)
    return True
    plt.xlabel('Response Time')
    plt.ylabel('Count')
    plt.title('Your vs {}\'s Response Times'.format(convo.display_name[:30]))
    plt.axis([lower, upper, 0, max(bins[0] + bins[1])])
    plt.grid(grid)
    plt.show()

main()

