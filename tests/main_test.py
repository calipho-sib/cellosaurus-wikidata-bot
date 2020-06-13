import unittest
from wikidataintegrator import wdi_core, wdi_login
import os
from src.local import WDUSER, WDPASS
from utils import DeserializeData, SerializeData , match_cellosaurus_dump_to_wikidata_items, get_cell_line_category_to_wikidata, Set, Create_Update, format_cellosaurus_dump_as_dictionary, query_wikidata_for_cell_lines, add_reference_to_wikidata
import requests
import eventlet



os.chdir("/")

release=wdi_core.WDItemEngine(wd_item_id="Q87574023").get_label()

class TestRelease(unittest.TestCase):
    
    def test_correct_release(self):
        self.assertEqual(release,'Cellosaurus release 34')

    def test_loading_of_cellosaurus(self):
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"],'#15310-LN')

cellosaurus_informations_to_wikidata_ids = DeserializeData("correspondance.pickle")

cellosaurus_dump_in_dictionary_format = format_cellosaurus_dump_as_dictionary("./project/test_cellosaurus.txt")

class TestRelease2(unittest.TestCase):


    login = wdi_login.WDLogin(WDUSER, WDPASS)
    species = cellosaurus_informations_to_wikidata_ids["species"]
    references = cellosaurus_informations_to_wikidata_ids["references"]
    diseases = cellosaurus_informations_to_wikidata_ids["diseases"]
    categories = get_cell_line_category_to_wikidata("project/category.txt")

    wikidata=query_wikidata_for_cell_lines()
    cellosaurus_release = Create_Update(login=login, releaseID="Q87574023", cellosaurus=cellosaurus_dump_in_dictionary_format, wikidata=wikidata,
                                     references=references, species=species, categories=categories, diseases=diseases)

    with eventlet.Timeout(10):
        print("ok, timeout set for 10 seconds")
        cellosaurus_release.UpdateWikidata(
          cell_line, cellosaurus_release.InitialisationData(cell_line))

    for cell_line in cellosaurus_dump_in_dictionary_format:
        print(cell_line)

        if cell_line in cellosaurus_release.wikidata:
            print("update")
            cellosaurus_release.UpdateWikidata(cell_line, cellosaurus_release.InitialisationData(cell_line))

    def test_correct_release(self):
        self.assertEqual(release,'Cellosaurus release 34')



if __name__ == '__main__':
    unittest.main()