import requests
import urllib
import time

query = "SELECT ?person ?personLabel WHERE {?person (wdt:P22|wdt:P25|wdt:P40) wd:Q543880 SERVICE wikibase:label { bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. } }"
urlquery = urllib.parse.quote(query)

headers = {'Accept': 'application/sparql-results+json'}
r = requests.get("https://query.wikidata.org/sparql?query=" + urlquery, headers=headers)

result = r.json()
print(result)