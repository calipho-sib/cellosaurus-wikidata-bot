#!/usr/bin/python3
from wikidataintegrator import wdi_core
from datetime import datetime
from .wdi_wrapper import *

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

    def prepare_for_wikidata(self, folder_for_errors):

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
                with open(folder_for_errors + "/diseases_not_in_wikidata.txt", "a") as file:
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
            # P2158: Cell Line Ontology ID 
            data_to_add_to_wikidata.append(wdi_core.WDString(
                value= CLO,
                prop_nr="P2158",
                references=reference))
            # P2888: exact match
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + CLO,
                prop_nr="2888",
                references=reference))


    if cell_line_dump["BTO"]:
        for BTO in cell_line_dump["BTO"]:
            # P2888: exact match
            data_to_add_to_wikidata.append(wdi_core.WDUrl(
                value="http://purl.obolibrary.org/obo/" + BTO,
                prop_nr="2888",
                references=reference))

    if cell_line_dump["EFO"]:
        for EFO in cell_line_dump["EFO"]:
            # P2888: exact match
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
    sourceref_to_wikidata = cell_line_object.references
    sourceref_ids = cell_line_object.cell_line_dump["RX"]

    references_in_wdi_format = cell_line_object.references_in_wdi_format
    
    for sourceref in sourceref_ids:
        
        if sourceref in sourceref_to_wikidata:
            sourceref_qid = sourceref_to_wikidata[sourceref]
            data_to_add_to_wikidata.append(wdi_core.WDItemID(
                    value=sourceref_qid,
                    prop_nr="P1343",
                    references=references_in_wdi_format))
        else:
            print("Reference " + sourceref + " could not be added")

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



def add_all_statements_to_wdi_cell_line(cell_line_object, data):
    cellosaurus_id = cell_line_object.cell_line_id

    if cellosaurus_id in cell_line_object.wikidata_dictionary_with_existing_cell_lines:
        wikidata_qid = cell_line_object.wikidata_dictionary_with_existing_cell_lines[cellosaurus_id]
        item = wdi_core.WDItemEngine(wd_item_id=wikidata_qid, data=data['data'],
                                 global_ref_mode='STRICT_OVERWRITE', fast_run=True, fast_run_base_filter={
            'P31': 'Q21014462', 'P31': '', 'P21': '', 'P703': '', 'P3432': '', 'P3578': '', 'P248': '', 'P3289': '',
            'P486': '', 'P2888': '', 'P1343': '', 'P5166': '', 'P813': ''}, fast_run_use_refs=True)
    else:
        item = wdi_core.WDItemEngine(wd_item_id='', new_item=True, data=data['data'],
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

