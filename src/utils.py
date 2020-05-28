#!/usr/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import calendar
from datetime import datetime, date
import json
import pickle
import os

"""
Contain the main functions for Wikidata Cellosaurus Bot
"""


def DeserializeData(pickleFileName):
    return (load_pickle_file(pickleFileName))


def SerializeData(dictionary, pickleFileName):
    return (save_pickle_file(dictionary, pickleFileName))


def categories(file):
    """
    Get cartegories for cell lines from file.
    :param file : a file which contains categories for cell lines
    :return : a dictionary, in key the category name, in value the wikidata
        item id corresponding
    """
    categories = {}
    with open(file) as file:
        for line in file:
            line = line.split(" (")
            category = line[0]
            QID = line[1].strip(")\n")
            categories[category] = QID
        return categories


def correspondance(cellosaurus):
    return (match_cellosaurus_to_wikidata_items(cellosaurus))


class Create_Update():
    """
    This class is using for integrate data in Wikidata
    """

    def __init__(self, login='', releaseID='', cellosaurus='', wikidata='', references='', species='', categories='',
                 diseases=''):
        """
        :param login : login correspond to a wdi_login object (..seealso::
            login in Main.py).
        :param releaseID : the wikidata item id which corresponding to the
            Cellosaurus release.
        :param cellosaurus : the cellosaurus dictionary which contains
            cellosaurus dump information.
        :param wikidata : the wikidata dictionary which contains wikidata
            cell lines items that already exit.
        :param references : the references dictionary creating with
            correspondance function.
        :param species : the species dictionary creating with correspondance
            function.
        :param categories : the categories dictionary creating with
            categories function.
        :param diseases : the diseases dictionary creating with
            correspondance function.
        """

        self.login = login
        self.releaseID = releaseID
        self.cellosaurus = cellosaurus
        self.wikidata = wikidata
        self.references = references
        self.species = species
        self.categories = categories
        self.diseases = diseases
        self.AddParentCellline = []
        self.PublicationNotReferencing = []
        self.WIDs = []

    def Update_Wikidata(self, newWikidata):
        self.wikidata = newWikidata

    def InitialisationData(self, Item):
        return create_information_objects_for_wikidata(self, Item)

    def InsertionWikidata(self, Item, data):
        """
        This function create a Wikidata item for the cell line with
            cellosaurus informations.
        :param Item : the Cellosaurus id for a cell line.
        :param data : the dictionary from InitialisationData function.
        :return : WikidataID.txt, a file which contains the Wikidata cell
            lines items created.
        """
        item = wdi_core.WDItemEngine(data=data['data'], global_ref_mode='STRICT_OVERWRITE', fast_run=True,
                                     fast_run_base_filter={
                                         'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '',
                                         'P248': '', 'P3289': '', 'P486': '', 'P2888': '', 'P1343': '', 'P5166': '',
                                         'P813': ''}, fast_run_use_refs=True)

        if self.cellosaurus[Item]["SY"] != []:
            item.set_aliases(
                self.cellosaurus[Item]["SY"], lang='en', append=False)

        for lang, description in Set(self.cellosaurus, Item)['descriptions'].items():
            item.set_description(description, lang=lang)
            item.set_label(label=Set(self.cellosaurus, Item)
            ['name'], lang=lang)

        with open("results/WikidataID.txt", "a") as file:
            file.write(item.write(self.login, bot_account=False, edit_summary="create item {}".format(
                self.cellosaurus[Item]["ID"])) + "\t" + Item + "\n")

    def UpdateWikidata(self, Item, data):
        """
        This function update a Wikidata item (add or delete informations).
        :param Item : the Cellosaurus id for a cell line.
        :param data : the dictionary from InitialisationData function within
            data and data_to_delete dictionnaries.
        """

        to_delete = []

        name = Set(self.cellosaurus, Item)['name']
        descriptions = Set(self.cellosaurus, Item)['descriptions']

        if data['data_to_delete'] != []:
            old = wdi_core.WDItemEngine(wd_item_id=self.wikidata[Item])
            olditem = old.get_wd_json_representation()
            for statement in olditem['claims']:
                if statement in data['data_to_delete']:
                    to_delete.append(
                        wdi_core.WDBaseDataType.delete_statement(prop_nr=statement))

            item_deletion = wdi_core.WDItemEngine(
                wd_item_id=self.wikidata[Item], data=to_delete)
            item_deletion.write(self.login, bot_account=False,
                                edit_summary="delete statements before update the item {}".format(
                                    self.cellosaurus[Item]["ID"]))

        item = wdi_core.WDItemEngine(wd_item_id=self.wikidata[Item], data=data['data'],
                                     global_ref_mode='STRICT_OVERWRITE', fast_run=True, fast_run_base_filter={
                'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '', 'P248': '', 'P3289': '',
                'P486': '', 'P2888': '', 'P1343': '', 'P5166': '', 'P813': ''}, fast_run_use_refs=True)

        if self.cellosaurus[Item] != "NUL":
            item.set_aliases(
                self.cellosaurus[Item]["SY"], lang='en', append=False)

        for lang, description in descriptions.items():
            item.set_description(description, lang=lang)
            item.set_label(label=name, lang=lang)

        item.write(self.login, bot_account=False, edit_summary="update item {}".format(
            self.cellosaurus[Item]["ID"]))


