#!/usr/bin/env python3

import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize, scipy.special

analysis_funcs = []

def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2*sigma**2))

def chi2(x, df, a, b):
    x = x / b
    return a / (2**(df/2) * scipy.special.gamma(df/2)) * (x)**(df/2-1) * np.exp(-x/2)

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
    x = np.linspace(lower, upper, 500)
    bin_centers = (edges[1:] + edges[:-1])/2
    center = (upper+lower)/2
    try:
        inbound_params, _ = scipy.optimize.curve_fit(chi2, bin_centers, hist[0], p0=(2, max(hist[0]), center))
    except (scipy.optimize.OptimizeWarning, RuntimeError) as e:
        warnings.warn(e.args[0], scipy.optimize.OptimizeWarning, 2)
    else:
        inbound_y = chi2(x, *inbound_params)
        plt.plot(x, inbound_y, colors[0] + '-')

    try:
        outbound_params, _ = scipy.optimize.curve_fit(chi2, bin_centers, hist[1], p0=[2, max(hist[1]), center])
    except (scipy.optimize.OptimizeWarning, RuntimeError) as e:
        warnings.warn(e.args[0], scipy.optimize.OptimizeWarning, 2)
    else:
        outbound_y = chi2(x, *outbound_params)
        plt.plot(x, outbound_y, colors[1] + '-')

    # Configure decorations and show plot
    plt.xlabel('Response Time')
    plt.ylabel('Count')
    plt.title('Your vs {}\'s Response Times'.format(convo.display_name[:30]))
    plt.axis((lower, upper, 0, 1.2 * max(max(hist[0]), max(hist[1]))))
    plt.grid(grid)
    plt.legend()
    plt.show()

