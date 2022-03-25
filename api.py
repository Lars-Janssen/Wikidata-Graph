from __future__ import annotations

import time
import urllib

import requests


def fetch(root, generations):
    """
        root: the person for which relatives are searched
        generations: the amount of generation to be searched

        Fetches the relatives within a certain generations of root
        by querying wikidata.
    """
    # Gets the query to use
    query = getString(root, generations)
    urlquery = urllib.parse.quote(query)

    # Gets the result of the query and the time it took
    headers = {'Accept': 'application/sparql-results+json'}
    t = time.time()
    r = requests.get(
        'https://query.wikidata.org/sparql?query=' + urlquery, headers=headers,
    )
    queryTime = time.time() - t
    items = []

    # Return error if the query failed
    if r.status_code == 429:
        print(r.text)
        print(r.status_code)
        items.append(queryTime)
        return items

    result = r.json()
    items.append(queryTime)

    # Saves all names and wikidata codes of all the resulting people
    for i in range(len(result['results']['bindings'])):
        urls = []
        names = []
        codes = []

        for j in range(generations):
            urls.append(
                result['results']['bindings']
                [i]['person' + str(j)]['value'],
            )
            names.append(
                result['results']['bindings'][i]
                ['person' + str(j) + 'Label']['value'],
            )
            codes.append(urls[j].split('/')[-1])

        items.append([codes, names])

    # Returns the queryTime, names and codes.
    return items


def getString(root, generations):
    """
        root: the person for which relatives are searched
        generations: the amount of generation to be searched

        Generates the query to be used.
    """
    persons = ''
    for i in range(generations):
        persons += ' ?person' + str(i)

    for i in range(generations):
        persons += ' ?person' + str(i) + 'Label'

    lines = ''
    for i in range(1, generations):
        lines += '?person' + \
            str(i - 1) + ' (wdt:P22|wdt:P25|wdt:P40) ?person' + str(i) + '. '

    return 'SELECT ' + persons + ' WHERE {wd:' + root + '\
    (wdt:P22|wdt:P25|wdt:P40) ?person0.' + lines + " SERVICE wikibase:label\
    { bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. } }"
