def get_items_post(values, key_word, replace=True):
    items = list()

    for item in values:
        if key_word in item:
            if replace:
                items.append(str.replace(item, key_word, ''))
            else:
                items.append(item)

    return items


def verbose_name(name):
    return str.replace(name, '_', ' ').upper()
