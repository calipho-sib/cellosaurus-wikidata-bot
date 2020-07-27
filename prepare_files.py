#!/usr/bin/python3

# This script takes a Cellosaurus dump and matches its contents to Wikidata items.
# The dictionary is then serialized in a pickle fime. 
# It takes 2 arguments: 
# 1st: The path to the .txt of the Cellosaurus dump
# 2nd: The path to the folder where the pickle file and cell lines on wikidata will be saved.  
#
# Example: 
# python3 prepare_files.py project/test_cellosaurus.txt project
#
#
# The reconciled dump is named "cellosaurus_wikidata_items.pickle".
# 
# In the example above, the output would be in a file called:
# project/cellosaurus_wikidata_items.pickle
# 
# The cell lines on wikidata are saved as  "project/cell_lines_on_wikidata.pickle"
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

    filename_reconciled_dump = pickle_path + "cellosaurus_wikidata_items.pickle"
    filename_cell_lines = pickle_path + "cell_lines_on_wikidata.pickle"


    try:
        cellosaurus_dump_as_dictionary = utils.format_cellosaurus_dump_as_dictionary(cellosaurus_dump_path)
    except FileNotFoundError:
        print("------------------- Cellosaurus file could not be open -------------------")
    
    #contains the cell lines items with a Cellosaurus ID
    wikidata=utils.query_wikidata_for_cell_lines()

    cellosaurus_dump_to_wikidata_items = utils.match_cellosaurus_dump_to_wikidata_items(cellosaurus_dump_as_dictionary)

    utils.save_pickle_file(wikidata, filename_cell_lines)
    utils.save_pickle_file(cellosaurus_dump_to_wikidata_items, filename_reconciled_dump)


if __name__=="__main__": 
    main() 