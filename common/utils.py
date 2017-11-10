
def obscure(item, start=3, end=3):
    """
    Replaces middle of string with *
    :param item: string - to be obscured string
    :param start: int - how many letters to leave from start
    :return: obscured string - how many letters to leave from end
    """
    total_length = len(item)
    removed_length = start + end

    if removed_length > total_length:
        return item
    else:
        return item[:start] + "*"*(total_length-removed_length) + item[-end:]