def Set(cellosaurus, Item):
    """
    This function is using for give name and description in english, french
    and deutch.
    :param Item : the Cellosaurus id for a cell line.
    :return : dictionnaries with the name and the description in english, french and deutch
    """

    name = cellosaurus[Item]["ID"]

    descriptions = {
        "en": "cell line",
        "fr": "lignée cellulaire",
        "de": "Zelllinie"
    }

    if " [" in name:
        namecompose = name.split("[")
        descriptions = {
            "en": "cell line" + " (" + namecompose[1].strip("]") + ")",
            "fr": "lignée cellulaire" + " (" + namecompose[1].strip("]") + ")",
            "de": "Zelllinie" + " (" + namecompose[1].strip("]") + ")"
        }
        name = namecompose[0].strip(" ")

    return {'name': name, 'descriptions': descriptions}


def CellosaurusToDictionary(file):
    """
    Format Cellosaurus dump (.txt) in a dictionary with the informations that
        will integrating in Wikidata. 
    :param file : the cellosaurus dump at .txt format
    :return :  a dictionary. In key, the Cellosaurus id for the cell line. In
        value, the informations on the cell line (name, aliases, external ids,
        species of origin, parent cell line, references, autologous cell line,
        sex of the species of origin, ctaegory of the cell line, etc...) 
    """
    dico = {}
    with open(file) as file:
        AS = "NULL"
        SY = []
        MeSH = "NULL"
        CLO = []
        BTO = []
        EFO = []
        BCGO = []
        RX = []
        WW = []
        CC = []
        DI = []
        di_names = {}
        OX = []
        HI = []
        OI = []
        SX = []
        CA = "NULL"
        for line in file.readlines():
            if line.startswith("ID"):
                ID = line.rstrip("\n").split("   ")[1]
            if line.startswith("AC"):
                AC = line.rstrip("\n").split("   ")[1]
            if line.startswith("AS"):
                AS = line.rstrip("\n").split("   ")[1]
            if line.startswith("SY"):
                SY = line.rstrip("\n").split("   ")[1].split(";")
            if line.startswith("DR"):
                DR = line.rstrip("\n").split("   ")[1]
                if DR.startswith("MeSH"):
                    MeSH = DR.strip("MeSH; ")
                if DR.startswith("CLO"):
                    CLO.append(DR.strip("CLO;").strip(" "))
                if DR.startswith("BTO"):
                    BTO.append(DR.strip("BTO;").replace(
                        "BTO:", "BTO_").strip(" "))
                if DR.startswith("EFO"):
                    EFO.append(DR.strip("EFO;").strip(" "))
                if DR.startswith("BCGO"):
                    BCGO.append(DR.strip("BCGO;").strip(" "))
            if line.startswith("RX"):
                reference = line.rstrip("\n").split("   ")[1]
                if reference.startswith("PubMed") or reference.startswith("DOI"):
                    RX.append(reference.strip(";"))
            if line.startswith("WW"):
                WW.append(line.rstrip("\n").split("   ")[1])
            if line.startswith("CC"):
                comment = (line.rstrip("\n").split("   ")[1])
                if "Problematic cell line:" in comment:
                    CC.append(comment.strip(
                        "Problematic cell line: ").split(".")[0])
            if line.startswith("DI"):
                disease = line.rstrip("\n").split("   ")[1]
                DI.append(disease.split(";")[1].strip(" "))
                di_names[disease.split(";")[1].strip(" ")] = disease.split(";")[
                    2].strip(" ").strip("\n")
            if line.startswith("OX"):
                species = line.rstrip("\n").split("   ")[1]
                OX.append(species.strip("NCBI_taxid=").split(";")[0])
            if line.startswith("HI"):
                hi = line.rstrip("\n").split("   ")[1].split(";")
                HI.append(hi[0].split(" !")[0])
            if line.startswith("OI"):
                oi = line.rstrip("\n").split("   ")[1].split(";")
                OI.append(oi[0].split(" !")[0])
            if line.startswith("SX"):
                SX.append(line.rstrip("\n").split("   ")[1])
            if line.startswith("CA"):
                CA = line.strip("\n").split("   ")[1]
            if line.startswith("//"):
                dico[AC] = {"ID": ID,
                            "AS": AS,
                            "SY": SY,
                            "MeSH": MeSH,
                            "CLO": CLO,
                            "BTO": BTO,
                            "EFO": EFO,
                            "BCGO": BCGO,
                            "RX": RX,
                            "WW": WW,
                            "CC": CC,
                            "DI": DI,
                            "DI_names": di_names,
                            "OX": OX,
                            "HI": HI,
                            "OI": OI,
                            "SX": SX,
                            "CA": CA}
                AC = "NULL"
                ID = "NULL"
                SY = []
                CLO = []
                MeSH = "NULL"
                BTO = []
                EFO = []
                BCGO = []
                AS = "NULL"
                RX = []
                WW = []
                CC = []
                DI = []
                di_names = {}
                OX = []
                HI = []
                OI = []
                SX = []
                CA = "NULL"
        return (dico)


