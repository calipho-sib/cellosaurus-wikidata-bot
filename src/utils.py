#!/usr/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
from tqdm import tqdm
import time
import calendar
from datetime import datetime, date
import json
import pickle
import os

"""
Contain the main functions for Wikidata Cellosaurus Bot
"""

def get_cell_line_category_to_wikidata(file):
    """
    Get categories for cell lines matched to wikidata items from a tab separeted file.
    :param file : a file which contains categories for cell lines and their wikidata qids
    :return : a dictionary, in key the category name, in value the wikidata
        item id corresponding
    """
    cell_line_category_to_wikidata = {}
    with open(file) as file:
        for line in file:
            line = line.split(" (")
            name_on_cellosaurus = line[0]
            category_qid = line[1].strip(")\n")
            cell_line_category_to_wikidata[name_on_cellosaurus] = category_qid
        return cell_line_category_to_wikidata


def match_cellosaurus_dump_to_wikidata_items(cellosaurus):
    return match_cellosaurus_to_wikidata_items(cellosaurus)


def format_cellosaurus_dump_as_dictionary(file):
    """
    Format Cellosaurus dump (.txt) in a dictionary with the informations that
        will integrating in Wikidata.
    :param file : the cellosaurus dump at .txt format
    :return :  a dictionary. In key, the Cellosaurus id for the cell line. In
        value, the informations on the cell line (name, aliases, external ids,
        species of origin, parent cell line, references, autologous cell line,
        sex of the species of origin, ctaegory of the cell line, etc...)
    """
    cellosaurus_dump_as_dictionary = {}
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
                cellosaurus_dump_as_dictionary[AC] = {"ID": ID,
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
        return cellosaurus_dump_as_dictionary


class CellosaurusCellLine():
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
    :param cell_line_id : the cellosaurus_id for this cell line

    """

    def __init__(self, wdi_login_object='', release_qid='', cellosaurus_dump='',
                 wikidata_dictionary_with_existing_cell_lines='', references='',
                 species='', cell_line_categories='', diseases='', cell_line_id=""):
        """
        :param login : login correspond to a wdi_login object (..seealso::
            login in Main.py).
        :param releaseID : the wikidata item id which corresponding to the
            Cellosaurus release.
        :param cellosaurus_dump : the cellosaurus dictionary which contains
            cellosaurus dump information.
        :param wikidata : the wikidata dictionary which contains wikidata
            cell lines items that already exit.
        :param references : the references dictionary created with
            "match_cellosaurus_to_wikidata_items" function.
        :param species : the species dictionary creating with correspondance
            function.
        :param cell_line_categories : the categories dictionary creating with
            "get_cell_line_category_to_wikidata" function.
        :param diseases : the diseases dictionary created with
            "match_cellosaurus_to_wikidata_items" function.

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
        self.wdi_cell_line_to_delete = []

        self.related_cell_line_to_add = []
        self.PublicationNotReferencing = []
        self.WIDs = []

    def prepare_for_wikidata(self, folder_for_errors="doc/ERRORS/"):
        data_to_add_to_wikidata = []
        data_to_delete = []
        data_to_delete = verify_empty_fields_and_add_as_data_to_delete(self, data_to_delete)

        data_to_add_to_wikidata = add_info_about_the_cell_line_identity(self, data_to_add_to_wikidata)

        data_to_add_to_wikidata = add_info_about_the_cell_line_source(self, data_to_add_to_wikidata,
                                                                      folder_for_errors)

        data_to_add_to_wikidata, related_cell_line_to_add = add_info_about_related_cell_lines(self,
                                                                                              data_to_add_to_wikidata)

        self.related_cell_line_to_add = related_cell_line_to_add

        data_to_add_to_wikidata = append_cellosaurus_id(self.cell_line_id,
                                                        data_to_add_to_wikidata,
                                                        reference=self.references_in_wdi_format)

        data_to_add_to_wikidata = add_info_about_identifiers(self, data_to_add_to_wikidata)

        data_to_add_to_wikidata = add_info_about_references(self, data_to_add_to_wikidata)
        return {'data': data_to_add_to_wikidata, 'data_to_delete': data_to_delete}

    def update_line_on_wikidata(self, data):
        label = self.cell_line_dump["ID"]

        if " [" in label:
            label = label.split("[")[0].strip(" ")
        descriptions = prepare_item_descriptions(self)

        delete_old_statements(self, data)

        item_with_statements_to_update = add_all_statements_to_wdi_cell_line(self, data)

        item_with_statements_to_update_with_labels = add_labels_and_descriptions_to_cell_line_item_ready_for_update(
            self,
            item_with_statements_to_update,
            label,
            descriptions)

        cell_line_item = self.cell_line_dump["ID"]
        item_with_statements_to_update_with_labels.write(self.wdi_login_object,
                                                         bot_account=True,
                                                         edit_summary="update item {}".format(
                                                             cell_line_item
                                                                                              ))


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


def append_is_cell_ine(information_to_insert_on_wikidata, reference):
    information_to_insert_on_wikidata.append(make_instance_of_cell_line_statement(
        reference=reference
    ))
    return information_to_insert_on_wikidata


def append_is_contaminated(cell_line_object, data_to_add_to_wikidata):
    cell_line_comments = cell_line_object.cell_line_dump["CC"]
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


def add_info_about_the_cell_line_source(cell_line_object, data_to_add_to_wikidata,
                                        folder_for_errors):
    data_to_add_to_wikidata = append_diseases(cell_line_object,
                                              data_to_add_to_wikidata,
                                              folder_for_errors=folder_for_errors)

    list_of_taxons_of_origin = get_list_of_taxons(cell_line_object, folder_for_errors)

    list_of_biological_sexes_of_source = get_list_of_biological_sexes(cell_line_object,
                                                                      list_of_taxons_of_origin)

    data_to_add_to_wikidata = append_taxon_and_gender(cell_line_object,
                                                      data_to_add_to_wikidata,
                                                      list_of_taxons_of_origin,
                                                      list_of_biological_sexes_of_source)
    return data_to_add_to_wikidata


def append_diseases(cell_line_object, data_to_add_to_wikidata, folder_for_errors):
    reference = cell_line_object.references_in_wdi_format
    cell_line_diseases_of_source = cell_line_object.cell_line_dump["DI"]
    diseases_in_wikidata = cell_line_object.diseases

    if cell_line_diseases_of_source:
        for disease in cell_line_diseases_of_source:
            if disease in diseases_in_wikidata:
                disease_id = diseases_in_wikidata[disease]

                data_to_add_to_wikidata.append(make_established_from_disease_statement(
                    disease_id=disease_id,
                    references=reference
                ))

            else:
                with open(folder_for_errors + "diseases/diseases_not_in_wikidata.txt", "a") as file:
                    file.write(disease + "\n")
    return data_to_add_to_wikidata


def append_taxon_and_gender(cell_line_object, data_to_add_to_wikidata,
                            list_of_taxons_of_origin, list_of_biological_sexes_of_source):
    references_for_this_cell_line = cell_line_object.references_in_wdi_format

    if list_of_taxons_of_origin:
        for taxon_of_origin in list_of_taxons_of_origin:

            if taxon_of_origin == "Unknow value":
                data_to_add_to_wikidata.append(wdi_core.WDString(
                    value="Unknow value", prop_nr="P703", qualifiers=list_of_biological_sexes_of_source,
                    references=references_for_this_cell_line,
                    snak_type='somevalue'))
            else:
                data_to_add_to_wikidata.append(wdi_core.WDItemID(
                    value=taxon_of_origin, prop_nr="P703", qualifiers=list_of_biological_sexes_of_source,
                    references=references_for_this_cell_line))

    return data_to_add_to_wikidata


def get_list_of_biological_sexes(cell_line_object, list_of_taxons_of_origin):
    list_of_biological_sexes_of_source = []

    cell_line_sexes_of_source = cell_line_object.cell_line_dump["SX"]

    for biological_sex_of_source in cell_line_sexes_of_source:

        if biological_sex_of_source == "Sex unspecified":
            list_of_biological_sexes_of_source.append(wdi_core.WDString(
                value="Unknow value", prop_nr="P21", is_qualifier=True, snak_type='somevalue'))

        else:
            dict_for_human_sexes = {"Female": "Q6581072",
                                    "Male": "Q6581097",
                                    "Sex ambiguous": "Q1097630"}

            dict_for_non_human_sexes = {"Female": "Q43445",
                                        "Male": "Q44148",
                                        "Sex ambiguous": "Q28873047"}

            id_for_homo_sapiens = "Q15978631"

            if id_for_homo_sapiens in list_of_taxons_of_origin:
                biological_sex_id = dict_for_human_sexes[biological_sex_of_source]

            else:
                if biological_sex_of_source == "Mixed sex":
                    biological_sex_id = "Q43445"
                    list_of_biological_sexes_of_source.append(wdi_core.WDItemID(
                        value="Q44148", prop_nr="P21", is_qualifier=True))

                else:
                    biological_sex_id = dict_for_non_human_sexes[biological_sex_of_source]

            list_of_biological_sexes_of_source.append(wdi_core.WDItemID(
                value=biological_sex_id, prop_nr="P21", is_qualifier=True))

    return list_of_biological_sexes_of_source


def get_list_of_taxons(cell_line_object, folder_for_errors):
    # OX : Taxon od origin
    # P703 : Found in taxon
    list_of_taxons_of_origin = []
    cell_line_taxons = cell_line_object.cell_line_dump["OX"]

    wikidata_species = cell_line_object.species

    if cell_line_taxons:

        for taxon_of_origin in cell_line_taxons:
            # Format is TaxID=9606 (example)
            # It is split to get "9606"
            taxon_of_origin = taxon_of_origin.split("=")[1]

            if taxon_of_origin in wikidata_species:
                wikidata_taxon_qid = wikidata_species[taxon_of_origin]
                list_of_taxons_of_origin.append(wikidata_taxon_qid)

            elif taxon_of_origin == "32644":
                # if the species is unknow
                list_of_taxons_of_origin.append("Unknow value")

            else:
                with open(folder_for_errors + "species_that_are_not_in_wikidata.txt", "a") as file:
                    file.write(taxon_of_origin + "\n")

    return list_of_taxons_of_origin


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


def add_info_about_related_cell_lines(cell_line_object, data_to_add_to_wikidata):
    parent_cell_lines = cell_line_object.cell_line_dump["HI"]
    wikidata_reference_for_statement = cell_line_object.references_in_wdi_format
    cellosaurus_cell_line_id = cell_line_object.cell_line_id
    for parent_cell_line in parent_cell_lines:

        data_to_add_to_wikidata = append_parent_cell_line(cell_line_object, parent_cell_line,
                                                          data_to_add_to_wikidata)

        list_of_related_cell_lines_to_add = cell_line_object.related_cell_line_to_add
        if cellosaurus_cell_line_id not in list_of_related_cell_lines_to_add:
            cell_line_object.related_cell_line_to_add.append(cellosaurus_cell_line_id)

    cell_lines_from_same_individual = cell_line_object.cell_line_dump["OI"]
    if cell_lines_from_same_individual:
        for autologous_cell_line in cell_lines_from_same_individual:
            data_to_add_to_wikidata = append_autologous_cell_line(cell_line_object, autologous_cell_line,
                                                                  data_to_add_to_wikidata)
            if cellosaurus_cell_line_id not in cell_line_object.related_cell_line_to_add:
                cell_line_object.related_cell_line_to_add.append(cellosaurus_cell_line_id)

    return data_to_add_to_wikidata, cell_line_object.related_cell_line_to_add


def append_parent_cell_line(cell_line_object, parent_cell_line, data_to_add_to_wikidata):
    reference = cell_line_object.references_in_wdi_format
    cell_lines_in_wikidata = cell_line_object.wikidata_dictionary_with_existing_cell_lines
    if parent_cell_line in cell_lines_in_wikidata:
        # P3432 : parent cell line
        parent_cell_line_id = cell_lines_in_wikidata[parent_cell_line]
        data_to_add_to_wikidata.append(make_statement(
            statement_property="P3432",
            statement_value=parent_cell_line_id,
            references=reference
        ))
    return data_to_add_to_wikidata


def append_autologous_cell_line(cell_line_object, autologous_cell_line, data_to_add_to_wikidata):
    cell_lines_in_wikidata = cell_line_object.wikidata_dictionary_with_existing_cell_lines
    reference = cell_line_object.references_in_wdi_format
    if autologous_cell_line in cell_lines_in_wikidata:
        autologous_cell_line_id = cell_lines_in_wikidata[autologous_cell_line]
        data_to_add_to_wikidata.append(make_statement(
            statement_property="P3578",
            statement_value=autologous_cell_line_id,
            references=reference
        ))
    return data_to_add_to_wikidata


def add_info_about_identifiers(cell_line_object, data_to_add_to_wikidata):
    data_to_add_to_wikidata = append_mesh_id(cell_line_object, data_to_add_to_wikidata)
    data_to_add_to_wikidata = append_obo_exact_matches(cell_line_object, data_to_add_to_wikidata)
    return data_to_add_to_wikidata


def append_mesh_id(cell_line_object, data_to_add_to_wikidata):
    # P486 : MeSH ID
    cell_line_mesh = cell_line_object.cell_line_dump["MeSH"]

    reference = cell_line_object.references_in_wdi_format
    if cell_line_mesh != "NULL":
        data_to_add_to_wikidata.append(wdi_core.WDExternalID(
            value=cell_line_object.cell_line_dump["MeSH"],
            prop_nr="P486",
            references=reference))
    return data_to_add_to_wikidata


def append_obo_exact_matches(cell_line_object, data_to_add_to_wikidata):
    reference = cell_line_object.references_in_wdi_format

    cell_line_dump = cell_line_object.cell_line_dump
    if cell_line_dump["CLO"]:
        for CLO in cell_line_dump["CLO"]:
            # P2888: exact match
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + CLO,
                prop_nr="P2888",
                references=reference))

    if cell_line_dump["BTO"]:
        for BTO in cell_line_dump["BTO"]:
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BTO,
                prop_nr="2888",
                references=reference))

    if cell_line_dump["EFO"]:
        for EFO in cell_line_dump["EFO"]:
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + EFO,
                prop_nr="2888",
                references=reference))

    if cell_line_dump["BCGO"]:
        for BCGO in cell_line_dump["BCGO"]:
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BCGO,
                prop_nr="2888",
                references=reference))
    return data_to_add_to_wikidata


