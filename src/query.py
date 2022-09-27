#!/usr/bin/python3

from tqdm import tqdm
from wikidataintegrator import wdi_core

# cellosaurus_in_dicionary_format is currently provided by the
# format_cellosaurus_dump_as_dictionary function in the format.py file


def query_wikidata_for_ncit_diseases(cellosaurus_in_dicionary_format):
    diseases_dictionary = {}
    diseases_absent_in_wikidata = []
    diseases_with_multiple_matches_in_wikidata = []

    list_of_ncits = []

    for celline in cellosaurus_in_dicionary_format:

        try:
            ncit = cellosaurus_in_dicionary_format[celline]["DI"][0]
            list_of_ncits.append(ncit)
        except Exception as e:
            print(e)
            print(cellosaurus_in_dicionary_format[celline]["DI"])

    list_of_unique_ncits = list(set(list_of_ncits))

    print("Total ids: " + str(len(list_of_ncits)))
    print("Unique ids: " + str(len(list_of_unique_ncits)))

    for ncit in tqdm(list_of_unique_ncits):
        try:
            nci_thesaurus_qids = query_wikidata_by_ncit(ncit)
            if len(nci_thesaurus_qids) == 1:
                diseases_dictionary[ncit] = nci_thesaurus_qids[0]

            if len(nci_thesaurus_qids) > 1:
                diseases_with_multiple_matches_in_wikidata.append(ncit)

        except Exception as e:
            tqdm.write(e)
            diseases_absent_in_wikidata.append(ncit)
    return (
        diseases_dictionary,
        diseases_absent_in_wikidata,
        diseases_with_multiple_matches_in_wikidata,
    )


def query_wikidata_for_articles(
    cellosaurus_in_dicionary_format,
    references_dictionary,
    references_absent_in_wikidata,
):

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
                        tqdm.write(
                            "Exception: " + str(e) + "(" + individual_reference + ")"
                        )
                        references_absent_in_wikidata.append(individual_reference)

                if individual_reference.startswith("DOI"):
                    doi = individual_reference.strip("DOI=")
                    try:
                        reference_qid = query_wikidata_by_doi(doi)
                        references_dictionary[individual_reference] = reference_qid
                    except Exception as e:
                        tqdm.write(
                            "Exception: " + str(e) + "(" + individual_reference + ")"
                        )
                        references_absent_in_wikidata.append(individual_reference)
    return references_dictionary, references_absent_in_wikidata


def query_wikidata_by_pubmed_id(pubmed):
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item WHERE{?item wdt:P698 '""" + pubmed + """'.}"""
    )
    qid_for_pubmed_id = strip_qid_from_query_result(query_result)
    return qid_for_pubmed_id


def query_wikidata_by_doi(doi):
    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item WHERE{?item wdt:P356 '""" + doi + """'.}"""
    )
    qid_for_doi = strip_qid_from_query_result(query_result)
    return qid_for_doi


def query_wikidata_by_ncit(ncit):
    """
    : param ncit : a NCI thesaurus term for a disease
    : return : a list of qids that match this term
    """

    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        """SELECT ?item ?NCIt WHERE { ?item wdt:P1748 '""" + ncit + """'.}"""
    )

    qids_for_ncit = []
    for disease in query_result["results"]["bindings"]:
        qid_for_ncit = disease["item"]["value"].strip("http://www.wikidata.org/entity/")
        qids_for_ncit.append(qid_for_ncit)

    return qids_for_ncit


def strip_qid_from_query_result(query_result):
    """
    Strips the qid out of a Wikidata query that
    returns a single result

    : param query_result : The result of a query to the
    Wikidata SPARQL service using WikidataIntegrator

    :return: the first qid listed in query results
    """
    query_result = query_result["results"]["bindings"]
    query_result = query_result[0]["item"]["value"]
    qid = query_result.strip("http://www.wikidata.org/entity/")

    return qid


def query_wikidata_for_cell_lines():
    """
    Recover all the cell lines that exist in Wikidata (with a Cellosaurus id).
    :return : a dictionary matching Cellosaurus id to  Wikidata cell line item id.
    """

    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        query="""SELECT ?QID ?CVCL WHERE{ 
    ?QID wdt:P3289 ?CVCL.
    }"""
    )
    query_result = query_result["results"]["bindings"]

    cellosaurus_to_wikidata_cell_lines = {}
    for cell_line_entry in query_result:
        qid_url = str(cell_line_entry["QID"]["value"])
        qid = qid_url.strip("http://www.wikidata.org/entity/").strip("\n")
        CVCL = cell_line_entry["CVCL"]["value"]
        cellosaurus_to_wikidata_cell_lines[CVCL] = qid

    return cellosaurus_to_wikidata_cell_lines


def query_wikidata_for_taxons():
    """
    Recover all the taxons that exist in Wikidata (with an NCBI taxid).
    :return : a dictionary matching NCBI taxid to  Wikidata item id.
    """

    query_result = wdi_core.WDItemEngine.execute_sparql_query(
        query="""SELECT ?QID ?TAXID WHERE{ 
    ?QID wdt:P685 ?TAXID.
    }"""
    )

    query_result = query_result["results"]["bindings"]

    taxid_to_wikidata = {}
    for taxid_entry in query_result:
        qid_url = str(taxid_entry["QID"]["value"])
        qid = qid_url.strip("http://www.wikidata.org/entity/").strip("\n")
        taxid = taxid_entry["TAXID"]["value"]
        taxid_to_wikidata[taxid] = qid

    return taxid_to_wikidata
