#!/Users/leliadebornes/anaconda3/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import json
import pickle
import os

"""
Contain the main functions for Wikidata Cellosaurus Bot
"""


def DeserializeData(pickleFileName):
	"""
	If you want to Deserialize a pickle file.
	:param pickeFileName : YourFile.pickle
	:return : a dictionnary wich contain YourFile.pickle informations
	"""

	with open(pickleFileName, 'rb') as file:
		dictionnary=pickle.load(file)
	return dictionnary

def SerializeData(dictionnary, pickleFileName):
	"""
	If you want to serialize dictionnary into a file.
	:param dictionnary : the dictionnary that you want to serialize
	:param pickleFileName : the name of the file that will contain you
	    serialized dictionnary
	"""

	with open(pickleFileName, 'wb') as file:
		pickle.dump(dictionnary, file)

def categories(file):
	"""
	Get cartegories for cell lines from file.
	:param file : a file which contains categories for cell lines
	:return : a dictionnary, in key the category name, in value the wikidata
	    item id corresponding
	"""
	categories={}
	with open (file) as file:
		for line in file:
			line=line.split(" (")
			category=line[0]
			QID=line[1].strip(")\n")
			categories[category]=QID
		return categories

def correspondance(cellosaurus):
	"""
	This function create dictionnaries of list of pre-requisite wikidata
		informations.
	:param cellosaurus : the cellosaurus dictionnary from .txt file create
	    with CellosaurusToDictionary function
	:return : a dictionnary with contain dictionnaries or list.
		- references dictionnary : in key, the PubMed or DOI id for an article
		  	in wikidata and in value, the wikidata item id which correspond to
		  	this article.
		- DOI_not_in_wikidata : a list of DOI references that are not in
		 	 wikidata.
		- error_references : all the errors that occurs during the item
		  creation for the article by Fatameh.
		- species dictionnary : in key, a NCBI taxonomy id in cellosaurus
		  	and in value, the wikidata item id which correspond to this species
		- problematic_species: a list of NCBI taxonomy id that are not in
		  	wikidata.
		- diseases dictionnary : in key, a NCI thesaurus if in cellosaurus and
		  	in value, the wikidata item id which correspond to this disease.
		- problematic_diseases : in key notin, if the disease is not in
		  	wikidata; in key morethan, if the NCI thesaurus id correspond to
		  	more than 1 disease in Wikidata. In value, the thesaurus id with
		  	these problems.


	"""

	references={}
	references_done=[]
	DOI_not_in_wikidata=[]
	error_references={}
	species={}
	problematic_species={}
	diseases={}
	problematic_diseases={}

	query1=wdi_core.WDItemEngine.execute_sparql_query("""SELECT distinct ?item ?taxid WHERE { ?item p:P685 ?node. ?node ps:P685 ?taxid.}""")
	for spec in query1['results']['bindings']:
		WDid=spec['item']['value'].strip("http://www.wikidata.org/entity/")
		Taxid=spec['taxid']['value']
		if Taxid in species and Taxid not in problematic_species:
			problematic_species[Taxid]=[WDid]
		elif Taxid in species and Taxid in problematic_species:
			problematic_species[Taxid].append(WDid)
		elif Taxid not in species:
			species[Taxid]=WDid


	with open ("doc/ERRORS/Fatameh_errors.txt", "w") as references_errors:

		for celline in cellosaurus:
		
			if cellosaurus[celline]["RX"] != []:
						
						for reference in cellosaurus[celline]["RX"]:
							
							if reference.startswith("PubMed"):
								pubmed=reference.strip("PubMed=")
								if pubmed not in references :
									query=wdi_core.WDItemEngine.execute_sparql_query("""SELECT ?item WHERE{?item wdt:P698 '"""+pubmed+"""'.}""")
									query=query['results']
									query=query['bindings']
									if query == []:
										if reference not in references_done:
											references_done.append(reference)
											result=os.popen("curl --header 'Authorization: Token 6fef682d6c34261d860dde2b5dc3561d63b4fefe' tools.wmflabs.org/fatameh/token/pmid/add/"+pubmed, "r")	
											exitresult=result.read().replace('"', '\"')
											final=json.loads(exitresult)
					
											if final['error'] != []:
												error_references[reference]=str(result)
												references_errors.write(reference+"\t"+str(exitresult)+"\n")

									else:
										query=query[0]['item']['value']
										QIDreferences=query.strip("http://www.wikidata.org/entity/")
										references[pubmed]=QIDreferences
								

							if  reference.startswith("DOI"):
								DOI=reference.strip("DOI=")
								if DOI not in references and DOI not in DOI_not_in_wikidata:
									query=wdi_core.WDItemEngine.execute_sparql_query("""SELECT ?item WHERE{?item wdt:P356 '"""+DOI+"""'.}""")
									query=query['results']
									query=query['bindings']
									if query == []:
										DOI_not_in_wikidata.append(DOI)
									else:
										query=query[0]['item']['value']
										QIDreferences=query.strip("http://www.wikidata.org/entity/")
										references[DOI]=QIDreferences
	



	query3=wdi_core.WDItemEngine.execute_sparql_query("""SELECT ?item ?NCIt WHERE { ?item wdt:P1748 ?NCIt.}""")
	for disease in query3['results']['bindings']:
		WDid=disease['item']['value'].strip("http://www.wikidata.org/entity/")
		NCIt=disease['NCIt']['value']
		if NCIt in diseases and NCIt not in problematic_diseases:
			problematic_diseases[NCIt]=[WDid]
		elif NCIt in diseases and NCIt in problematic_diseases:
			problematic_diseases[NCIt].append(WDid)
		elif NCIt not in diseases:
			diseases[NCIt]=WDid

	return {"references":references, "referencesniw":DOI_not_in_wikidata, "errorreferences":error_references, "species":species, "problematicspecies":problematic_species, "diseases":diseases, "problematicdiseases":problematic_diseases}