def add_info_about_references(cell_line_object, data_to_add_to_wikidata):
    #  RX         References identifiers
    reference_publication_ids = cell_line_object.cell_line_dump["RX"]
    if reference_publication_ids:
        data_to_add_to_wikidata = append_literature_descriptions(cell_line_object, data_to_add_to_wikidata)
    return data_to_add_to_wikidata


# Functions to append Wikidata Integrator statements to the list of statements
def append_literature_descriptions(cell_line_object, data_to_add_to_wikidata):
    pubmed_ids_and_DOIs_in_wikidata = cell_line_object.references
    reference_publication_ids = cell_line_object.cell_line_dump["RX"]

    references_in_wdi_format = cell_line_object.references_in_wdi_format
    for reference_id in reference_publication_ids:
        if reference_id.startswith("PubMed"):
            pubmed = reference_id.strip("PubMed=")

            if pubmed in pubmed_ids_and_DOIs_in_wikidata:
                # P1343:described by source
                data_to_add_to_wikidata.append(wdi_core.WDItemID(
                    value=pubmed_ids_and_DOIs_in_wikidata[pubmed],
                    prop_nr="P1343",
                    references=references_in_wdi_format))

        elif reference_id.startswith("DOI"):
            doi = reference_id.strip("DOI=")

            if doi in pubmed_ids_and_DOIs_in_wikidata:
                data_to_add_to_wikidata.append(wdi_core.WDItemID(
                    value=pubmed_ids_and_DOIs_in_wikidata[doi],
                    prop_nr="P1343",
                    references=references_in_wdi_format))

    return data_to_add_to_wikidata


