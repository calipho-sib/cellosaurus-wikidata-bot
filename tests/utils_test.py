import unittest
import os
import utils
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from src.local import WDUSER, WDPASS


# login with your Wikidata user and password in local.py


class TestRunning(unittest.TestCase):

    def test_run(self):
        self.assertEqual(1, 1)


class TestStringMethods(unittest.TestCase):

    def test_loading_of_cellosaurus(self):
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"], '#15310-LN')

    def test_loading_of_cell_lines(self):
        cell_line_to_wikidata_id = utils.QueryingWikidata()
        self.assertEqual(cell_line_to_wikidata_id["CVCL_E548"], 'Q54398957')

    def test_matching_of_cellosaurus_to_wikidata(self):
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
        cellosaurus_informations_to_wikidata_ids = utils.correspondance(cellosaurus_dump_in_dictionary_format)
        utils.save_pickle_file(cellosaurus_informations_to_wikidata_ids,
                               "../tests/test_full_cellosaurus_to_wikidata.pickle")

        self.assertEqual(cellosaurus_informations_to_wikidata_ids["references"]['25400923'], 'Q42064754')


class TestAuxiliaryFunctions(unittest.TestCase):

    def test_add_reference_to_wikidata(self):
        pubmed_id = "mock_id"
        utils.add_reference_to_wikidata(pubmed_id)
        self.assertEqual("bla", "bla")


class TestPickleFunctions(unittest.TestCase):

    def test_save__load_pickle(self):
        test_dictionary = {"a": 1, "b": 2}

        utils.SerializeData(test_dictionary, "/tmp/test.pickle")
        test_dictionary_after_processing = utils.DeserializeData("/tmp/test.pickle")

        os.remove("/tmp/test.pickle")

        self.assertEqual(test_dictionary, test_dictionary_after_processing)


class TestCreate_UpdateClass(unittest.TestCase):

    def test_CreateUpdate_object_creation(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
        wikidata = utils.QueryingWikidata()
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

        old_release = utils.load_pickle_file("../tests/release_object_before_refactoring.pickle")

        self.assertEqual(old_release.references, Release.references)

    def test_Initialisation_Data(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
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

        old_release = utils.load_pickle_file("../tests/release_object_before_refactoring.pickle")

        new_output_of_InitialisationData = Release.InitialisationData("CVCL_2260")
        old_output_of_InitialisationData = old_release.InitialisationData("CVCL_2260")

        print(new_output_of_InitialisationData)

        self.assertEqual(new_output_of_InitialisationData, old_output_of_InitialisationData)


    def test_InsertionWikidata(self):

        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus_create.txt")

        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/test_full_cellosaurus_to_wikidata_create.pickle")


        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
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

        output_of_InitialisationData = Release.InitialisationData("CVCL_VR94")

        Release.InsertionWikidata("CVCL_VR94",
                               data=output_of_InitialisationData)
        self.assertEqual(1, 1)


    def test_UpdateWikidata(self):

        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
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

        old_release = utils.load_pickle_file("../tests/release_object_before_refactoring.pickle")
        old_output_of_InitialisationData = old_release.InitialisationData("CVCL_2260")

        Release.UpdateWikidata("CVCL_2260",
                               data=old_output_of_InitialisationData)
        self.assertEqual(1, 1)


class TestCellossaurusCellLine(unittest.TestCase):

    def test_CellossaurusCellLine_object_creation(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.categories("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
        wikidata = utils.QueryingWikidata()
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        cell_line = utils.CellossaurusCellLine(wdi_login_object=login,
                                      release_qid=releaseID,
                                      cellosaurus_dictionary=cellosaurus_dump_in_dictionary_format,
                                      wikidata_dictionary_with_existing_cell_lines=wikidata,
                                      references=references,
                                      species=species,
                                      categories=categories,
                                      diseases=diseases,
                                      cell_line_id="CVCL_2260")

        print(cell_line)

        self.assertEqual(cell_line.cell_line_id, "CVCL_2260")





class TestMakeStatements(unittest.TestCase):
    def test_make_statement(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")
        references = the_so_called_correspondance["references"]
        statement = utils.make_statement(statement_property="P31",
                                         statement_value="Q5",
                                         references=references)

        statement_native_wdi = wdi_core.WDItemID(value="Q5",
                                                 prop_nr="P31",
                                                 references=references)
        self.assertEqual(statement, statement_native_wdi)


if __name__ == '__main__':
    unittest.main()
