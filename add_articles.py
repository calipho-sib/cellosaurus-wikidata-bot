"""
Uses Wikidata Integrator to add articles to Wikidata based on DOI.

It takes as input the path for a folder with DOIs in the format 
DOI=10.7554/eLife.67077
DOI=10.7554/eLife.67078


"""

import sys
from src.local import WDUSER, WDPASS
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers
from tqdm import tqdm
from src.utils import *

folder_for_errors = sys.argv[1]
assert (
    folder_for_errors
), "You need to pass the folder for errors used by prepare_files.py"

doi_file = folder_for_errors + "/references_absent_in_wikidata.txt"

with open(doi_file, "r") as f:
    references = f.readlines()

references_still_absent = []
login_instance = wdi_login.WDLogin(user=WDUSER, pwd=WDPASS)
for reference in tqdm(references):
    doi = reference.replace("DOI=", "").replace("\n", "")
    tqdm.write(f"Adding article with DOI = {doi}")
    wdi_publication_helper = wdi_helpers.PublicationHelper(
        ext_id=doi, id_type="doi", source="crossref"
    )
    wdi_result = wdi_publication_helper.get_or_create(login_instance)
    if wdi_result[0] == None:
        print("Not added to Wikidata.")
        references_still_absent.append(reference.strip())

write_list(doi_file, references_still_absent)