def prepare_item_descriptions(cell_line_object):
    label = cell_line_object.cell_line_dump["ID"]

    descriptions = {
        "en": "cell line",
        "fr": "lignée cellulaire",
        "de": "Zelllinie",
        "pt": "linhagem celular",
        "pt-br": "linhagem celular",
        "es": "línea celular"
    }

    if " [" in label:
        namecompose = label.split("[")
        descriptions = {
            "en": "cell line" + " (" + namecompose[1].strip("]") + ")",
            "fr": "lignée cellulaire" + " (" + namecompose[1].strip("]") + ")",
            "de": "Zelllinie" + " (" + namecompose[1].strip("]") + ")"
        }

    return descriptions


def delete_old_statements(cell_line_object, data):
    statements_to_delete = []

    cellosaurus_cell_line_id = cell_line_object.cell_line_id
    wikidata_dictionary_with_existing_cell_lines = cell_line_object.wikidata_dictionary_with_existing_cell_lines

    cell_line_wikidata_id = wikidata_dictionary_with_existing_cell_lines[cellosaurus_cell_line_id]
    cell_line_dump = cell_line_object.cell_line_dump
    if data['data_to_delete']:
        wikidata_item_for_this_cell_line = wdi_core.WDItemEngine(wd_item_id=cell_line_wikidata_id)
        wikidata_item_for_this_cell_line_json = wikidata_item_for_this_cell_line.get_wd_json_representation()

        for statement in wikidata_item_for_this_cell_line_json['claims']:
            if statement in data['data_to_delete']:
                statements_to_delete.append(
                    wdi_core.WDBaseDataType.delete_statement(prop_nr=statement))

        item_deletion = wdi_core.WDItemEngine(
            wd_item_id=cell_line_wikidata_id, data=statements_to_delete)

        item_name = cell_line_dump["ID"]
        item_deletion.write(cell_line_object.wdi_login_object, bot_account=True,
                            edit_summary="delete statements before update the item {}".format(item_name))


