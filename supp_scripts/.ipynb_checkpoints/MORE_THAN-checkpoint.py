#!/usr/bin/python3


"""
This script write in more_than.txt the NCIt id that are referenced more than once in wikidata
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

already={}	

#request Wikidata 
query=wdi_core.WDItemEngine.execute_sparql_query("""#SELECT ?item ?NCIt WHERE {?item wdt:P1748 ?NCIt.}""")
query=query['results']['bindings']
for result in query:
	NCIt=result['NCIt']['value'].strip("'")
	if NCIt in Diseases:
		if NCIt not in already:
			already[NCIt]=[result['item']['value'].strip("'http://www.wikidata.org/entity/")]
		else:
			already[NCIt].append(result['item']['value'].strip("'http://www.wikidata.org/entity/"))

#write the informations in more_than.txt
with open ("more_than.txt", "w") as file:
	for NCIt in already:
		if len(already[NCIt]) > 1 :
			file.write(NCIt+"\t"+Diseases[NCIt]+"\t"+str(already[NCIt])+"\n")


