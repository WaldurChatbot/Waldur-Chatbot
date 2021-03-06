import json
import matplotlib

matplotlib.use('Agg')  # requirement of matplotlib

import matplotlib.pyplot as plt
from textwrap import wrap
import numpy as np
import io
from logging import getLogger

log = getLogger(__name__)


def make_graph(data):
    if data['graphID'] == 1:
        return totalCostsBarGraph(data)


def totalCostsBarGraph(data):
    plotx = data['x']
    ploty = data['y']

    log.debug(data)
    log.debug("x: {}".format(plotx))
    log.debug("y: {}".format(ploty))

    N = len(ploty)

    ind = np.arange(N)
    width = 0.35

    plt.style.use('ggplot')
    fig, ax = plt.subplots()

    rects1 = ax.bar(ind, ploty, width, color='#75ad58')  # 2388d6

    ax.set_xlabel('Months')
    ax.set_ylabel('Total costs')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(plotx)
    title = ax.set_title("\n".join(wrap('Last ' + str(N) + ' months total costs for \n' + data['org_name'], 60)))

    autolabel(rects1, ax)

    counter = 0
    for child in ax.get_children():
        counter += 1
        if counter == N:
            child.set_color('#2388d6')
            break

    real_invoice = matplotlib.patches.Patch(color='#75ad58', label='Invoice')
    estimate_invoice = matplotlib.patches.Patch(color='#2388d6', label='Estimation')
    plt.legend(handles=[real_invoice, estimate_invoice])

    fig.tight_layout()
    title.set_y(1.05)
    fig.subplots_adjust(top=0.8)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return buf


def autolabel(rects, ax):
    """
    Labels the bars of bar graph with the value of the bars
    A helper function from the internet
    :param rects: bars of the graph
    :param ax: axes of the graph
    """
    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()
        label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width() / 2., label_position,
                '%d' % int(height),
                ha='center', va='bottom')
