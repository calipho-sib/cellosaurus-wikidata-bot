#!/usr/bin/python3


"""
This script write in Wikidiseases.txt for each NCIt found in Wikidata:
	- the NCI thesaurus id found in Cellosaurus
	- the name of the disease found in Cellosaurus
	- the Wikidata item id which reference the NCI thesaurus id
	- the label of this Wikidata item
	- all the NCIt referenced in the Wikidata item
	- the value of the property "instance of" of this item
	- the value of the property "subclass of" of this item

example for a disease:
C2975	NCIT:Cystic fibrosis	Q178194	Wiki:cystic fibrosis	['C2975']	instanceof=['disease']	subclassof=['autosomal recessive disease']
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


#indicate the dump file of Cellosaurus
cellosaurus=CellosaurusToDictionary("../project/cellosaurus.txt")

cellosaurus_disease=[]
cellosaurus_names={}

#recover the disease name in Cellosaurus
for cell_line in cellosaurus:
	for disease in cellosaurus[cell_line]["DI"]:
		cellosaurus_disease.append(disease)
	for names in cellosaurus[cell_line]["DI_names"]:
		cellosaurus_names[names]=cellosaurus[cell_line]["DI_names"][names]



instanceofdico={}
subclassofdico={}


#request Wikidata for recover all the informations
query=wdi_core.WDItemEngine.execute_sparql_query("""SELECT DISTINCT ?item ?itemLabel ?NCIt ?instanceof ?instanceofLabel ?subclassof ?subclassofLabel WHERE {
  ?item wdt:P1748 ?NCIt.
  OPTIONAL{?item wdt:P31 ?instanceof.}
  OPTIONAL{?item wdt:P279 ?subclassof.}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}""")
query=query['results']['bindings']

#write the informations in the file Wikidiseases.txt
with open ("Wikidiseases.txt", "w") as file:
	for disease in query:
		allNCIt=[]
		NCIt=disease['NCIt']['value'].strip("'")
		wikiitem=disease['item']['value'].strip("'").strip("http://www.wikidata.org/entity/")
		itemname=disease['itemLabel']['value'].strip("'")
		if 'instanceofLabel' in disease:
			instanceof=disease['instanceofLabel']['value'].strip("'")
			
			if NCIt in instanceofdico:
				instanceofdico[NCIt].append(instanceof)
			else:
				instanceofdico[NCIt]=[instanceof]
		else:
			if NCIt in instanceofdico:
				instanceofdico[NCIt].append("NULL")
			else:
				instanceofdico[NCIt]=["NULL"]

		if 'subclassofLabel' in disease:
			subclassof=disease['subclassofLabel']['value'].strip("'")
			if NCIt in subclassofdico:
				subclassofdico[NCIt].append(subclassof)
			else:
				subclassofdico[NCIt]=[subclassof]
		else:
			if NCIt in subclassofdico:
				subclassofdico[NCIt].append("NULL")
			else:
				subclassofdico[NCIt]=["NULL"]

		if NCIt in cellosaurus_disease:
			query2=wdi_core.WDItemEngine.execute_sparql_query("""SELECT ?NCIt WHERE { wd:"""+wikiitem+""" wdt:P1748 ?NCIt }""")
			query2=query2['results']['bindings']
			for nc in query2:
				allNCIt.append(nc['NCIt']['value'].strip("'"))
			file.write(NCIt+"\t"+"NCIT:"+cellosaurus_names[NCIt]+"\t"+wikiitem+"\t"+"Wiki:"+itemname+"\t"+str(allNCIt)+"\t"+"instanceof="+str(instanceofdico[NCIt])+"\t"+"subclassof="+str(subclassofdico[NCIt])+"\n")

