#!/usr/bin/python3

"""
Updates the Wikidata items relative to the cells in the Cellosaurus dump of interest. 

It takes 3 arguments: 
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on wikidata 
were saved after running "prepare_files.py"
- 3rd: The folder for errors.
- 4th: The QID for the Cellosaurus release on Wikidata   

 Example:
 $ python3 check_lines_on_wikidata.py project/cellosaurus.txt pickle_files errors Q96794096
 """

import json
import os
import pickle
import sys
import time
from pprint import pprint

from SPARQLWrapper import JSON, SPARQLWrapper
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login

import src.utils as utils
from src.cellosaurusbot import *
from src.format import format_cellosaurus_dump_as_dictionary
from src.local import WDPASS, WDUSER
from src.query import *
from src.utils import *
from src.wdi_wrapper import *


def main():

    # -----------------INPUT-------------------------#

    cellosaurus_dump_path = sys.argv[1]
    assert cellosaurus_dump_path, "You need to add a Cellosaurus Dump"

    pickle_path = sys.argv[2]
    assert pickle_path, "You need to add a path to the folder with the pickle files"

    folder_for_errors = sys.argv[3]
    assert folder_for_errors, "You need to add a folder for errors"

    release_qid = sys.argv[4]
    assert release_qid, "You need to add a release QID Dump"

    reconciled_dump_path = pickle_path + "/cellosaurus_wikidata_items.pickle"
    wikidata_cell_lines_path = pickle_path + "/cell_lines_on_wikidata.pickle"
    filename_taxons = pickle_path + "/taxons_on_wikidata.pickle"

    cellosaurus_dump_in_dictionary_format = format_cellosaurus_dump_as_dictionary(
        cellosaurus_dump_path
    )
    cellosaurus_to_wikidata_matches = load_pickle_file(reconciled_dump_path)

    wikidata_cell_lines = load_pickle_file(wikidata_cell_lines_path)
    login = wdi_login.WDLogin(WDUSER, WDPASS)
    ncbi_id_to_qid_species = load_pickle_file(filename_taxons)

    references = cellosaurus_to_wikidata_matches["references_dictionary"]
    diseases = cellosaurus_to_wikidata_matches["diseases_dictionary"]

    categories = load_cell_line_category_to_wikidata("project/category.txt")

    new_cell_lines = []
    for cellosaurus_id in cellosaurus_dump_in_dictionary_format:
        if cellosaurus_id not in wikidata_cell_lines:
            new_cell_lines.append(cellosaurus_id)

    flag_for_new_lines = False
    for cellosaurus_id in tqdm(new_cell_lines):
        tqdm.write(cellosaurus_id)
        cell_line = CellosaurusCellLine(
            wdi_login_object=login,
            release_qid=release_qid,
            cellosaurus_dump=cellosaurus_dump_in_dictionary_format,
            wikidata_dictionary_with_existing_cell_lines=wikidata_cell_lines,
            references=references,
            species=ncbi_id_to_qid_species,
            cell_line_categories=categories,
            diseases=diseases,
            cell_line_id=cellosaurus_id,
        )

        prepared_data = cell_line.prepare_for_wikidata(folder_for_errors)

        try:
            cell_line.update_line_on_wikidata(prepared_data)
        except Exception as e:
            print(e)
        flag_for_new_lines = True

        time.sleep(1)

    if flag_for_new_lines:
        filename_cell_lines = pickle_path + "/cell_lines_on_wikidata.pickle"
        wikidata_cell_lines = query_wikidata_for_cell_lines()
        save_pickle_file(wikidata_cell_lines, filename_cell_lines)


if __name__ == "__main__":
    main()
