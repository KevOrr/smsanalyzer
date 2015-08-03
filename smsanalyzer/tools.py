#!/usr/bin/env python3

import warnings

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy.optimize, scipy.special
except ImportError:
    warnings.warn('Without numpy, scipy, and matplotlib, you won\'t be able to run any of the visualize_* functions', ImportWarning)

try:
    import seaborn
except ImportError:
    warnings.warn('I recommend installing the package seaborn, it really makes pyplot plots look nicer', ImportWarning)
else:
    seaborn.set()

analysis_funcs = []

def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2*sigma**2))

def chi2(x, df, a, b):
    x = x / b
    return a / (2**(df/2) * scipy.special.gamma(df/2)) * (x)**(df/2-1) * np.exp(-x/2)

def plot_compute_fit(func, x, y, p0, domain, color):
    try:
        params, _ = scipy.optimize.curve_fit(func, x, y, p0)
    except (scipy.optimize.OptimizeWarning, RuntimeError) as e:
        warnings.warn(e.args[0], scipy.optimize.OptimizeWarning, 2)
    else:
        fit_y = func(domain, *params)
        plt.plot(domain, fit_y, color)

def analysis(func):
    analysis_funcs.append(func)
    analysis_funcs.sort(key=lambda f: f.__name__)
    return func

@analysis
def visualize_response_times(convo, bins=50, lower=0, upper=600, log=False, colors='rb', grid=True):
    # Calculate response times
    inbound, outbound = [], []
    # min_time = lambda a,b: a or b if not (a and b) else max(a,b)
    last_direction = convo.messages[0].direction
    # last_time =  max(convo.messages[0].ts, convo.messages[0].message_center_ts)
    last_time = convo.messages[0].ts
    for m in sorted(convo.messages[1:], key=lambda mess:mess.ts): # sorted "just in case"
        if m.direction == last_direction:
            last_time = m.ts
            continue
        else:
            ts = max(m.ts, m.message_center_ts)
            [inbound, outbound][m.direction].append((m.ts - last_time)/1000)
            last_direction, last_time = m.direction, m.ts

    # Calculate bounds if not given explicitly necessary
    if lower is None:
        lower = min(inbound + outbound)
    if upper is None:
        upper = max(inbound + outbound)

    # Plot histogram
    hist, edges, patches = plt.hist([inbound, outbound], bins, (lower, upper), histtype='bar', log=log,
                                    color=colors, alpha=0.5, label=(convo.display_name[:20], 'You'))

    # Compute and plot Chi2 fit
    domain = np.linspace(lower, upper, 500)
    bin_centers = (edges[1:] + edges[:-1])/2
    center = (upper+lower)/2
    plot_compute_fit(chi2, bin_centers, hist[0], [2, max(hist[0]), center], domain, colors[0] + '-')
    plot_compute_fit(chi2, bin_centers, hist[1], [2, max(hist[1]), center], domain, colors[1] + '-')

    # Configure decorations and show plot
    plt.xlabel('Response Time')
    plt.ylabel('Count')
    plt.title('Your vs {}\'s Response Times'.format(convo.display_name[:30]))
    plt.axis((lower, upper, 0, 1.2 * max(max(hist[0]), max(hist[1]))))
    plt.grid(grid)
    plt.legend()
    plt.show()

@analysis
def visualize_message_length(convo, bins=50, lower=0, upper=250, log=False, colors='rb', grid=True):
    inbound = [len(mess.text) for mess in convo.messages if mess.text and mess.direction == 0]
    outbound = [len(mess.text) for mess in convo.messages if mess.text and mess.direction == 1]

    # Calculate bounds if not given explicitly necessary
    if lower is None:
        lower = min(inbound + outbound)
    if upper is None:
        upper = max(inbound + outbound)

    # Plot histogram
    hist, edges, patches = plt.hist([inbound, outbound], bins, (lower, upper), histtype='bar', log=log,
                                    color=colors, alpha=0.5, label=(convo.display_name[:20], 'You'))

    # Compute and plot Chi2 fit
    domain = np.linspace(lower, upper, 500)
    bin_centers = (edges[1:] + edges[:-1])/2
    center = (upper+lower)/2
    plot_compute_fit(chi2, bin_centers, hist[0], [2, max(hist[0]), center], domain, colors[0] + '-')
    plot_compute_fit(chi2, bin_centers, hist[1], [2, max(hist[1]), center], domain, colors[1] + '-')

    # Configure decorations and show plot
    plt.xlabel('Message Length (Characters)')
    plt.ylabel('Count')
    plt.title('Your vs {}\'s Message Lengths'.format(convo.display_name[:30]))
    plt.axis((lower, upper, 0, 1.2 * max(max(hist[0]), max(hist[1]))))
    plt.grid(grid)
    plt.legend()
    plt.show()

@analysis
def get_lol_count_per_message(convo):
    inbound, outbound = [], []
    for message in convo.messages:
        count = 0
        if not message.text:
            continue
        for word in message.text.lower().split():
            if (word.startswith('lol') or word.endswith('lol')) and ''.join(filter(str.isalpha, word)) == 'lol':
                count += 1
        (inbound, outbound)[message.direction].append(count)
    avg_in = sum(inbound)/len(inbound)
    avg_out = sum(outbound)/len(outbound)

    print('{}: {}\nYou: {}\n'.format(convo.display_name, avg_in, avg_out))

@analysis
def get_lol_count_per_word(convo):
    inbound, outbound = [], []
    for message in convo.messages:
        count = 0
        total = 0
        if not message.text or not message.text.lower().split(): # No body or 0 words
            continue
        for word in message.text.lower().split():
            total += 1
            if (word.startswith('lol') or word.endswith('lol')) and ''.join(filter(str.isalpha, word)) == 'lol':
                count += 1
        (inbound, outbound)[message.direction].append(count/total)
    avg_in = sum(inbound)/len(inbound)
    avg_out = sum(outbound)/len(outbound)

    print('{}: {}\nYou: {}\n'.format(convo.display_name, avg_in, avg_out))

@analysis
def visualize_mime_types(convo, margin=0.05, colors='rb'):
    # Get mime type names
    types = sorted(set(m.part_content_type for m in convo.messages) - set([None]))
    n = len(types)

    # Count occurences
    inbound, outbound = [0 for i in range(n)], [0 for i in range(n)]
    for message in convo.messages:
        if message.part_content_type is not None:
            (inbound, outbound)[message.direction][types.index(message.part_content_type)] += 1

    # Plot bar charts
    ind = np.arange(n)
    width = (1 - 2*margin)/2
    plt.bar(ind + margin, inbound, width, color=colors[0], alpha=0.6, label=convo.display_name[:20])
    plt.bar(ind + margin + width, outbound, width, color=colors[1], alpha=0.6, label='You')

    # Configure decorations and show plot
    plt.xlabel('Mime Type')
    plt.ylabel('Count')
    plt.title('Your vs {}\'s MMS Mime Types'.format(convo.display_name[:30]))
    plt.xticks(ind + 0.5, types)
    plt.gca().xaxis.grid(False)
    plt.gca().yaxis.grid(True)
    plt.legend()
    plt.show()