class Create_Update():
	"""
	This class is using for integrate data in Wikidata
	"""

	def __init__(self, login='', releaseID='', cellosaurus='', wikidata='', references='', species='', categories='', diseases=''):
		"""
		:param login : login correspond to a wdi_login object (..seealso::
		    login in Main.py).
		:param releaseID : the wikidata item id which corresponding to the
		    Cellosaurus release.
		:param cellosaurus : the cellosaurus dictionnary which contains
		    cellosaurus dump information.
		:param wikidata : the wikidata dictionnary which contains wikidata
		    cell lines items that already exit.
		:param references : the references dictionnary creating with
		    correspondance function.
		:param species : the species dictionnary creating with correspondance
		    function.
		:param categories : the categories dictionnary creating with
		    categories function.
		:param diseases : the diseases dictionnary creating with
		    correspondance function.
		"""
		
		self.login=login
		self.releaseID=releaseID
		self.cellosaurus=cellosaurus
		self.wikidata=wikidata
		self.references=references
		self.species=species
		self.categories=categories
		self.diseases=diseases
		self.AddParentCellline=[]
		self.PublicationNotReferencing=[]
		self.WIDs=[]

	
	def Update_Wikidata(self, newWikidata):
		self.wikidata=newWikidata
	
	def InitialisationData(self, Item):
		"""
		This function must have to be run for each cell line in cellosaurus.
		It create the information objects that will be in the Wikidata item
			for the cell line.

		:param Item: the Cellosaurus id for a cell line. 
		:return : a dictionnary composed of 2 dictionnaries: 
			- data : is composed of information objects that are to add or
			  	update for the wikidata cell line item.
			- data_to_delete : is the information objects that are have to be
			  	deleted in this release for a wikidata cell line item.
		"""


		data=[]
		data_to_delete=[]

		if self.cellosaurus[Item]["CA"] == "NULL" or self.cellosaurus[Item]["CC"] == []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P31"))
			data_to_delete.append("P31")


		#add item cell line(Q21014462) in instance of(P31):
		data.append(wdi_core.WDItemID(value="Q21014462", prop_nr="P31"))
		
		
		#add category item in instance of(P31):
		if self.cellosaurus[Item]["CA"] in self.categories:
			data.append(wdi_core.WDItemID(value=self.categories[self.cellosaurus[Item]["CA"]],prop_nr="P31"))


		#add contaminated/misiendtified(Q27971671) in instance of(P31) if cell
			#line is contaminated of misidentified
		if self.cellosaurus[Item]["CC"] != []:
			data.append(wdi_core.WDItemID(value="Q27971671", prop_nr="P31"))

 		
 		#check if disease informations exists for the cell line
		if self.cellosaurus[Item]["DI"]== []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P5166"))
			data_to_delete.append("P5166")
		
		else:
			for disease in self.cellosaurus[Item]["DI"]:
				#add the disease in established from medical condition(P5166)
				if disease in self.diseases:
					data.append(wdi_core.WDItemID(value=self.diseases[disease], prop_nr="5166"))
				#if the disease does not exist in Wikidata, write it in
					#doc/ERRORS/diseases/not_in.txt
				else :
					with open ("doc/ERRORS/diseases/not_in.txt", "a") as file:
						file.write(disease+"\n")
		

		#check if species information exists for the cell line
		if self.cellosaurus[Item]["OX"] == []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement( prop_nr="P703"))
			data_to_delete.append("P703")
	

		species=[]
		for spec in self.cellosaurus[Item]["OX"]:
			if spec in self.species:
				species.append(self.species[spec])
			else:
				#if the species is not in wikidata, write it in
					#doc/ERRORS/species.txt
				with open ("doc/ERRORS/species.txt", "a") as file:
					file.write(spec+"\n")


		#check if sexes information exists for the cell line
		if self.cellosaurus[Item]["SX"] == []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P21"))
			data_to_delete.append("P21")
		

		sexes=[]
		
		for sexe in self.cellosaurus[Item]["SX"]:

			if sexe == "Sex unspecified":
				#add "Unknow value" if sex is unspecified in sex or gender
					#(P21)
				sexes.append(wdi_core.WDString(value="Unknow value", prop_nr="P21", is_qualifier=True))
			else:
				#else add the item corresponding to sex in sex or gender (P21)
				if "Q15978631" in species:
					if sexe == "Female":
						value="Q6581072"
					elif sexe == "Male":
						value="Q6581097"
					elif sexe == "Intersex":
						value="Q1097630"
				else:
					if sexe == "Female":
						value="Q43445"
					elif sexe == "Male":
						value="Q44148"	
					elif sexe == "Intersex":
						value="Q28873047"
				sexes.append(wdi_core.WDItemID(value=value, prop_nr="P21", is_qualifier=True))
			
		#add species information in found in taxon (P703)
		if species != []:
			for spec in species:
				data.append(wdi_core.WDItemID(value=spec, prop_nr="P703", qualifiers=sexes))

		#check if parent cell line information exist for the cell line 
		if self.cellosaurus[Item]["HI"] == []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P3432"))
			data_to_delete.append("P3432")
		

		for parent in self.cellosaurus[Item]["HI"]:
			if parent in self.wikidata:
				#add parent cell line information in parent cell line (P3432)
				data.append(wdi_core.WDItemID(value=self.wikidata[parent], prop_nr="P3432"))
			else:
				#if the parent cell line does not exist in Wikidata, add it in
					#AddParentCelline
				if Item not in self.AddParentCellline:
					self.AddParentCellline.append(Item)

		#check if autologous cell line information exist for the cell line
		if self.cellosaurus[Item]["OI"] == []:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P3578"))
			data_to_delete.append("P3578")
		else:
			for autologous in self.cellosaurus[Item]["OI"]:
				if autologous in self.wikidata:
					#add autiologous cell line information in autologous cell line
						#(P3578)
					data.append(wdi_core.WDItemID(value=self.wikidata[autologous], prop_nr="P3578"))
				else:
					#if the autologous cell line does not exist in Wikidata, add
						#it in AddParentCelline
					if Item not in self.AddParentCellline:
						self.AddParentCellline.append(Item)



		release=[wdi_core.WDItemID(value=self.releaseID, prop_nr="P248", is_reference=True)]
		#add the Cellosaurus ID with the Cellosaurus ID in Cellosaurus ID
		#(P3289)
		data.append(wdi_core.WDExternalID(value=Item, prop_nr="P3289", references=[release]))
		

		#check if external reference in CLO, BTO, EFO, BCGO exists
		for id in ["CLO", "BTO", "EFO", "BCGO"]:
			if self.cellosaurus[Item][id] == []:
				#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement( prop_nr="P2888"))
				data_to_delete.append("P2888")

		if self.cellosaurus[Item]["MeSH"] != "NULL":
			#add MeSH id corresponding to the cell line in MeSH ID (P486) if
				#it exists
			data.append(wdi_core.WDExternalID(value=self.cellosaurus[Item]["MeSH"], prop_nr="P486"))
		else:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement( prop_nr="P486"))
			data_to_delete.append("P486")


		if self.cellosaurus[Item]["CLO"] != []:
			for CLO in self.cellosaurus[Item]["CLO"]:
				#add CLO id Url corresponding to the cell line in exact match
					#(P2888)
				data.append(wdi_core.WDUrl(value="http://purl.obolibrary.org/obo/"+CLO, prop_nr="P2888")) 
		

		if self.cellosaurus[Item]["BTO"] != []:
			for BTO in self.cellosaurus[Item]["BTO"]:
				#add BTO id Url corresponding to the cell line in exact match
					#(P2888)
				data.append(wdi_core.WDUrl(value="http://purl.obolibrary.org/obo/"+BTO, prop_nr="2888")) 


		if self.cellosaurus[Item]["EFO"] != []:
			for EFO in self.cellosaurus[Item]["EFO"]:
				#add EFO id Url corresponding to the cell line in exact match
					#(P2888)
				data.append(wdi_core.WDUrl(value="http://purl.obolibrary.org/obo/"+EFO, prop_nr="2888"))
		 

		if self.cellosaurus[Item]["BCGO"] != []:
			for BCGO in self.cellosaurus[Item]["BCGO"]:
				#add BCGO id Url corresponding to the cell line in exact match
					#(P2888)
				data.append(wdi_core.WDUrl(value="http://purl.obolibrary.org/obo/"+BCGO, prop_nr="2888"))


		if self.cellosaurus[Item]["RX"] != []:
			for reference in self.cellosaurus[Item]["RX"]:
				if reference.startswith("PubMed"):
					pubmed=reference.strip("PubMed=")
					if pubmed in self.references:
						#add Pubmed reference with the property described by
							#source (P1343)
						data.append(wdi_core.WDItemID(value=self.references[pubmed], prop_nr="P1343"))
				elif reference.startswith("DOI"):
					DOI=reference.strip("DOI=")
					if DOI in self.references:
						#add DOI reference with the property described by
							#source (P1343)
						data.append(wdi_core.WDItemID(value=self.references[DOI], prop_nr="P1343"))	
		else:
			#data_to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr="P1343"))
			data_to_delete.append("P1343")

		return {'data':data, 'data_to_delete':data_to_delete}

	




	def InsertionWikidata(self, Item, data):
		"""
		This function create a Wikidata item for the cell line with
			cellosaurus informations.
		:param Item : the Cellosaurus id for a cell line.
		:param data : the dictionnary from InitialisationData function.
		:return : WikidataID.txt, a file which contains the Wikidata cell
		    lines items created.
		"""

		item=wdi_core.WDItemEngine(item_name=Set(self.cellosaurus,Item)['name'], domain="cell line", data=data['data'], fast_run=True, fast_run_base_filter= {'P31':'Q21014462','P31':'','P21':'', 'P703':'', 'P3432':'','P3578':'','P248':'','P3289':'','P486':'', 'P2888':'','P1343':''}, fast_run_use_refs=True)

		if self.cellosaurus[Item]["SY"] != []:
			item.set_aliases(self.cellosaurus[Item]["SY"], lang='en', append=False)

		for lang, description in Set(self.cellosaurus,Item)['descriptions'].items():
			item.set_description(description, lang=lang)
			item.set_label(label=Set(self.cellosaurus,Item)['name'], lang=lang)


		#with open ("results/WikidataID.txt", "a") as file:
			#file.write(item.write(self.login, bot_account=True, edit_summary="create item {}".format(self.cellosaurus[Item]["ID"]))+"\t"+Item+"\n")	
	


	def UpdateWikidata(self, Item, data):
		"""
		This function update a Wikidata item (add or delete informations).
		:param Item : the Cellosaurus id for a cell line.
		:param data : the dictionnary from InitialisationData function within
		    data and data_to_delete dictionnaries.
		"""

		to_delete=[]

		name=Set(self.cellosaurus, Item)['name']
		descriptions=Set(self.cellosaurus, Item)['descriptions']


		if data['data_to_delete']!= []:
			old=wdi_core.WDItemEngine(wd_item_id=self.wikidata[Item],domain="cell line")
			olditem=old.get_wd_json_representation()
			for statement in olditem['claims']:
				if statement in data['data_to_delete']:
					to_delete.append(wdi_core.WDBaseDataType.delete_statement(prop_nr=statement))
			item_deletion=wdi_core.WDItemEngine(wd_item_id=self.wikidata[Item], domain="cell line", data=to_delete)
			#item_deletion.write(self.login, bot_account=True, edit_summary="delete statements before update the item {}".format(self.cellosaurus[Item]["ID"]))



		item=wdi_core.WDItemEngine(wd_item_id=self.wikidata[Item],domain="cell line",data=data['data'],fast_run=True, fast_run_base_filter={'P31':'Q21014462','P31':'','P21':'', 'P703':'', 'P3432':'','P3578':'','P248':'','P3289':'','P486':'', 'P2888':'','P1343':''},fast_run_use_refs=True)


		if self.cellosaurus[Item] != "NUL":
			item.set_aliases(self.cellosaurus[Item]["SY"], lang='en', append=False)
		
		for lang, description in descriptions.items():
			item.set_description(description, lang=lang)
			item.set_label(label=name, lang=lang)
		
		#item.write(self.login, bot_account=True, edit_summary="update item {}".format(self.cellosaurus[Item]["ID"]))



