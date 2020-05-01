#!/usr/bin/python3


"""
This script write in not_in.txt the diseases that are not already in Wikidata
"""
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import json
import pickle
import sys
import os

from utils import DeserializeData, SerializeData , correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata

from local import WDUSER, WDPASS

login = wdi_login.WDLogin(WDUSER, WDPASS)

Diseases={}

#indicate the dump file
cellosaurusdump="../project/cellosaurus.txt"

with open(cellosaurusdump, "r") as file:
	for line in file.readlines():
		if line.startswith("DI"):
			disease=line.rstrip("\n").split("   ")[1].split(";")
			if disease[2].strip("  ") not in Diseases:
				Diseases[disease[1].strip("  ")]=disease[2].strip("  ")




cellosaurus=CellosaurusToDictionary(cellosaurusdump)


already=[]
allNCIt=[]

#request Wikidata
query=wdi_core.WDItemEngine.execute_sparql_query("""SELECT distinct ?NCIt WHERE {?item wdt:P1748 ?NCIt.}""")
query=query['results']['bindings']
for result in query:
	NCIt=result['NCIt']['value'].strip("'")
	allNCIt.append(NCIt)

#write informations in not_in.txt
with open ("not_in.txt", "w") as file:
	for celline in cellosaurus:
		for di in cellosaurus[celline]["DI"]:
			if di not in already:
				already.append(di)
				if di not in allNCIt:
					file.write(di+"\t"+Diseases[di]+"\n")

