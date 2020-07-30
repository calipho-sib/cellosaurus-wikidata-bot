#!/usr/bin/python3



'''
Updates the Wikidata items relative to the cells in the Cellosaurus dump of interest. 

It takes 3 arguments: 
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on wikidata 
were saved after running "prepare_files.py"
- 4th: The QID for the Cellosaurus release on Wikidata   

 Example:
 $ python3 update_wikidata.py project/test_cellosaurus.txt pickle_files  Q87574023
'''

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import json
import pickle
import sys
import os
import progressbar

import src.utils as utils
from src.local import WDUSER, WDPASS

def main():

    #-----------------INPUT-------------------------#


    cellosaurus_dump_path = sys.argv[1]
    pickle_path = sys.argv[2]
    release_qid = sys.argv[3]
    
    reconciled_dump_path = pickle_path + "/cellosaurus_wikidata_items.pickle"
    wikidata_cell_lines_path = pickle_path + "/cell_lines_on_wikidata.pickle"
    filename_taxons = pickle_path + "/taxons_on_wikidata.pickle"

    cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary(cellosaurus_dump_path)
    cellosaurus_to_wikidata_matches = utils.load_pickle_file(reconciled_dump_path)
    wikidata_cell_lines = utils.load_pickle_file(wikidata_cell_lines_path)
    login = wdi_login.WDLogin(WDUSER, WDPASS)
    ncbi_id_to_qid_species = utils.load_pickle_file(wikidata_cell_lines_path)
    references = cellosaurus_to_wikidata_matches["references_dictionary"]
    print(references)
    diseases = cellosaurus_to_wikidata_matches["diseases_dictionary"]
    categories = utils.get_cell_line_category_to_wikidata("project/category.txt")
    
    for cellosaurus_id in cellosaurus_dump_in_dictionary_format:

        print(cellosaurus_id)
        print(wikidata_cell_lines[cellosaurus_id])
        cell_line = utils.CellosaurusCellLine(wdi_login_object=login,
                                    release_qid=release_qid,
                                    cellosaurus_dump=cellosaurus_dump_in_dictionary_format,
                                    wikidata_dictionary_with_existing_cell_lines=wikidata_cell_lines,
                                    references=references,
                                    species=ncbi_id_to_qid_species,
                                    cell_line_categories=categories,
                                    diseases=diseases,
                                    cell_line_id=cellosaurus_id)

        prepared_data =  cell_line.prepare_for_wikidata(folder_for_errors="doc/ERRORS/") 

        cell_line.update_line_on_wikidata(prepared_data)

'''




updated_items = {}
created_items = ["Cell Lines created", "Release ID:", release_qid]

with open("results/cell_line_duplicate.txt", "w") as file_for_duplicated_lines:
    widgets = [
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        ' (', progressbar.ETA(), ') ',
    ]
    bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength, redirect_stdout=True, widgets=widgets)
    dict_size = len(cellosaurus_dump_in_dictionary_format)

    counter = 0
    for cell_line in cellosaurus_dump_in_dictionary_format:
        print(cell_line)
        bar.update(counter)
        counter += 1
        print(str(counter) + "out of" + str(dict_size))
        
        if cell_line in cellosaurus_release.wikidata and cell_line not in updated_items:
            print("update")

            try:
                cellosaurus_release.UpdateWikidata(
                    cell_line, cellosaurus_release.InitialisationData(cell_line))
            except Exception as e:
                print(e)
                pass

            updated_items[cell_line] = wikidata[cell_line]

        elif cell_line in cellosaurus_release.wikidata and cell_line in updated_items:
            print("duplicated")

            file_for_duplicated_lines.write(
                cell_line + "\t" + wikidata[cell_line] + "\n")

        else:
            print("create")

            cellosaurus_release.InsertionWikidata(
                cell_line, cellosaurus_release.InitialisationData(cell_line))
            created_items.append(cell_line)

f = open('results/created_cell_line_items.txt', 'w')

for cell_line in created_items:
    f.write(cell_line + '\n')

f.close()

with open("results/Qids_2_delete.txt", "w") as file:
    for cell_line in cellosaurus_release.wikidata:
        if cell_line not in cellosaurus_release.cellosaurus:
            file.write(cell_line + "\t" + wikidata[cell_line] + "\n")

with open("doc/ERRORS/diseases/more_than_1.txt", "w") as file:
    for duplicate in cellosaurus_to_wikidata_matches["problematicdiseases"]:
        problematic_disease = cellosaurus_to_wikidata_matches["problematicdiseases"][duplicate]
        file.write(
            duplicate + "\t" + str(problematic_disease) + "\n")

wikidata = query_wikidata_for_cell_lines()

cellosaurus_release.Update_Wikidata(wikidata)

for cell_line in cellosaurus_release.AddParentCellline:
    if cell_line in cellosaurus_release.wikidata:
        cellosaurus_release.UpdateWikidata(
            cell_line, cellosaurus_release.InitialisationData(cell_line))
'''

if __name__=="__main__": 
    main() 