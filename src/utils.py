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

class CellossaurusCellLine():
    """
    :param wdi_login : wdi_login object
    :param release_qid: the wikidata qid for the Cellosaurus release of interest.
    :param cellosaurus_dump : the  dictionary which contains cellosaurus dump information.
    :param wikidata_dictionary_with_existing_cell_lines :  wikidata cell lines items that already exit.
    :param references : the references dictionary creating with correspondance function.
    :param species : the species dictionary creating with correspondance function.
    :param cell_line_categories : the categories dictionary creating with  categories function.
    :param diseases : the diseases dictionary creating with correspondance function.
    :param wdi_cell_line_to_add : the cell line information to add in Wikidata Integrator format
    :param wdi_cell_line_to_delete : the cell line information to delete in Wikidata Integrator format
    :param cell_line_dump : the cellosaurus dump specific for this cell line

    """

    def __init__(self, wdi_login_object='', release_qid='', cellosaurus_dump='',
                 wikidata_dictionary_with_existing_cell_lines='', references='',
                 species='', cell_line_categories='', diseases='', cell_line_id=""):
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
        :param cell_line_categories : the categories dictionary creating with
            categories function.
        :param diseases : the diseases dictionary creating with
            correspondance function.

        """

        self.wdi_login_object = wdi_login_object
        self.release_qid = release_qid
        self.cellosaurus_dump = cellosaurus_dump
        self.wikidata_dictionary_with_existing_cell_lines = wikidata_dictionary_with_existing_cell_lines
        self.references = references
        self.species = species
        self.cell_line_categories = cell_line_categories
        self.diseases = diseases
        self.cell_line_id = cell_line_id

        self.cell_line_dump = cellosaurus_dump[cell_line_id]
        self.references_in_wdi_format = get_WQ_reference(self.cell_line_id,
                                                         cellosaurus_release_qid=self.release_qid)

        self.wdi_cell_line_to_add = []
        self.wdi_cell_line_to_delete =  []

        self.parent_cell_line_to_add = []
        self.PublicationNotReferencing = []
        self.WIDs = []



    def prepare_for_wikidata(self, folder_for_errors="doc/ERRORS/"):
        data_to_add_to_wikidata = []
        data_to_delete = []
        data_to_delete = verify_empty_fields_and_add_as_data_to_delete(self, data_to_delete)

        data_to_add_to_wikidata = add_info_about_the_cell_line_identity(self, data_to_add_to_wikidata)

        data_to_add_to_wikidata = add_info_about_the_cell_line_source(self, self.cell_line_id,
                                                                                data_to_add_to_wikidata,
                                                                                wikidata_reference_for_statement,
                                                                                folder_for_errors)

        data_to_add_to_wikidata = add_info_about_related_cell_lines(self, self.cell_line_id,
                                                                              data_to_add_to_wikidata,
                                                                              wikidata_reference_for_statement)

        data_to_add_to_wikidata = append_cellosaurus_id(self.cell_line_id,
                                                                  data_to_add_to_wikidata,
                                                                  reference=wikidata_reference_for_statement)

        data_to_add_to_wikidata = add_info_about_identifiers(self,
                                                                       self.cell_line_id,
                                                                       data_to_add_to_wikidata,
                                                                       wikidata_reference_for_statement)

        data_to_add_to_wikidata = add_info_about_references(self,
                                                                      self.cell_line_id,
                                                                      data_to_add_to_wikidata,
                                                                      wikidata_reference_for_statement)
        return {'data': data_to_add_to_wikidata, 'data_to_delete': data_to_delete}


def verify_empty_fields_and_add_as_data_to_delete(cell_line_object, data_to_delete):

    cell_line_dump = cell_line_object.cell_line_dump

    cell_line_comments = cell_line_dump["CC"]
    cell_line_category = cell_line_dump["CA"]

    if cell_line_category == "NULL" or cell_line_comments == []:
        data_to_delete.append("P31")

    cell_line_taxon_of_origin = cell_line_dump["OX"]
    if cell_line_taxon_of_origin:
        data_to_delete.append("P703")

    parent_cell_line = cell_line_dump["HI"]
    if not parent_cell_line:
        data_to_delete.append("P3432")

    cell_line_diseases_of_source = cell_line_dump["DI"]
    if not cell_line_diseases_of_source:
        data_to_delete.append("P5166")

    cell_line_sex_of_source = cell_line_dump["SX"]
    if not cell_line_sex_of_source:
        data_to_delete.append("P21")

    autologous_cell_line = cell_line_dump["OI"]
    if not autologous_cell_line:
        data_to_delete.append("P3578")

    for ontology_name in ["CLO", "BTO", "EFO", "BCGO"]:
        if not cell_line_dump[ontology_name]:
            data_to_delete.append("P2888")

    if cell_line_dump["MeSH"] == "NULL":
        data_to_delete.append("P486")

    cell_line_describing_source_references = cell_line_dump["RX"]
    if cell_line_describing_source_references:
        data_to_delete.append("P1343")

    return data_to_delete


def add_info_about_the_cell_line_identity(cell_line_object,
                                          data_to_add_to_wikidata):

    data_to_add_to_wikidata = append_is_cell_ine(data_to_add_to_wikidata, cell_line_object.references_in_wdi_format)

    data_to_add_to_wikidata = append_is_contaminated(cell_line_object, data_to_add_to_wikidata)

    data_to_add_to_wikidata = append_category(cell_line_object, data_to_add_to_wikidata)
    return data_to_add_to_wikidata


def append_is_contaminated(cell_line_object, data_to_add_to_wikidata):
    cell_line_comments = cell_line_object.cell_line_dump  ["CC"]
    if cell_line_comments:
        data_to_add_to_wikidata.append(make_instance_of_contaminated_cell_line_statement(
            reference=cell_line_object.references_in_wdi_format
        ))
    return data_to_add_to_wikidata


def append_category(cell_line_object, data_to_add_to_wikidata):

    cell_line_category = cell_line_object.cell_line_dump["CA"]
    category_to_wikidata = cell_line_object.cell_line_categories

    if cell_line_category in category_to_wikidata:
        cell_line_category_id = category_to_wikidata[cell_line_category]
        data_to_add_to_wikidata.append(make_instance_of_statement(
            statement_value=cell_line_category_id,
            reference=cell_line_object.references_in_wdi_format
        ))

    return data_to_add_to_wikidata


def Set(cellosaurus, cellosaurus_cell_line_id):
    return prepare_item_label_and_descriptions(cellosaurus, cellosaurus_cell_line_id)


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


# Functions to query and match to Wikidata
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
                            if not query:
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


def get_WQ_reference(cellosaurus_cell_line_id, cellosaurus_release_qid):
    release = wdi_core.WDItemID(
        value=cellosaurus_release_qid, prop_nr="P248", is_reference=True)

    date = datetime.now()
    timeStringNow = date.strftime("+%Y-%m-%dT00:00:00Z")
    refRetrieved = wdi_core.WDTime(
        timeStringNow, prop_nr='P813', is_reference=True)

    cellosaurusref = wdi_core.WDExternalID(
        value=cellosaurus_cell_line_id, prop_nr="P3289", is_reference=True)

    WQreference = [[release, refRetrieved, cellosaurusref]]
    return (WQreference)



# Functions to that wrap different Wikidata Integrator statements to the list of statements


def add_info_about_the_cell_line_source(self, cellosaurus_cell_line_id,
                                        information_to_insert_on_wikidata,
                                        wikidata_reference_for_statement,
                                        folder_for_errors):
    information_to_insert_on_wikidata = append_diseases(self,
                                                        cellosaurus_cell_line_id,
                                                        information_to_insert_on_wikidata,
                                                        reference=wikidata_reference_for_statement,
                                                        folder_for_errors=folder_for_errors)

    list_of_taxons_of_origin = get_list_of_taxons(self, cellosaurus_cell_line_id, folder_for_errors)

    list_of_biological_sexes_of_source = get_list_of_biological_sexes(self, cellosaurus_cell_line_id, list_of_taxons_of_origin)

    information_to_insert_on_wikidata = append_taxon_and_gender(information_to_insert_on_wikidata,
                                                                list_of_taxons_of_origin,
                                                                list_of_biological_sexes_of_source,
                                                                references=wikidata_reference_for_statement)
    return information_to_insert_on_wikidata


def add_info_about_related_cell_lines(self, cellosaurus_cell_line_id,
                                      information_to_insert_on_wikidata,
                                      wikidata_reference_for_statement):
    for parent_cell_line in self.cellosaurus[cellosaurus_cell_line_id]["HI"]:

        information_to_insert_on_wikidata = append_parent_cell_line(self, parent_cell_line,
                                                                    information_to_insert_on_wikidata,
                                                                    reference=wikidata_reference_for_statement)
        if cellosaurus_cell_line_id not in self.AddParentCellline:
            self.AddParentCellline.append(cellosaurus_cell_line_id)

    if self.cellosaurus[cellosaurus_cell_line_id]["OI"]:
        for autologous_cell_line in self.cellosaurus[cellosaurus_cell_line_id]["OI"]:
            information_to_insert_on_wikidata = append_autologous_cell_line(self, autologous_cell_line,
                                                                            information_to_insert_on_wikidata,
                                                                            reference=wikidata_reference_for_statement)
            if cellosaurus_cell_line_id not in self.AddParentCellline:
                self.AddParentCellline.append(cellosaurus_cell_line_id)

    return information_to_insert_on_wikidata


def add_info_about_identifiers(self, cellosaurus_cell_line_id,
                               information_to_insert_on_wikidata,
                               wikidata_reference_for_statement):
    if self.cellosaurus[cellosaurus_cell_line_id]["MeSH"] != "NULL":
        information_to_insert_on_wikidata = append_mesh_id(self, cellosaurus_cell_line_id, information_to_insert_on_wikidata,
                                                           reference=wikidata_reference_for_statement)

    information_to_insert_on_wikidata = append_obo_exact_matches(self, cellosaurus_cell_line_id, information_to_insert_on_wikidata,
                                                                 reference=wikidata_reference_for_statement)
    return information_to_insert_on_wikidata


def add_info_about_references(self, cellosaurus_cell_line_id,
                              information_to_insert_on_wikidata,
                              wikidata_reference_for_statement):
    #  RX         References identifiers
    if self.cellosaurus[cellosaurus_cell_line_id]["RX"]:
        information_to_insert_on_wikidata = append_literature_descriptions(self, cellosaurus_cell_line_id,
                                                                           information_to_insert_on_wikidata,
                                                                           wikidata_reference_for_statement)
    return information_to_insert_on_wikidata


def append_obo_exact_matches(self, cellosaurus_cell_line_id, information_to_insert_on_wikidata, reference):
    if self.cellosaurus[cellosaurus_cell_line_id]["CLO"]:
        for CLO in self.cellosaurus[cellosaurus_cell_line_id]["CLO"]:
            # P2888: exact match
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + CLO,
                prop_nr="P2888",
                references=reference))

    if self.cellosaurus[cellosaurus_cell_line_id]["BTO"]:
        for BTO in self.cellosaurus[cellosaurus_cell_line_id]["BTO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BTO,
                prop_nr="2888",
                references=reference))

    if self.cellosaurus[cellosaurus_cell_line_id]["EFO"]:
        for EFO in self.cellosaurus[cellosaurus_cell_line_id]["EFO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + EFO,
                prop_nr="2888",
                references=reference))

    if self.cellosaurus[cellosaurus_cell_line_id]["BCGO"]:
        for BCGO in self.cellosaurus[cellosaurus_cell_line_id]["BCGO"]:
            information_to_insert_on_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BCGO,
                prop_nr="2888",
                references=reference))
    return information_to_insert_on_wikidata


# Functions to append Wikidata Integrator statements to the list of statements
def append_literature_descriptions(self, cellosaurus_cell_line_id, information_to_insert_on_wikidata, wikidata_reference_for_statement):
    for reference in self.cellosaurus[cellosaurus_cell_line_id]["RX"]:

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

    return information_to_insert_on_wikidata


def append_taxon_and_gender(information_to_insert_on_wikidata,
                            list_of_taxons_of_origin, list_of_biological_sexes_of_source, references):
    if list_of_taxons_of_origin:
        for taxon_of_origin in list_of_taxons_of_origin:

            if taxon_of_origin == "Unknow value":
                information_to_insert_on_wikidata.append(wdi_core.WDString(
                    value="Unknow value",
                    prop_nr="P703",
                    qualifiers=list_of_biological_sexes_of_source,
                    references=references,
                    snak_type='somevalue'))
            else:
                information_to_insert_on_wikidata.append(wdi_core.WDItemID(
                    value=taxon_of_origin, prop_nr="P703", qualifiers=list_of_biological_sexes_of_source,
                    references=references))

    return information_to_insert_on_wikidata


def get_list_of_taxons(self, cellosaurus_cell_line_id, folder_for_errors):
    # OX : Taxon od origin
    # P703 : Found in taxon
    list_of_taxons_of_origin = []

    if self.cellosaurus[cellosaurus_cell_line_id]["OX"]:

        for taxon_of_origin in self.cellosaurus[cellosaurus_cell_line_id]["OX"]:

            # Format is TaxID=9606 (example)
            # It is split to get "9606"
            taxon_of_origin = taxon_of_origin.split("=")[1]
            print(taxon_of_origin)
            if taxon_of_origin in self.species:
                list_of_taxons_of_origin.append(self.species[taxon_of_origin])

            elif taxon_of_origin == "32644":
                # if the species is unkown
                list_of_taxons_of_origin.append("Unknow value")
            else:
                with open(folder_for_errors + "species_that_are_not_in_wikidata.txt", "a") as file:
                    file.write(taxon_of_origin + "\n")

    return list_of_taxons_of_origin


def get_list_of_biological_sexes(self, cellosaurus_cell_line_id, list_of_taxons_of_origin):
    list_of_biological_sexes_of_source = []

    for biological_sex_of_source in self.cellosaurus[cellosaurus_cell_line_id]["SX"]:

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

    return list_of_biological_sexes_of_source


def append_is_cell_ine(information_to_insert_on_wikidata, reference):
    information_to_insert_on_wikidata.append(make_instance_of_cell_line_statement(
        reference=reference
    ))
    return information_to_insert_on_wikidata


def append_diseases(self, cellosaurus_cell_line_id, information_to_insert_on_wikidata,
                    reference, folder_for_errors):
    if self.cellosaurus[cellosaurus_cell_line_id]["DI"]:
        diseases_in_wikidata = self.diseases

        for disease in self.cellosaurus[cellosaurus_cell_line_id]["DI"]:
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


def append_parent_cell_line(self, parent_cell_line, information_to_insert_on_wikidata, reference):
    if parent_cell_line in self.wikidata:
        # P3432 : parent cell line
        parent_cell_line_id = self.wikidata[parent_cell_line]
        information_to_insert_on_wikidata.append(make_statement(
            statement_property="P3432",
            statement_value=parent_cell_line_id,
            references=reference
        ))
    return information_to_insert_on_wikidata


def append_autologous_cell_line(self, autologous_cell_line, information_to_insert_on_wikidata, reference):
    if autologous_cell_line in self.wikidata:
        autologous_cell_line_id = self.wikidata[autologous_cell_line]
        information_to_insert_on_wikidata.append(make_statement(
            statement_property="P3578",
            statement_value=autologous_cell_line_id,
            references=reference
        ))
    return information_to_insert_on_wikidata


def append_cellosaurus_id(cellosaurus_cell_line_id, information_to_insert_on_wikidata, reference):
    # P3289 : Cellosaurus ID
    information_to_insert_on_wikidata.append(wdi_core.WDExternalID(
        value=cellosaurus_cell_line_id,
        prop_nr="P3289",
        references=reference))

    return information_to_insert_on_wikidata


def append_mesh_id(self, Item, information_to_insert_on_wikidata, reference):
    # P486 : MeSH ID
    information_to_insert_on_wikidata.append(wdi_core.WDExternalID(
        value=self.cellosaurus[Item]["MeSH"],
        prop_nr="P486",
        references=reference))
    return information_to_insert_on_wikidata


# Functions to make statements in the Wikidata Integrator format

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


def add_statements_to_cell_line_item_ready_for_update(self, cellosaurus_cell_line_id, data):
    item = wdi_core.WDItemEngine(wd_item_id=self.wikidata[cellosaurus_cell_line_id], data=data['data'],
                                 global_ref_mode='STRICT_OVERWRITE', fast_run=True, fast_run_base_filter={
            'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '', 'P248': '', 'P3289': '',
            'P486': '', 'P2888': '', 'P1343': '', 'P5166': '', 'P813': ''}, fast_run_use_refs=True)

    return item


def add_labels_and_descriptions_to_cell_line_item_ready_for_update(self, cellosaurus_cell_line_id,
                                                                   item_with_statements_to_update,
                                                                   label,
                                                                   descriptions):
    if self.cellosaurus[cellosaurus_cell_line_id] != "NUL":
        item_with_statements_to_update.set_aliases(
            self.cellosaurus[cellosaurus_cell_line_id]["SY"], lang='en', append=False)

    for lang, description in descriptions.items():
        item_with_statements_to_update.set_description(description, lang=lang)
        item_with_statements_to_update.set_label(label=label, lang=lang)

    return item_with_statements_to_update


# Functions that actually interact with Wikidata API
def update_wikidata_entry_for_this_cell_line(self, cellosaurus_cell_line_id, data):
    label = prepare_item_label_and_descriptions(self.cellosaurus, cellosaurus_cell_line_id)['name']
    descriptions = prepare_item_label_and_descriptions(self.cellosaurus, cellosaurus_cell_line_id)['descriptions']

    delete_old_statements(self, cellosaurus_cell_line_id, data)

    item_with_statements_to_update = add_statements_to_cell_line_item_ready_for_update(self, cellosaurus_cell_line_id, data)

    item_with_statements_to_update_with_labels = add_labels_and_descriptions_to_cell_line_item_ready_for_update(self,
                                                                                                                cellosaurus_cell_line_id,
                                                                                                                item_with_statements_to_update,
                                                                                                                label,
                                                                                                                descriptions)
    item_with_statements_to_update_with_labels.write(self.login,
                                                     bot_account=True,
                                                     edit_summary="update item {}".format(
                                                         self.cellosaurus[cellosaurus_cell_line_id]["ID"]))


def delete_old_statements(self, cellosaurus_cell_line_id, data):
    statements_to_delete = []

    if data['data_to_delete']:
        wikidata_item_for_this_cell_line = wdi_core.WDItemEngine(wd_item_id=self.wikidata[cellosaurus_cell_line_id])
        wikidata_item_for_this_cell_line_json = wikidata_item_for_this_cell_line.get_wd_json_representation()

        for statement in wikidata_item_for_this_cell_line_json['claims']:
            if statement in data['data_to_delete']:
                statements_to_delete.append(
                    wdi_core.WDBaseDataType.delete_statement(prop_nr=statement))

        item_deletion = wdi_core.WDItemEngine(
            wd_item_id=self.wikidata[cellosaurus_cell_line_id], data=statements_to_delete)

        item_name = self.cellosaurus[cellosaurus_cell_line_id]["ID"]
        item_deletion.write(self.login, bot_account=False,
                            edit_summary="delete statements before update the item {}".format(item_name))


def prepare_item_label_and_descriptions(cellosaurus, cellosaurus_cell_line_id):
    """
    This function is using for give name and description in english, french
    and deutch.
    :param cellosaurus_cell_line_id : the Cellosaurus id for a cell line.
    :return : dictionnaries with the name and the description in english, french and deutch
    """

    label = cellosaurus[cellosaurus_cell_line_id]["ID"]

    descriptions = {
        "en": "cell line",
        "fr": "lignée cellulaire",
        "de": "Zelllinie",
        "pt": "linhagem celular"
    }

    if " [" in label:
        namecompose = label.split("[")
        descriptions = {
            "en": "cell line" + " (" + namecompose[1].strip("]") + ")",
            "fr": "lignée cellulaire" + " (" + namecompose[1].strip("]") + ")",
            "de": "Zelllinie" + " (" + namecompose[1].strip("]") + ")"
        }
        label = namecompose[0].strip(" ")

    return {'name': label, 'descriptions': descriptions}


def create_wikidata_entry_for_this_cell_line(self, cellosaurus_cell_line_id, data):
    """
    This function create a Wikidata item for the cell line with
        cellosaurus informations.
    :param cellosaurus_cell_line_id : the Cellosaurus id for a cell line.
    :param data : the dictionary from InitialisationData function.
    :return : WikidataID.txt, a file which contains the Wikidata cell
        lines items created.
    """
    item = wdi_core.WDItemEngine(data=data['data'], global_ref_mode='STRICT_OVERWRITE', fast_run=True,
                                 fast_run_base_filter={
                                     'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '',
                                     'P248': '', 'P3289': '', 'P486': '', 'P2888': '', 'P1343': '', 'P5166': '',
                                     'P813': ''}, fast_run_use_refs=True)
    #  SY         Synonyms
    if self.cellosaurus[cellosaurus_cell_line_id]["SY"]:
        item.set_aliases(
            self.cellosaurus[cellosaurus_cell_line_id]["SY"], lang='en', append=False)

    for lang, description in prepare_item_label_and_descriptions(self.cellosaurus, cellosaurus_cell_line_id)['descriptions'].items():
        item.set_description(description, lang=lang)
        item.set_label(label=prepare_item_label_and_descriptions(self.cellosaurus, cellosaurus_cell_line_id)['name'], lang=lang)

    with open("./results/WikidataID.txt", "a") as file:
        newly_created_item_qid = item.write(self.login, bot_account=True, edit_summary="create item {}".format(
            self.cellosaurus[cellosaurus_cell_line_id]["ID"]))
        file.write(newly_created_item_qid + "\t" + cellosaurus_cell_line_id + "\n")