def add_all_statements_to_wdi_cell_line(cell_line_object, data):
    cellosaurus_id = cell_line_object.cell_line_id
    wikidata_qid = cell_line_object.wikidata_dictionary_with_existing_cell_lines[cellosaurus_id]
    item = wdi_core.WDItemEngine(wd_item_id=wikidata_qid, data=data['data'],
                                 global_ref_mode='STRICT_OVERWRITE', fast_run=True, fast_run_base_filter={
            'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '', 'P248': '', 'P3289': '',
            'P486': '', 'P2888': '', 'P1343': '', 'P5166': '', 'P813': ''}, fast_run_use_refs=True)

    return item


def add_labels_and_descriptions_to_cell_line_item_ready_for_update(cell_line_object,
                                                                   item_with_statements_to_update,
                                                                   label,
                                                                   descriptions):
    cell_line_dump = cell_line_object.cell_line_dump
    if cell_line_dump:
        item_with_statements_to_update.set_aliases(
            cell_line_dump["SY"], lang='en', append=False)

    for lang, description in descriptions.items():
        item_with_statements_to_update.set_description(description, lang=lang)
        item_with_statements_to_update.set_label(label=label, lang=lang)

    return item_with_statements_to_update


def append_cellosaurus_id(cellosaurus_cell_line_id, information_to_insert_on_wikidata, reference):
    # P3289 : Cellosaurus ID
    information_to_insert_on_wikidata.append(wdi_core.WDExternalID(
        value=cellosaurus_cell_line_id,
        prop_nr="P3289",
        references=reference))

    return information_to_insert_on_wikidata


