import unittest
import os
from utils import DeserializeData, SerializeData , correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata, add_reference_to_wikidata


class TestRunning(unittest.TestCase):
    
    def test_run(self):
        self.assertEqual(1,1)


os.chdir("/home/lubianat/Documents/cellosaurus-wikidata-bot")

class TestStringMethods(unittest.TestCase):
  
    def test_loading_of_cellosaurus(self):
        cellosaurus_dump_in_dictionary_format = CellosaurusToDictionary("./project/test_cellosaurus.txt")
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"],'#15310-LN')
        
    def test_loading_of_cell_lines(self):
        cell_line_to_wikidata_id = QueryingWikidata()
        self.assertEqual(cell_line_to_wikidata_id["CVCL_E548"],'Q54398957')


    def test_matching_of_cellosaurus_to_wikidata(self):
        cellosaurus_dump_in_dictionary_format = CellosaurusToDictionary("./project/test_cellosaurus.txt")
        cellosaurus_informations_to_wikidata_ids = correspondance(cellosaurus_dump_in_dictionary_format)
        self.assertEqual(cellosaurus_informations_to_wikidata_ids["references"]['25400923'],'Q42064754')


class TestAuxiliaryFunctions(unittest.TestCase):
    
    def test_add_reference_to_wikidata(self):
        pubmed_id = "mock_id"
        add_reference_to_wikidata(pubmed_id)
        self.assertEqual("bla", "bla")


class TestPickleFunctions(unittest.TestCase):
    
    def test_save_pickle(self):
        test_dictionary = {"a":1 , "b":2}
        self.assertEqual(test_dictionary['a'],1)
           
 
if __name__ == '__main__':
    unittest.main()