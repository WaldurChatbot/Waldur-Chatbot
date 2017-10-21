def text(message):
    return {
        'type': 'text',
        'message': message
    }


def graph(graph_data):
    return {
        'type': 'graph',
        'data': graph_data
    }