def QueryingWikidata():
    return (query_wikidata_for_cell_lines())


# Auxiliary functions added by lubianat

###### Functions to process pickle files ######

def load_pickle_file(pickleFileName):
    """
    Loads a serialized pickle file.
    :param pickeFileName : YourFile.pickle
    :return : a dictionary wich contain YourFile.pickle informations
    """

    with open(pickleFileName, 'rb') as file:
        dictionary = pickle.load(file)
    return dictionary


def save_pickle_file(dictionary, pickleFileName):
    """
    Saves a dictionary into a pickle file.
    :param dictionary : the dictionary that you want to serialize
    :param pickleFileName : the name of the file
    """
    with open(pickleFileName, 'wb') as file:
        pickle.dump(dictionary, file)


###### Functions to query and match to wikidata ###### 

def match_cellosaurus_to_wikidata_items(cellosaurus_in_dicionary_format):
    """
    This function create dictionnaries of list of pre-requisite wikidata
        informations.
    :param cellosaurus_in_dicionary_format : the cellosaurus dictionary from .txt file create
        with CellosaurusToDictionary function
    :return : a dictionary with contain dictionnaries or list.
        - references dictionary : in key, the PubMed or DOI id for an article
              in wikidata and in value, the wikidata item id which correspond to
              this article.
        - DOI_not_in_wikidata : a list of DOI references that are not in
              wikidata.
        - error_references : all the errors that occurs during the item
          creation for the article by Fatameh.
        - species dictionary : in key, a NCBI taxonomy id in cellosaurus
              and in value, the wikidata item id which correspond to this species
        - problematic_species: a list of NCBI taxonomy id that are not in
              wikidata.
        - diseases dictionary : in key, a NCI thesaurus if in cellosaurus and
              in value, the wikidata item id which correspond to this disease.
        - problematic_diseases : in key notin, if the disease is not in
              wikidata; in key morethan, if the NCI thesaurus id correspond to
              more than 1 disease in Wikidata. In value, the thesaurus id with
              these problems.


    """
    references = {}
    references_that_were_not_on_wikidata = []
    DOI_not_in_wikidata = []
    error_references = {}
    species = {}
    problematic_species = {}
    diseases = {}
    problematic_diseases = {}

    taxids_on_wikidata = query_wikidata_for_taxids()

    species, problematic_species = add_ids_to_species_id_holders(
        taxids_on_wikidata)

    with open("../doc/ERRORS/Fatameh_errors.txt", "w") as references_errors:

        for celline in cellosaurus_in_dicionary_format:

            cell_line_references = cellosaurus_in_dicionary_format[celline]["RX"]

            if cell_line_references != []:

                for reference in cell_line_references:

                    if reference.startswith("PubMed"):
                        pubmed_id = reference.strip("PubMed=")

                        if pubmed_id not in references:
                            query = query_wikidata_by_pubmed_id(pubmed_id)

                            if query == []:
                                if reference not in references_that_were_not_on_wikidata:
                                    print(
                                        "This reference is not on Wikidata yet: " + reference)
                                    add_reference_to_wikidata(pubmed_id)
                                    references_that_were_not_on_wikidata.append(
                                        reference)
                                    references_errors.write(
                                        "Reference for article with PMID " + pubmed_id + " could not be added to Wikidata")

                            else:
                                query = query[0]['item']['value']
                                QIDreferences = query.strip(
                                    "http://www.wikidata.org/entity/")
                                references[pubmed_id] = QIDreferences

                    if reference.startswith("DOI"):
                        DOI = reference.strip("DOI=")
                        if DOI not in references and DOI not in DOI_not_in_wikidata:
                            query = wdi_core.WDItemEngine.execute_sparql_query(
                                """SELECT ?item WHERE{?item wdt:P356 '""" + DOI + """'.}""")
                            query = query['results']
                            query = query['bindings']
                            if query == []:
                                DOI_not_in_wikidata.append(DOI)
                            else:
                                query = query[0]['item']['value']
                                QIDreferences = query.strip(
                                    "http://www.wikidata.org/entity/")
                                references[DOI] = QIDreferences

    query3 = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item ?NCIt WHERE { ?item wdt:P1748 ?NCIt.}""")
    for disease in query3['results']['bindings']:
        wikidata_id = disease['item']['value'].strip(
            "http://www.wikidata.org/entity/")
        NCIt = disease['NCIt']['value']
        if NCIt in diseases and NCIt not in problematic_diseases:
            problematic_diseases[NCIt] = [wikidata_id]
        elif NCIt in diseases and NCIt in problematic_diseases:
            problematic_diseases[NCIt].append(wikidata_id)
        elif NCIt not in diseases:
            diseases[NCIt] = wikidata_id

    return {"references": references, "referencesniw": DOI_not_in_wikidata, "errorreferences": error_references,
            "species": species, "problematicspecies": problematic_species, "diseases": diseases,
            "problematicdiseases": problematic_diseases}


def query_wikidata_for_taxids():
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT distinct ?item ?taxid WHERE { ?item p:P685 ?node. ?node ps:P685 ?taxid.}""")
    return (query_result['results']['bindings'])


