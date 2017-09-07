from string import digits
from unicodedata import normalize
import nltk


def create_search_list(search):
    search = search.lower()
    search = search.strip()
    search = remove_accentuation(search)
    search = remove_numbers(search)

    #search_list = get_nouns(search)
    search_list = search.split(' ')

    return search_list


def remove_numbers(text):
    remove_digits = str.maketrans('', '', digits)
    return text.translate(remove_digits)


def remove_accentuation(text):
    return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


def get_nouns(search):
    tokens = nltk.word_tokenize(text=search, language='portuguese')
    tagged = nltk.pos_tag(tokens)

    print("Tagged: " + tagged.__str__())

    final_list = list()

    for tag in tagged:
        if tag[1] == 'NN' or tag[1] == 'VB':
            final_list.append(tag[0])

    return final_list
