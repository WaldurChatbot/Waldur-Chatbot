
def obscure(item, start=3, end=3):
    """
    Replaces middle of string with *
    :param item: string - to be obscured string
    :param start: int - how many letters to leave from start
    :return: obscured string - how many letters to leave from end
    """
    # ignore None
    if item is None:
        return None

    total_length = len(str(item))
    removed_length = start + end

    if removed_length > total_length:
        return item
    else:
        return item[:start] + "*"*(total_length-removed_length) + item[-end:]
