"""API for data at http://www.theatlantic.com/politics/archive/2016/11/where-republicans-stand-on-donald-trump-a-cheat-sheet/481449/"""
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
import requests
import hug
import re


def get_html() -> str:
    """
    Return the text of the html document.
    """
    corpus = requests.get(
        "http://www.theatlantic.com/politics/archive/2016/11/where-republicans-stand-on-donald-trump-a-cheat-sheet/481449/").text
    return corpus


def get_data_from_html(html: str) -> [dict]:
    """
    Return a list of dictionaries with the data we want
    """

    soup = BeautifulSoup(html, 'lxml')

    strongs = soup.find_all('strong')

    result = []
    for tag in strongs:
        # skip blanks
        if not tag.string: continue
        # skip author's notes
        if 'author' in tag.string.lower(): continue

        name, position = tag.string.split(':')
        position = position.strip()

        if position.startswith('SOFT') or position.lower().startswith('apparent'):
            position = ' '.join(position.split()[:2])
        else:
            position = position.split()[0]

        result.append({'name': name.strip(), 'position': position})

    return result


@hug.get('/republicans', examples="position=nay")
def name(name: hug.types.text = '', position: hug.types.text = ''):
    db = TinyDB('republicans.json')
    Republican = Query()

    name_re = re.compile(name, re.I)
    position_re = re.compile(position, re.I)

    if name and position:
        return ["you must use either name or position"]
    elif name:
        result = db.search(Republican.name.search(name_re))
    elif position:
        result = db.search(Republican.position.search(position_re))
    else:
        result = db.all()

    return {
        "count": len(result),
        "result": result,
    }


if __name__ == '__main__':
    from pprint import pprint

    republicans = get_data_from_html(get_html())

    # database
    db = TinyDB('republicans.json')
    db.purge()
    for r in republicans:
        db.insert(r)

    pprint(db.all())
