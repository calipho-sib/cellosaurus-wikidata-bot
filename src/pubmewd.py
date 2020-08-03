#!/usr/bin/python3
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login


def add_pubmed_id_to_wikidata(pubmed_id):
    '''
    This funcion adds an article to Wikidata based on its pubmed_id. 
    It is a wrapper for Wikidata Integrators 
    wdi_core.wdi_helpers.PubmedItem function. 

    : param pubmed_id: The numbers for the PubMed ID of the  publication
    : return : The article is added to Wikidata. 
    '''

    