def Set(cellosaurus, Item):
	"""
	This function is using for give name and description in english, french
	and deutch.
	:param Item : the Cellosaurus id for a cell line.
	:return : dictionnaries with the name and the description in english, french and deutch
	"""

	name=cellosaurus[Item]["ID"]

	descriptions={
	"en":"cell line",
	"fr":"lignée cellulaire",
	"de":"Zelllinie"
	}

	if "[" in name:
		namecompose=name.split("[")
		descriptions={
		"en":"cell line"+" ("+namecompose[1].strip("]")+")",
		"fr":"lignée cellulaire"+" ("+namecompose[1].strip("]")+")",
		"de":"Zelllinie"+" ("+namecompose[1].strip("]")+")"
		}
		name=namecompose[0].strip(" ")

	return {'name':name, 'descriptions':descriptions}



def CellosaurusToDictionary(file):
	"""
	Format Cellosaurus dump (.txt) in a dictionnary with the informations that
		will integrating in Wikidata. 
	:param file : the cellosaurus dump at .txt format
	:return :  a dictionnary. In key, the Cellosaurus id for the cell line. In
	    value, the informations on the cell line (name, aliases, external ids,
	    species of origin, parent cell line, references, autologous cell line,
	    sex of the species of origin, ctaegory of the cell line, etc...) 
	"""
	dico={}
	with open(file) as file:
		AS="NULL"
		SY=[]
		MeSH="NULL"
		CLO=[]
		BTO=[]
		EFO=[]
		BCGO=[]
		RX=[]
		WW=[]
		CC=[]
		DI=[]
		di_names={}
		OX=[]
		HI=[]
		OI=[]
		SX=[]
		CA="NULL"
		for line in file.readlines():
			if line.startswith("ID"):
				ID=line.rstrip("\n").split("   ")[1]
			if line.startswith("AC"):
				AC=line.rstrip("\n").split("   ")[1]
			if line.startswith("AS"):
				AS=line.rstrip("\n").split("   ")[1]
			if line.startswith("SY"):
				SY=line.rstrip("\n").split("   ")[1].split(";")
			if line.startswith("DR"):
				DR=line.rstrip("\n").split("   ")[1]
				if DR.startswith("MeSH"):
					MeSH=DR.strip("MeSH;")
				if DR.startswith("CLO"):
					CLO.append(DR.strip("CLO;").strip(" "))
				if DR.startswith("BTO"):
					BTO.append(DR.strip("BTO;").replace("BTO:", "BTO_").strip(" "))
				if DR.startswith("EFO"):
					EFO.append(DR.strip("EFO;").strip(" "))
				if DR.startswith("BCGO"):
					BCGO.append(DR.strip("BCGO;").strip(" "))
			if line.startswith("RX"):
				reference=line.rstrip("\n").split("   ")[1]
				if reference.startswith("PubMed") or reference.startswith("DOI"):
					RX.append(reference.strip(";"))
			if line.startswith("WW"):
				WW.append(line.rstrip("\n").split("   ")[1])
			if line.startswith("CC"):
				comment=(line.rstrip("\n").split("   ")[1])
				if "Problematic cell line:" in comment:
					CC.append(comment.strip("Problematic cell line: ").split(".")[0])
			if line.startswith("DI"):
				disease=line.rstrip("\n").split("   ")[1]
				DI.append(disease.split(";")[1].strip(" "))
				di_names[disease.split(";")[1].strip(" ")]=disease.split(";")[2].strip(" ").strip("\n")
			if line.startswith("OX"):
				species=line.rstrip("\n").split("   ")[1]
				OX.append(species.strip("NCBI_TaxID=").split(";")[0])
			if line.startswith("HI"):
				hi=line.rstrip("\n").split("   ")[1].split(";")
				HI.append(hi[0].split(" !")[0])
			if line.startswith("OI"):
				oi=line.rstrip("\n").split("   ")[1].split(";")
				OI.append(oi[0].split(" !")[0])
			if line.startswith("SX"):
				SX.append(line.rstrip("\n").split("   ")[1])
			if line.startswith("CA"):
				CA= line.strip("\n").split("   ")[1]
			if line.startswith("//"):
				dico[AC]={"ID":ID,
				"AS":AS, 
				"SY":SY, 
				"MeSH":MeSH, 
				"CLO":CLO,
				"BTO":BTO,
				"EFO":EFO,
				"BCGO":BCGO,
				"RX":RX,
				"WW":WW, 
				"CC":CC,
				"DI":DI,
				"DI_names":di_names,
				"OX":OX,
				"HI":HI,
				"OI":OI,
				"SX":SX,
				"CA":CA} 
				AC="NULL"
				ID="NULL"
				SY=[]
				CLO=[]
				MeSH="NULL"
				BTO=[]
				EFO=[]
				BCGO=[]
				AS="NULL"
				RX=[]
				WW=[]
				CC=[]
				DI=[]
				di_names={}
				OX=[]
				HI=[]
				OI=[]
				SX=[]	
				CA="NULL"
		return(dico)




def QueryingWikidata():

	"""
	Thanks to a SPARQL request on Wikidata, this function recover all the cell
		lines that exist already in Wikidata (with a Cellosaurus id).
	:return : a dictionnary with in key, the Cellosaurus id and in value the
	    Wikidata cell line item id.
	"""
	Wikidata_query_result={}
	query=wdi_core.WDItemEngine.execute_sparql_query(query="""SELECT distinct ?QID ?CVCL WHERE{  
	?QID wdt:P31 wd:Q21014462.
	?QID wdt:P3289 ?CVCL.
	}""")
	query=query['results']
	query=query['bindings']
	for data in query:
		QID=data['QID']
		QID=str(QID['value'])
		QID=QID.strip("http://www.wikidata.org/entity/").strip("\n")
		CVCL=data['CVCL']
		CVCL=CVCL['value']
		Wikidata_query_result[CVCL]=QID
	return(Wikidata_query_result)

