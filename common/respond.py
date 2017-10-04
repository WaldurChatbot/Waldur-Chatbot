

def ok(message):
    return _base('ok', message)


def error(message):
    return _base('error', message)


def _base(status, message):
    return {
        'status': status,
        'message': message
    }