# Functions to make statements in the Wikidata Integrator format

def make_statement(statement_property, statement_value, references):
    statement = wdi_core.WDItemID(value=statement_value,
                                  prop_nr=statement_property,
                                  references=references)
    return statement


def make_instance_of_cell_line_statement(reference):
    # Q21014462 -> "cell line" ; P31 -> "instance of"
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


# Functions that  interact with Wikidata API

# Functions to query and match to Wikidata
def match_cellosaurus_to_wikidata_items(cellosaurus_in_dicionary_format):
    """
    This function create dictionnaries of list of pre-requisite wikidata
        informations.
    :param cellosaurus_in_dicionary_format : the cellosaurus dictionary from .txt file create
        with format_cellosaurus_dump_as_dictionary function
    :return : a dictionary with contain dictionnaries or list.
        - references_dictionary : in key, the PubMed or DOI id for an article
              in wikidata and in value, the wikidata item id which correspond to
              this article.
        - references_absent_in_wikidata : a list of  references that are not in
              wikidata.
        - species_dictionary : NCBI taxonomy ids matched to the Wikidata id 
        - species_absent_in_wikidata: a list of NCBI taxonomy id that are not in
             Wikidata.
        - diseases_dictionary : NCI thesaurus and matched to Wikidata item 
         for this disease.
        - diseases_absent_in_wikidata :a list of NCI thesaurus ids that are not in
             Wikidata.
        - diseases_with_multiple_matches_in_wikidata : a list of NCI thesaurus ids with multiple
        Wikidata matches
    """
    references_dictionary = {}
    references_absent_in_wikidata = []
    diseases_dictionary = {}
    diseases_absent_in_wikidata = []
    diseases_with_multiple_matches_in_wikidata = []

    print("------------ Checking References on Wikidata-----------")

    list_of_references = []

    for celline in cellosaurus_in_dicionary_format:
        references_for_this_cell_line = cellosaurus_in_dicionary_format[celline]["RX"]
        list_of_references.extend(references_for_this_cell_line)

    list_of_unique_references = list(set(list_of_references))

    print("Total references: " + str(len(list_of_references)))
    print("Unique references: " + str(len(list_of_unique_references)))


    for individual_reference in tqdm(list_of_unique_references):
        
        # check if the reference has been already processed
        # and if not, proceed

        if individual_reference not in references_dictionary:
            if individual_reference not in references_absent_in_wikidata:
            
                if individual_reference.startswith("PubMed"):
                    pubmed_id = individual_reference.strip("PubMed=")
                    try:
                        reference_qid = query_wikidata_by_pubmed_id(pubmed_id)
                        references_dictionary[individual_reference] = reference_qid
                    except Exception as e:
                        tqdm.write("Exception: " + str(e) + "(" + individual_reference + ")")
                        references_absent_in_wikidata.append(individual_reference)


                if individual_reference.startswith("DOI"):
                    doi = individual_reference.strip("DOI=")
                    try:
                        reference_qid = query_wikidata_by_doi(doi)
                        references_dictionary[individual_reference] = reference_qid
                    except Exception as e:
                        tqdm.write("Exception: " + str(e) + "(" + individual_reference + ")")
                        references_absent_in_wikidata.append( individual_reference)



    print("------------ Checking NCI Thesaurus on Wikidata-----------")

    list_of_ncits = []

    for celline in cellosaurus_in_dicionary_format:
        ncit = cellosaurus_in_dicionary_format[celline]["DI"][0]
        list_of_ncits.append(ncit)

    list_of_unique_ncits = list(set(list_of_ncits))

    print("Total ids: " + str(len(list_of_ncits)))
    print("Unique ids: " + str(len(list_of_unique_ncits)))

    for ncit in list_of_unique_ncits:
        try:
            nci_thesaurus_qids = query_wikidata_by_ncit(ncit)
            if len(nci_thesaurus_qids) == 1:
                diseases_dictionary[ncit] = nci_thesaurus_qids[0]

            if len(nci_thesaurus_qids) > 1:
                diseases_with_multiple_matches_in_wikidata.append(ncit)

        except Exception as e:
            print(e)
            diseases_absent_in_wikidata.append(ncit)


    print("------------ Completed matching Cellosaurus on Wikidata-----------")

    return {"references_dictionary": references_dictionary,
            "references_absent_in_wikidata":references_absent_in_wikidata,
            "diseases_dictionary": diseases_dictionary,
            "diseases_absent_in_wikidata": diseases_absent_in_wikidata,
            "diseases_with_multiple_matches_in_wikidata": diseases_with_multiple_matches_in_wikidata}


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
        qid_url = str(cell_line_entry['QID']['value'])
        qid = qid_url.strip("http://www.wikidata.org/entity/").strip("\n")
        CVCL = cell_line_entry['CVCL']['value']
        cellosaurus_to_wikidata_cell_lines[CVCL] = qid

    return (cellosaurus_to_wikidata_cell_lines)

