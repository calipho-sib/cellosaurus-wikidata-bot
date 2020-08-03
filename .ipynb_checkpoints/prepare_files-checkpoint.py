#!/usr/bin/python3

# This script takes a Cellosaurus dump and matches its contents to Wikidata items.
# The dictionary is then serialized in a pickle fime. 
# It takes 3 arguments: 
# 1st: The path to the .txt of the Cellosaurus dump
# 2nd: The path to the folder where the pickle file and cell lines on wikidata will be saved.
# 3rd: The path to the folder where the errors in match to wikidata will be saved.   
#
# Example: 
# python3 prepare_files.py project/test_cellosaurus.txt project 
#
# The reconciled dump is named "cellosaurus_wikidata_items.pickle".
#
# In the example above, the outputs would be two files called:
# project/cellosaurus_wikidata_items.pickle
# project/cell_lines_on_wikidata.pickle
#

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import json
import pickle
import sys
import os
import src.utils as utils


def main():

    #-----------------INPUT-------------------------#


    cellosaurus_dump_path = sys.argv[1]
    pickle_path = sys.argv[2]
    folder_for_errors = sys.argv[3]

    filename_reconciled_dump = pickle_path + "/cellosaurus_wikidata_items.pickle"
    filename_cell_lines = pickle_path + "/cell_lines_on_wikidata.pickle"
    filename_taxons = pickle_path + "/taxons_on_wikidata.pickle"
    try:
        cellosaurus_dump_as_dictionary = utils.format_cellosaurus_dump_as_dictionary(cellosaurus_dump_path)
    except FileNotFoundError:
        print("------------------- Cellosaurus file could not be open -------------------")
    
    print("------------------- Querying Wikidata for cell lines -------------------")

    wikidata_cell_lines = utils.query_wikidata_for_cell_lines()

    print("------------------- Querying Wikidata for taxon ids -------------------")

    wikidata_taxons = utils.query_wikidata_for_taxons()
    utils.save_pickle_file(wikidata_taxons, filename_taxons)

    print("------------------- Processing Cellosaurus dump -------------------")
    cellosaurus_dump_to_wikidata_items = utils.match_cellosaurus_dump_to_wikidata_items(cellosaurus_dump_as_dictionary)
    utils.save_pickle_file(cellosaurus_dump_to_wikidata_items, filename_reconciled_dump)


    print("------------------- Writing failed matches to folder -------------------")

    absent_references_filepath = folder_for_errors + "/references_absent_in_wikidata.txt"
    with open(absent_references_filepath, "w") as f: 
        for item in cellosaurus_dump_to_wikidata_items["references_absent_in_wikidata"]:
            f.write("%s\n" % item)


    absent_diseases_filepath = folder_for_errors + "/diseases_absent_in_wikidata.txt"
    with open(absent_diseases_filepath, "w") as f: 
        for item in cellosaurus_dump_to_wikidata_items["diseases_absent_in_wikidata"]:
            f.write("%s\n" % item)

    
    multiple_diseases_filepath = folder_for_errors + "/diseases_with_multiple_matches_in_wikidata.txt"
    with open(multiple_diseases_filepath, "w") as f: 
        for item in cellosaurus_dump_to_wikidata_items["diseases_with_multiple_matches_in_wikidata"]:
            f.write("%s\n" % item)


if __name__=="__main__": 
    main() 