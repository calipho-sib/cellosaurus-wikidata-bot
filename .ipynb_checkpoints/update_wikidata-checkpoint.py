#!/usr/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import json
import pickle
import sys
import os
from src.utils import DeserializeData, SerializeData, correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata

from src.local import WDUSER, WDPASS


cellosaurus_dump_in_dictionary_format = CellosaurusToDictionary(sys.argv[2])

cellosaurus_to_wikidata_matches = DeserializeData("correspondance.pickle")

login = wdi_login.WDLogin(WDUSER, WDPASS)

species = cellosaurus_to_wikidata_matches["species"]
references = cellosaurus_to_wikidata_matches["references"]
diseases = cellosaurus_to_wikidata_matches["diseases"]
categories = categories("project/category.txt")

wikidata=QueryingWikidata()

cellosaurus_release = Create_Update(login=login, releaseID=sys.argv[1], cellosaurus=cellosaurus_dump_in_dictionary_format, wikidata=wikidata,
                                    references=references, species=species, categories=categories, diseases=diseases)

updated_items = {}
created_items = []

with open("results/cell_line_duplicate.txt", "w") as file_for_duplicated_lines:

    for cell_line in cellosaurus_dump_in_dictionary_format:
        print(cell_line)

        if cell_line in cellosaurus_release.wikidata and cell_line not in updated_items:
            print("update")

            try:
                cellosaurus_release.UpdateWikidata(
                cell_line, cellosaurus_release.InitialisationData(cell_line))
            except:
                print("oops")
                pass


            updated_items[cell_line] = wikidata[cell_line]

        elif cell_line in cellosaurus_release.wikidata and cell_line in updated_items:
            print("duplicated")

            file_for_duplicated_lines.write(
                cell_line+"\t"+wikidata[cell_line]+"\n")

        else:
            print("create")

            cellosaurus_release.InsertionWikidata(
                cell_line, cellosaurus_release.InitialisationData(cell_line))
            created_items.append(cell_line)


with open("results/Qids_2_delete.txt", "w") as file:
    for cell_line in cellosaurus_release.wikidata:
        if cell_line not in cellosaurus_release.cellosaurus:
            file.write(cell_line+"\t"+wikidata[cell_line]+"\n")

with open("doc/ERRORS/diseases/more_than_1.txt", "w") as file:
    for duplicate in cellosaurus_to_wikidata_matches["problematicdiseases"]:

        problematic_disease = cellosaurus_to_wikidata_matches["problematicdiseases"][duplicate]
        file.write(
            duplicate+"\t"+str(problematic_disease)+"\n")


wikidata = QueryingWikidata()

cellosaurus_release.Update_Wikidata(wikidata)


for cell_line in cellosaurus_release.AddParentCellline:
    if cell_line in cellosaurus_release.wikidata:
        cellosaurus_release.UpdateWikidata(
            cell_line, cellosaurus_release.InitialisationData(cell_line))