def query_wikidata_for_taxons():
    """
    Recover all the taxons that exist in Wikidata (with an NCBI taxid).
    :return : a dictionary matching NCBI taxid to  Wikidata item id.
    """

    query_result = wdi_core.WDItemEngine.execute_sparql_query(query="""SELECT ?QID ?TAXID WHERE{ 
    ?QID wdt:P685 ?TAXID.
    }""")
    
    query_result = query_result['results']['bindings']

    taxid_to_wikidata = {}
    for taxid_entry in query_result:
        qid_url = str(taxid_entry['QID']['value'])
        qid = qid_url.strip("http://www.wikidata.org/entity/").strip("\n")
        taxid = taxid_entry['TAXID']['value']
        taxid_to_wikidata[taxid] = qid

    return (taxid_to_wikidata)

def query_wikidata_by_pubmed_id(pubmed):
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item WHERE{?item wdt:P698 '""" + pubmed + """'.}""")
    qid_for_pubmed_id = strip_qid_from_query_result(query_result)
    return qid_for_pubmed_id

def query_wikidata_by_doi(doi):
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
            """SELECT ?item WHERE{?item wdt:P356 '""" + doi + """'.}""")
    qid_for_doi = strip_qid_from_query_result(query_result)
    return qid_for_doi

def query_wikidata_by_ncit(ncit):
    """
    : param ncit : a NCI thesaurus term for a disease
    : return : a list of qids that match this term
    """    

    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item ?NCIt WHERE { ?item wdt:P1748 '"""+ ncit +"""'.}""")
    
    qids_for_ncit = []
    for disease in query_result['results']['bindings']:
        qid_for_ncit = disease['item']['value'].strip("http://www.wikidata.org/entity/")
        qids_for_ncit.append(qid_for_ncit)
    
    return qids_for_ncit

def strip_qid_from_query_result(query_result):
    '''
    Strips the qid out of a Wikidata query that
    returns a single result 

    : param query_result : The result of a query to the
    Wikidata SPARQL service using WikidataIntegrator

    :return: the first qid listed in query results
    '''
    query_result = query_result['results']['bindings']
    query_result = query_result[0]['item']['value']
    qid = query_result.strip("http://www.wikidata.org/entity/")
    
    return qid


# Wrapper functions for pickle

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