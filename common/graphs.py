import json
import matplotlib.pyplot as plt
import numpy as np
import io
from logging import getLogger

log = getLogger(__name__)


# todo we should make this like requests

def make_graph(data):
    log.debug(data)

    plotx = data['x']
    ploty = data['y']
    log.debug("x: {}".format(plotx))
    log.debug("y: {}".format(ploty))

    N = len(ploty)

    ind = np.arange(N)
    width = 0.35
    fig, ax = plt.subplots()

    rects1 = ax.bar(ind, ploty, width, color='#2388d6')

    ax.set_xlabel('Months')
    ax.set_ylabel('Total costs')
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(plotx)
    ax.set_title('Last ' + str(N) + ' months total costs')

    autolabel(rects1, ax)

    # plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return buf

def autolabel(rects, ax):
    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()
        label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width() / 2., label_position,
                '%d' % int(height),
                ha='center', va='bottom')