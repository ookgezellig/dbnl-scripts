import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import json
import urllib.request
import os

################################################################################
# Load downloaded data from DBNL, select relevant entries, and download specific entries.

def load_dbnl_data():
    "Load data from DBNL"
    with open('resources/dbnl.json') as f:
        data = json.load(f)
        for entry in data:
            entry['genres'] = set(entry['genres'])
        return data


def select_entries(data, 
           genres, 
           exact=False, 
           year_start=0, 
           year_end=3000,
           need_epub=True,
           need_pdf=True):
    "Select books from DBNL."
    results = []
    genres = set(genres)
    for entry in data:
        if not genres.issubset(entry['genres']):
            continue
        if exact and not genres == entry['genres']:
            continue
        if need_epub and not 'epub' in entry['download']:
            continue
        if need_pdf and not 'pdf' in entry['download']:
            continue
        # Warning: only works for entries where exact year is specified!
        if not entry['year'].isdigit():
            continue
        if year_start <= int(entry['year']) <= year_end:
            results.append(entry)
    return results


def download(url, folder):
    "Download file to a folder."
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, folder + filename)


def download_entry(entry, folder):
    "Download entry to a folder."
    download(entry['download']['epub'], folder)

################################################################################
# Load text from epub.

def get_text(filename):
    "Get text from an epub file."
    book = epub.read_epub(filename)
    texts = []
    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = doc.content
        soup = BeautifulSoup(content, features="lxml")
        text = soup.text.replace('\n', ' ')
        texts.append(text)
    return(' '.join(texts))

################################################################################
# To deal with SpaCy's tokenization.

def has_pre_space(token):
    """
    Function to check whether a token has a preceding space.
    
    See: https://stackoverflow.com/a/50330877/2899924
    """
    if token.i == 0:
        return False
    if token.nbor(-1).whitespace_:
        return True
    else:
        return False

def detokenize(tokens):
    "Detokenize sequence of SpaCy tokens."
    sentence = []
    for token in tokens:
        if has_pre_space(token):
            sentence.append(' ')
        sentence.append(token.orth_)
    return ''.join(sentence).strip()


# Source: https://stackoverflow.com/a/312464/2899924
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
