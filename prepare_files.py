#!/usr/bin/python3

# This script takes a Cellosaurus dump and matches its contents to Wikidata items.
# The dictionary is then serialized in a pickle fime. 
# It takes 3 arguments: 
# 1st: The path to the .txt of the Cellosaurus dump
# 2nd: The path to the folder where the pickle file and cell lines on wikidata will be saved.
# 3rd: The path to the folder where the errors in match to wikidata will be saved.   
#
# Example: 
# python3 prepare_files.py project/test_cellosaurus.txt pickle_files errors

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import json
import pickle
import sys
import os.path
from src.format import format_cellosaurus_dump_as_dictionary
from src.utils import *
from src.query import *
from src.wdi_wrapper import *
from src.cellosaurusbot import *


def main():

    #-----------------INPUT-------------------------#


    cellosaurus_dump_path = sys.argv[1]
    pickle_path = sys.argv[2]
    folder_for_errors = sys.argv[3]

    filename_reconciled_dump = pickle_path + "/cellosaurus_wikidata_items.pickle"
    filename_cell_lines = pickle_path + "/cell_lines_on_wikidata.pickle"
    filename_taxons = pickle_path + "/taxons_on_wikidata.pickle"
    try:
        cellosaurus_dump_as_dictionary = format_cellosaurus_dump_as_dictionary(cellosaurus_dump_path)
    except FileNotFoundError:
        print("------------------- Cellosaurus file could not be open -------------------")
    
    print("------------------- Querying Wikidata for cell lines -------------------")


    if os.path.isfile(filename_cell_lines):
        print("Skipping. Previously cached cell lines are present.")
    else:
        wikidata_cell_lines = query_wikidata_for_cell_lines()
        save_pickle_file(wikidata_cell_lines, filename_cell_lines)

    print("------------------- Querying Wikidata for taxon ids -------------------")

    if os.path.isfile(filename_taxons):
        print("Skipping. Previously cached taxons are present.")
    else:
        wikidata_taxons = query_wikidata_for_taxons()
        save_pickle_file(wikidata_taxons, filename_taxons)

    print("------------------- Processing Cellosaurus dump -------------------")

    print("------------ Checking References on Wikidata-----------")
    
    references_path = pickle_path + "/references_in_wikidata.json"
    
    try:
        references_dictionary = json.load(open(references_path))
        print("Previous article dictionary found. Incrementing if needed.") 
    except Exception as e:
        print(e)
        print("No previous article dictionary found. Building new one.")
        references_dictionary = {}
    
    references_dictionary, references_absent_in_wikidata = query_wikidata_for_articles( \
            cellosaurus_dump_as_dictionary, \
            references_dictionary)

    with open(references_path, 'w+') as file:

        file.write(json.dumps(references_dictionary)) # use `json.loads` to do the revers

    absent_references_filepath = folder_for_errors + "/references_absent_in_wikidata.txt"
    with open(absent_references_filepath, "w") as f: 
        for item in references_absent_in_wikidata:
            f.write("%s\n" % item)

    print("------------ Checking NCI Thesaurus on Wikidata-----------")
   
    diseases_dictionary, diseases_absent_in_wikidata, diseases_with_multiple_matches_in_wikidata = query_wikidata_for_ncit_diseases(cellosaurus_dump_as_dictionary)

    absent_diseases_filepath = folder_for_errors + "/diseases_absent_in_wikidata.txt"
    with open(absent_diseases_filepath, "w") as f: 
        for item in diseases_absent_in_wikidata:
            f.write("%s\n" % item)

    
    multiple_diseases_filepath = folder_for_errors + "/diseases_with_multiple_matches_in_wikidata.txt"
  
    with open(multiple_diseases_filepath, "w") as f: 
        for item in diseases_with_multiple_matches_in_wikidata:
            f.write("%s\n" % item)


    cellosaurus_dump_as_dictionary = {"references_dictionary": references_dictionary,
            "references_absent_in_wikidata":references_absent_in_wikidata,
            "diseases_dictionary": diseases_dictionary,
            "diseases_absent_in_wikidata": diseases_absent_in_wikidata,
            "diseases_with_multiple_matches_in_wikidata": diseases_with_multiple_matches_in_wikidata}

    save_pickle_file(cellosaurus_dump_as_dictionary, filename_reconciled_dump)



if __name__=="__main__": 
    main() 