def query_wikidata_for_cell_lines():
    """
    Recover all the cell lines that exist in Wikidata (with a Cellosaurus id).
    :return : a dictionary matching Cellosaurus id to  Wikidata cell line item id.
    """

    query_result = wdi_core.WDItemEngine.execute_sparql_query(query="""SELECT ?QID ?CVCL WHERE{ 
    ?QID wdt:P3289 ?CVCL.
    }""")
    query_result = query_result['results']['bindings']

    cellosaurus_to_wikidata_cell_lines = {}
    for cell_line_entry in query_result:
        QID_url = str(cell_line_entry['QID']['value'])
        QID = QID_url.strip("http://www.wikidata.org/entity/").strip("\n")
        CVCL = cell_line_entry['CVCL']['value']
        cellosaurus_to_wikidata_cell_lines[CVCL] = QID

    return (cellosaurus_to_wikidata_cell_lines)


def query_wikidata_by_pubmed_id(pubmed):
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item WHERE{?item wdt:P698 '""" + pubmed + """'.}""")
    query_result = query_result['results']['bindings']
    return query_result


###### Functions to add things to wikidata ######
def add_reference_to_wikidata(pubmed_id):
    pass


###### Other equally important functions ######
def add_ids_to_species_id_holders(taxid_to_wikidata):
    species_ids = {}
    problematic_species_ids = {}
    for taxid_snak in taxid_to_wikidata:

        wikidata_id = taxid_snak['item']['value'].strip(
            "http://www.wikidata.org/entity/")
        taxid = taxid_snak['taxid']['value']

        if taxid not in species_ids:
            species_ids[taxid] = wikidata_id

        elif taxid in species_ids and taxid not in problematic_species_ids:

            problematic_species_ids[taxid] = [wikidata_id]

        elif taxid in species_ids and taxid in problematic_species_ids:
            problematic_species_ids[taxid].append(wikidata_id)

    return (species_ids, problematic_species_ids)


def get_WQ_reference(Item, cellosaurus_release_qid):
    release = wdi_core.WDItemID(
        value=cellosaurus_release_qid, prop_nr="P248", is_reference=True)

    date = datetime.now()
    timeStringNow = date.strftime("+%Y-%m-%dT00:00:00Z")
    refRetrieved = wdi_core.WDTime(
        timeStringNow, prop_nr='P813', is_reference=True)

    cellosaurusref = wdi_core.WDExternalID(
        value=Item, prop_nr="P3289", is_reference=True)

    WQreference = [[release, refRetrieved, cellosaurusref]]
    return (WQreference)


# Functions to make statements

def make_statement(statement_property, statement_value, references):
    statement = wdi_core.WDItemID(value=statement_value,
                                  prop_nr=statement_property,
                                  references=references)
    return statement


# Q21014462 -> "cell line" ; P31 -> "instance of"
def make_instance_of_cell_line_statement(reference):
    statement = make_statement(statement_property="P31",
                               statement_value="Q21014462",
                               references=reference)
    return statement


def make_instance_of_statement(statement_value, reference):
    statement = make_statement(statement_property="P31",
                               statement_value=statement_value,
                               references=reference)
    return statement


def make_instance_of_contaminated_cell_line_statement(reference):
    statement = make_statement(statement_property="P31",
                               statement_value="Q27971671",
                               references=reference)
    return statement


def make_established_from_disease_statement(disease_id, references):
    cell_line_from_patient_with_disease_statement = make_statement(
        statement_property="5166",
        statement_value=disease_id,
        references=references
    )
    return cell_line_from_patient_with_disease_statement


### Append statement functions


def append_category(self, Item, information_to_insert_on_wikidata, reference):
    # CA         Category
    if self.cellosaurus[Item]["CA"] in self.categories:
        cell_line_category = self.cellosaurus[Item]["CA"]
        cell_line_category_id = self.categories[cell_line_category]

        information_to_insert_on_wikidata.append(make_instance_of_statement(
            statement_value=cell_line_category_id,
            reference=reference
        ))
    return information_to_insert_on_wikidata


def append_is_contaminated(self, Item, information_to_insert_on_wikidata, reference):
    # Q27971671 -> contaminated/misidentified ;
    # P31 -> "instance of"
    # CC         Comments
    # Code currently assumes that if there is a comment, cell line is contaminated.
    if self.cellosaurus[Item]["CC"]:
        information_to_insert_on_wikidata.append(make_instance_of_contaminated_cell_line_statement(
            reference=reference
        ))
    return information_to_insert_on_wikidata


def append_is_cell_ine(information_to_insert_on_wikidata, reference):
    information_to_insert_on_wikidata.append(make_instance_of_cell_line_statement(
        reference=reference
    ))
    return information_to_insert_on_wikidata


def append_diseases(self, Item, information_to_insert_on_wikidata,
                    reference, folder_for_errors):
    # P5166 -->  established from medical condition(
    diseases_in_wikidata = self.diseases

    for disease in self.cellosaurus[Item]["DI"]:
        if disease in diseases_in_wikidata:
            disease_id = diseases_in_wikidata[disease]

            information_to_insert_on_wikidata.append(make_established_from_disease_statement(
                disease_id=disease_id,
                references=reference
            ))

        else:
            with open(folder_for_errors + "diseases/diseases_not_in_wikidata.txt", "a") as file:
                file.write(disease + "\n")
    return information_to_insert_on_wikidata

def get_list_of_taxons(self, Item, folder_for_errors ):

    # OX : Taxon od origin
    # P703 : Found in taxon
    list_of_taxons_of_origin = []

    if self.cellosaurus[Item]["OX"]:

        for taxon_of_origin in self.cellosaurus[Item]["OX"]:
            if taxon_of_origin in self.species:
                list_of_taxons_of_origin.append(self.species[taxon_of_origin])

            elif taxon_of_origin == "32644":
                # if the species is unkown
                list_of_taxons_of_origin.append("Unknow value")
            else:
                with open(folder_for_errors + "species_that_are_not_in_wikidata.txt", "a") as file:
                    file.write(taxon_of_origin + "\n")
    return list_of_taxons_of_origin


def create_information_objects_for_wikidata(self, Item, folder_for_errors="../doc/ERRORS/"):
    """
    This function has to be run for each cell line in cellosaurus.
    It create the information objects that will be in the Wikidata item
        for the cell line.

    :param Item: the Cellosaurus id for a cell line.
    :return : a dictionary composed of 2 dictionnaries:
        - data : is composed of information objects that are to add or
              update for the wikidata cell line item.
        - data_to_delete : is the information objects that are have to be
              deleted in this release for a wikidata cell line item.
    :folder_for_errors : The path to the folders where errors are stored.
    """

    information_to_insert_on_wikidata = []
    data_to_delete = []

    wikidata_reference_for_statement = get_WQ_reference(Item, cellosaurus_release_qid=self.releaseID)

    # CA         Category
    # CC         Comments
    if self.cellosaurus[Item]["CA"] == "NULL" or self.cellosaurus[Item]["CC"] == []:
        data_to_delete.append("P31")

    information_to_insert_on_wikidata = append_is_cell_ine(
        information_to_insert_on_wikidata,
        wikidata_reference_for_statement)

    information_to_insert_on_wikidata = append_is_contaminated(self,
                                                               Item,
                                                               information_to_insert_on_wikidata,
                                                               wikidata_reference_for_statement)

    information_to_insert_on_wikidata = append_category(self,
                                                        Item,
                                                        information_to_insert_on_wikidata,
                                                        wikidata_reference_for_statement)

    # DI : Diseases
    if not self.cellosaurus[Item]["DI"]:
        data_to_delete.append("P5166")

    else:
        information_to_insert_on_wikidata = append_diseases(self,
                                                            Item,
                                                            information_to_insert_on_wikidata,
                                                            reference=wikidata_reference_for_statement,
                                                            folder_for_errors=folder_for_errors)


    if self.cellosaurus[Item]["OX"]:
        data_to_delete.append("P703")

    list_of_taxons_of_origin = get_list_of_taxons(self, Item, folder_for_errors )


    # SX : Sex of cell line
    if not self.cellosaurus[Item]["SX"]:
        data_to_delete.append("P21")

    list_of_biological_sexes_of_source = []

    for biological_sex_of_source in self.cellosaurus[Item]["SX"]:

        if biological_sex_of_source == "Sex unspecified":

            # P21 : gender
            list_of_biological_sexes_of_source.append(wdi_core.WDString(
                value="Unknow value",
                prop_nr="P21",
                is_qualifier=True,
                snak_type='somevalue'))
        else:
            # else add the item corresponding to sex in sex or gender (P21)

            dict_for_human_genders = {"Female": "Q6581072",
                                      "Male": "Q6581097",
                                      "Sex ambiguous": "Q1097630"}

            dict_for_non_human_genders = {"Female": "Q43445",
                                          "Male": "Q44148",
                                          "Sex ambiguous": "Q28873047"}

            id_for_homo_sapiens = "Q15978631"
            if id_for_homo_sapiens in list_of_taxons_of_origin:
                biological_sex_id = dict_for_human_genders[biological_sex_of_source]

            else:
                if biological_sex_of_source == "Mixed sex":
                    biological_sex_id = "Q43445"
                    list_of_biological_sexes_of_source.append(wdi_core.WDItemID(
                        value="Q44148", prop_nr="P21", is_qualifier=True))
                else:
                    biological_sex_id = dict_for_non_human_genders[biological_sex_of_source]

            list_of_biological_sexes_of_source.append(wdi_core.WDItemID(
                value=biological_sex_id, prop_nr="P21", is_qualifier=True))

    # add species information in found in taxon (P703)
    if list_of_taxons_of_origin != []:

        for taxon_of_origin in list_of_taxons_of_origin:

            if taxon_of_origin == "Unknow value":
                information_to_insert_on_wikidata.append(wdi_core.WDString(
                    value="Unknow value",
                    prop_nr="P703",
                    qualifiers=list_of_biological_sexes_of_source,
                    references=wikidata_reference_for_statement,
                    snak_type='somevalue'))
            else:
                information_to_insert_on_wikidata.append(wdi_core.WDItemID(
                    value=taxon_of_origin, prop_nr="P703", qualifiers=list_of_biological_sexes_of_source,
                    references=wikidata_reference_for_statement))

    # HI         Hierarchy (parent cell line)
    if not self.cellosaurus[Item]["HI"]:
        data_to_delete.append("P3432")

    for parent_cell_line in self.cellosaurus[Item]["HI"]:
        if parent_cell_line in self.wikidata:
            # P3432 : parent cell line
            parent_cell_line_id = self.wikidata[parent_cell_line]
            information_to_insert_on_wikidata.append(make_statement(
                statement_property="P3432",
                statement_value=parent_cell_line_id,
                references=wikidata_reference_for_statement
            ))

        else:
            # if the parent cell line does not exist in Wikidata, add it in
            # AddParentCelline
            if Item not in self.AddParentCellline:
                self.AddParentCellline.append(Item)

    #  OI         Originate from same individual  (autologous cell line)
    #  P3578 : autologous cell line
    if not self.cellosaurus[Item]["OI"]:
        data_to_delete.append("P3578")

    else:
        for autologous_cell_line in self.cellosaurus[Item]["OI"]:
            if autologous_cell_line in self.wikidata:
                autologous_cell_line_id = self.wikidata[autologous_cell_line]
                information_to_insert_on_wikidata.append(make_statement(
                    statement_property="P3578",
                    statement_value=autologous_cell_line_id,
                    references=wikidata_reference_for_statement
                ))
            else:
                # if the autologous cell line does not exist in Wikidata, add
                # it in AddParentCelline
                if Item not in self.AddParentCellline:
                    self.AddParentCellline.append(Item)

    # P3289 : Cellosaurus ID
    information_to_insert_on_wikidata.append(wdi_core.WDExternalID(
        value=Item,
        prop_nr="P3289",
        references=wikidata_reference_for_statement))

    # check if external reference in CLO, BTO, EFO, BCGO exists
    for cell_line_id in ["CLO", "BTO", "EFO", "BCGO"]:
        if not self.cellosaurus[Item][cell_line_id]:
            data_to_delete.append("P2888")

    if self.cellosaurus[Item]["MeSH"] != "NULL":
        # P486 : MeSH ID
        information_to_insert_on_wikidata.append(wdi_core.WDExternalID(
            value=self.cellosaurus[Item]["MeSH"],
            prop_nr="P486",
            references=wikidata_reference_for_statement))
    else:
        data_to_delete.append("P486")

    if self.cellosaurus[Item]["CLO"]:
        for CLO in self.cellosaurus[Item]["CLO"]:
            # P2888: exact match
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + CLO,
                prop_nr="P2888",
                references=wikidata_reference_for_statement))

    if self.cellosaurus[Item]["BTO"]:
        for BTO in self.cellosaurus[Item]["BTO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BTO,
                prop_nr="2888",
                references=wikidata_reference_for_statement))

    if self.cellosaurus[Item]["EFO"]:
        for EFO in self.cellosaurus[Item]["EFO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + EFO,
                prop_nr="2888",
                references=wikidata_reference_for_statement))

    if self.cellosaurus[Item]["BCGO"]:
        for BCGO in self.cellosaurus[Item]["BCGO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BCGO,
                prop_nr="2888",
                references=wikidata_reference_for_statement))

    #  RX         References identifiers
    if self.cellosaurus[Item]["RX"]:

        for reference in self.cellosaurus[Item]["RX"]:

            if reference.startswith("PubMed"):
                pubmed = reference.strip("PubMed=")

                if pubmed in self.references:
                    # P1343:described by source
                    information_to_insert_on_wikidata.append(wdi_core.WDItemID(
                        value=self.references[pubmed],
                        prop_nr="P1343",
                        references=wikidata_reference_for_statement))

            elif reference.startswith("DOI"):
                doi = reference.strip("DOI=")

                if doi in self.references:
                    information_to_insert_on_wikidata.append(wdi_core.WDItemID(
                        value=self.references[doi],
                        prop_nr="P1343",
                        references=wikidata_reference_for_statement))
    else:
        data_to_delete.append("P1343")

    return {'data': information_to_insert_on_wikidata, 'data_to_delete': data_to_delete}
