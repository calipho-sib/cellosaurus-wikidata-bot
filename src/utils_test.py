import unittest
import os
import utils
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from src.local import WDUSER, WDPASS
#login with your Wikidata user and password in local.py


class TestRunning(unittest.TestCase):
    
    def test_run(self):
        self.assertEqual(1,1)


os.chdir("/home/lubianat/Documents/cellosaurus-wikidata-bot")

class TestStringMethods(unittest.TestCase):
  
    def test_loading_of_cellosaurus(self):
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("./project/test_cellosaurus.txt")
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"],'#15310-LN')
        
    def test_loading_of_cell_lines(self):
        cell_line_to_wikidata_id = utils.QueryingWikidata()
        self.assertEqual(cell_line_to_wikidata_id["CVCL_E548"],'Q54398957')


    def test_matching_of_cellosaurus_to_wikidata(self):
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("./project/test_cellosaurus.txt")
        cellosaurus_informations_to_wikidata_ids = utils.correspondance(cellosaurus_dump_in_dictionary_format)
        self.assertEqual(cellosaurus_informations_to_wikidata_ids["references"]['25400923'],'Q42064754')


class TestAuxiliaryFunctions(unittest.TestCase):
    
    def test_add_reference_to_wikidata(self):
        pubmed_id = "mock_id"
        utils.add_reference_to_wikidata(pubmed_id)
        self.assertEqual("bla", "bla")


class TestPickleFunctions(unittest.TestCase):
    
    def test_save__load_pickle(self):
        test_dictionary = {"a":1 , "b":2}

        utils.SerializeData(test_dictionary,"/tmp/test.pickle")
        test_dictionary_after_processing  = utils.DeserializeData("/tmp/test.pickle")
        
        os.remove("/tmp/test.pickle")
        
        self.assertEqual(test_dictionary,test_dictionary_after_processing)
           
class TestCreate_UpdateClass(unittest.TestCase):
    
    def test_CreateUpdate_object_creation(self):
        
        the_so_called_correspondance = utils.load_pickle_file("src/test_full_cellosaurus_to_wikidata.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("./project/test_cellosaurus.txt")
        wikidata=utils.QueryingWikidata()
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        Release = utils.Create_Update(login=login,
                                      releaseID=releaseID,
                                      cellosaurus=cellosaurus_dump_in_dictionary_format,
                                      wikidata=wikidata,
                                      references=references,
                                      species=species,
                                      categories=categories,
                                      diseases=diseases)

        old_release = utils.load_pickle_file("src/release_object_before_refactoring.pickle")
        
        self.assertEqual(old_release.references, Release.references)

    def test_Initialisation_Data(self):
        
        the_so_called_correspondance = utils.load_pickle_file("src/test_full_cellosaurus_to_wikidata.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("./project/test_cellosaurus.txt")
        wikidata = utils.QueryingWikidata()
        utils.save_pickle_file(wikidata, "output_of_QueryingWikidata")
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        Release = utils.Create_Update(login=login,
                                      releaseID=releaseID,
                                      cellosaurus=cellosaurus_dump_in_dictionary_format,
                                      wikidata=wikidata,
                                      references=references,
                                      species=species,
                                      categories=categories,
                                      diseases=diseases)

        old_release = utils.load_pickle_file("src/release_object_before_refactoring.pickle")
        
        new_output_of_InitialisationData = Release.InitialisationData(Item="CVCL_E548")
        old_output_of_InitialisationData = old_release.InitialisationData(Item="CVCL_E548")

        print(new_output_of_InitialisationData)

        self.assertEqual(new_output_of_InitialisationData, old_output_of_InitialisationData)

           




if __name__ == '__main__':
    unittest.main()
