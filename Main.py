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

		#correspondance=correspondance(cellosaurus)
		#SerializeData(correspondance, "correspondance.pickle")
		correspondance=DeserializeData("correspondance.pickle")
		

		#-----------------SPECIES-------------------------#
		#contains all wikidata species items with a NCBI Taxonomy id
		species=correspondance["species"]


		#-----------------REFERENCES-------------------------#
		#contains all wikidata references with PubMed or DOI id
		references=correspondance["references"]
		

		#-----------------CATEGORIES-------------------------#
		#contains all the cellosaurus categories and their wikidata item id
			#associated
		categories=categories("project/category.txt")

		#-----------------DISEASES-------------------------#
		#contains all wikidata items with NCI thesaurus id
		
		diseases=correspondance["diseases"]
		#if disease items in wikidata have the same NCI thesaurus id, they are
			#written in /doc/ERRORS/diseases/more_than_1.txt
		with open ("doc/ERRORS/diseases/more_than_1.txt", "w") as file:
			for duplicate in correspondance["problematicdiseases"]:
				file.write(duplicate+"\t"+str(correspondance["problematicdiseases"][duplicate])+"\n")

		#-----------------COMPARE_CELLOSAURUS_WIKIDATA-------------------------#
		#Create_Update object creation
		Release=Create_Update(login=login, releaseID=sys.argv[1], cellosaurus=cellosaurus, wikidata=wikidata, references=references, species=species, categories=categories, diseases=diseases)

		update={}
		create=[]

		#for each cell line, find if it needs to be created or updated or deleted
			#in wikidata. 
		
		with open ("results/cell_line_duplicate.txt", "w") as file:
			#for cell_line in Release.cellosaurus:
			for cell_line in ["CVCL_4888"]:
				#-----------------UPDATE-------------------------#
				if cell_line in Release.wikidata and cell_line not in update:
					# the cell line exist in Wikidata, it needs to be updated.
					update[cell_line]=wikidata[cell_line]
					Release.UpdateWikidata(cell_line, Release.InitialisationData(cell_line))

				#-----------------DUPLICATE-------------------------#
				elif cell_line in Release.wikidata and cell_line in update:
					#the cell line is duplicated
					file.write(cell_line+"\t"+wikidata[cell_line]+"\n")

				#-----------------CREATE-------------------------#
				else:
					#the cell line does not exist in Wikidata, it needs to be
						#created.
					create.append(cell_line)
					Release.InsertionWikidata(cell_line, Release.InitialisationData(cell_line))


		#-----------------DELETE-------------------------#
		with open ("results/Qids_2_delete.txt", "w") as file:		
			for cell_line in Release.wikidata:
				#the cell line exists in Wikidata but not in Cellosaurus, it
					#needs to be deleted.
				if cell_line not in Release.cellosaurus:
					file.write(cell_line+"\t"+wikidata[cell_line]+"\n")

		#-----------------ADD_PARENT_&_AUTOLOGOUS_CELL_LINES-------------------------#
		
		#Update the Wikidata informations after integration
		wikidata=QueryingWikidata()
		Release.Update_Wikidata(wikidata)

		#Update parent and autologous informations
		for cell_line in Release.AddParentCellline:
			if cell_line in Release.wikidata:
				Release.UpdateWikidata(cell_line, Release.InitialisationData(cell_line))





	else:
		print("------------------- Give the Wikidata ID for the release (form Q*****) in 1st argument -------------------")

	
else:
	print("------------------- You have to give the Wikidata ID for the Cellosaurus release -------------------")

