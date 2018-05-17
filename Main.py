#!/Users/leliadebornes/anaconda3/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import json
import pickle
import sys
import os
from src.utils import DeserializeData, SerializeData , correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata

from src.local import WDUSER, WDPASS

#login with your Wikidata user and password in local.py
login = wdi_login.WDLogin(WDUSER, WDPASS)

#-----------------INPUT-------------------------#

if len(sys.argv) <=3 and len(sys.argv) > 1 :

	#check if wikidata release item exist
	if wdi_core.WDItemEngine.get_wd_search_results(search_string=sys.argv[1]) != []:
		release=wdi_core.WDItemEngine(wd_item_id=sys.argv[1]).get_label()

		#ask if user want to upload Cellosaurus dump if the file is not done
		if len(sys.argv) == 2 :
			download= input("------------------- Would you download a Cellosaurus dump?(y/n) -------------------")
			if download == "y":
				os.system("wget -O ./project/cellosaurus.txt ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt ")
				cellosaurus=CellosaurusToDictionary("project/cellosaurus.txt")
			elif download =='n':
				print("------------------- Give a Cellosaurus dump in second argument -------------------")
			else:
				print("------------------- Answer by y or n -------------------")

		#if the cellosaurus dump is done, check if it could be open
		elif len(sys.argv) == 3 :
			try :
				cellosaurus=CellosaurusToDictionary(sys.argv[2])
			except FileNotFoundError:
				print("------------------- Cellosaurus file could not be open -------------------")
		

		#contains the cell lines items with a Cellosaurus ID
		wikidata=QueryingWikidata()

		correspondance=correspondance(cellosaurus)

		#-----------------SPECIES-------------------------#
		#contains all wikidata species items with a NCBI Taxonomy id
		species=correspondance["species"]


		#-----------------REFERENCES-------------------------#
		#contains all wikidata references with PubMed or DOI id
		references=correspondance["references"]
		

		#-----------------CATEGORIES-------------------------#
		#contains all the cellosaurus categories and their wikidata item id
			#associated
		categories=categories("/project/categories.txt")

		#-----------------DISEASES-------------------------#
		#contains all wikidata items with NCI thesaurus id
		diseases=correspondance["diseases"]
		#if disease items in wikidata have the same NCI thesaurus id, they are
			#written in /doc/ERRORS/diseases/more_than_1.txt
		with open ("./doc/ERRORS/diseases/more_than_1.txt", "w") as file:
			for duplicate in correspondance["problematicdiseases"]:
				file.write(duplicate+"\t"+str(correspondance["problematicdiseases"][duplicate])+"\n")


		



	else:
		print("------------------- Give the Wikidata ID for the release (form Q*****) in 1st argument -------------------")

	
else:
	print("------------------- You have to give the Wikidata ID for the Cellosaurus release -------------------")
"""


cellosaurus=CellosaurusToDictionary("cellosaurus.txt")
SerializeData(cellosaurus, "cellosaurus.pickle")

#cellosaurus=DeserializeData("cellosaurus.pickle")

#wikidata=DeserializeData("wikidata.pickle")
wikidata=QueryingWikidata()

correspondance=correspondance(cellosaurus)
#pprint(correspondance['errorreferences'])

#species=DeserializeData("species.pickle")
#species=correspondance["species"]
#SerializeData(species, "species.pickle")

#references=DeserializeData("references.pickle")
#references=correspondance["references"]
#SerializeData(references, "references.pickle")

#category.txt contains all the cellosaurus categories and their wikidata item id associated.
#categories=categories("category.txt")

#diseases_name={}
#for celline in cellosaurus:
#	if cellosaurus[celline]["DI"] != []:
#		for disname in cellosaurus[celline]["DI_names"]:
#			diseases_name[disname]=cellosaurus[celline]["DI_names"][disname]
#pprint(diseases_name)
#SerializeData(diseases_name, "diseasesname.pickle")

diseases_name=DeserializeData("diseasesname.pickle")


#diseases=DeserializeData("diseases.pickle")
#diseases=correspondance["diseases"]
#SerializeData(diseases, "diseases.pickle")


#problematicdiseases=DeserializeData("problematicdiseases.pickle")
problematicdiseases=correspondance["problematicdiseases"]
SerializeData(problematicdiseases, "problematicdiseases.pickle")

with open ("more_than_1.txt", "w") as file:
	for disease in problematicdiseases:
		if disease in diseases_name:
			file.write(disease+"\t"+diseases_name[disease]+"\t"+str(problematicdiseases[disease])+"\n")

supp={}
with open ("not_in.txt", "w") as file:
	for celline in cellosaurus:
		if cellosaurus[celline]["DI"] != []:
			for disease in cellosaurus[celline]["DI"]:
				if disease not in diseases and disease not in problematicdiseases:
					if disease not in supp:
						supp[disease]="s"
						file.write(disease+"\t"+diseases_name[disease]+"\n")






#notreferencing=DeserializeData("notreferencing.pickle")
#print(len(notreferencing))
#notreferencing=correspondance['referencesniw']
#SerializeData( notreferencing, "notreferencing.pickle")




#à voir quoi faire avec correspondance["referencesniw"] et correspondance["problematicspecies"]


"""
"""
Création de l'objet Create_Update
-> Prendra en sysargv[1] l'id de l'item wikidata corrrespondant à la release
Ici relsease 25 (Q50346976)

"""
"""
Release=Create_Update(login=login, releaseID="Q50346976", cellosaurus=cellosaurus, wikidata=wikidata, references=references, species=species, categories=categories, diseases=diseases)

update={}
create=[]
problematic={}
delete={}
#CVCL_1048 = Q52155313 = 638V => à updater

#for cell_line in Release.cellosaurus:
# POUR FAIRE TOURNER SUR TOUTES LES CELLINES
cell_line="CVCL_1049"

if cell_line in Release.wikidata and cell_line not in update:
	print("update")
	update[cell_line]=wikidata[cell_line]
	Release.UpdateWikidata(cell_line, Release.InitialisationData(cell_line))

elif cell_line in Release.wikidata and cell_line in update:
	print("problematic")
	problematic[wikidata[cell_line]]="2 or more items for 1 cell line"

else:
	print("create")
	create.append(cell_line)
	Release.InsertionWikidata(cell_line, Release.InitialisationData(cell_line))


for cell_line in Release.wikidata:
	if cell_line not in Release.cellosaurus:
		delete[cell_line]=wikidata[cell_line]


"""


#pour updater les lignées dont les items pour les parents et les autoloous n'étaient pas créés. 

#Release.wikidata=QueryingWikidata()
#mettre à jour le contenu de Wikidata

#for cell_line in Release.AddParentCelline:
#	Release.UpdateWikidata(cell_line, Release.InitialisationData(cell_line))




