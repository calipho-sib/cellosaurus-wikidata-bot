import unittest
import os

from utils import DeserializeData, SerializeData , correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata


os.chdir("/home/lubianat/Documents/cellosaurus-wikidata-bot")

cellosaurus_dump_in_dictionary_format = CellosaurusToDictionary("./project/test_cellosaurus.txt")

cell_line_to_wikidata_id = QueryingWikidata()

cellosaurus_informations_to_wikidata_ids = correspondance(cellosaurus_dump_in_dictionary_format)

class TestStringMethods(unittest.TestCase):
    
    def test_loading_of_cellosaurus(self):
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"],'#15310-LN')
        
    def test_loading_of_cell_lines(self):
        self.assertEqual(cell_line_to_wikidata_id["CVCL_E548"],'Q54398957')


    def test_matching_of_cellosaurus_to_wikidata(self):
        self.assertEqual(cellosaurus_informations_to_wikidata_ids["references"]['25400923'],'Q42064754')

           
 
if __name__ == '__main__':
    unittest.main()