import unittest
import os
import utils
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from src.local import WDUSER, WDPASS

# login with your Wikidata user and password in local.py

class TestStringMethods(unittest.TestCase):

    def test_loading_of_cellosaurus(self):
        cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary("../project/test_cellosaurus.txt")
        self.assertEqual(cellosaurus_dump_in_dictionary_format["CVCL_E548"]["ID"], '#15310-LN')

    def test_loading_of_cell_lines(self):
        cell_line_to_wikidata_id = utils.query_wikidata_for_cell_lines()
        self.assertEqual(cell_line_to_wikidata_id["CVCL_E548"], 'Q54398957')

    def test_matching_of_cellosaurus_to_wikidata(self):
        cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary("../project/test_cellosaurus.txt")
        cellosaurus_informations_to_wikidata_ids = utils.match_cellosaurus_dump_to_wikidata_items(cellosaurus_dump_in_dictionary_format)
        utils.save_pickle_file(cellosaurus_informations_to_wikidata_ids,
                               "../tests/test_full_cellosaurus_to_wikidata.pickle")

        self.assertEqual(cellosaurus_informations_to_wikidata_ids["references"]['25400923'], 'Q42064754')


class TestPickleFunctions(unittest.TestCase):

    def test_save__load_pickle(self):
        test_dictionary = {"a": 1, "b": 2}

        utils.SerializeData(test_dictionary, "/tmp/test.pickle")
        test_dictionary_after_processing = utils.DeserializeData("/tmp/test.pickle")

        os.remove("/tmp/test.pickle")

        self.assertEqual(test_dictionary, test_dictionary_after_processing)


class TestCellossaurusCellLine(unittest.TestCase):

    def test_CellossaurusCellLine_object_creation(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.get_cell_line_category_to_wikidata("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary("../project/test_cellosaurus.txt")
        wikidata = utils.query_wikidata_for_cell_lines()
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        cell_line = utils.CellossaurusCellLine(wdi_login_object=login,
                                      release_qid=releaseID,
                                      cellosaurus_dump =cellosaurus_dump_in_dictionary_format,
                                      wikidata_dictionary_with_existing_cell_lines=wikidata,
                                      references=references,
                                      species=species,
                                      cell_line_categories=categories,
                                      diseases=diseases,
                                      cell_line_id="CVCL_2260")

        print(cell_line)

        self.assertEqual(cell_line.cell_line_id, "CVCL_2260")

    def test_prepare_for_wikidata_function(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.get_cell_line_category_to_wikidata("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary("../project/test_cellosaurus.txt")
        wikidata = utils.query_wikidata_for_cell_lines()
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        cell_line = utils.CellossaurusCellLine(wdi_login_object=login,
                                      release_qid=releaseID,
                                      cellosaurus_dump=cellosaurus_dump_in_dictionary_format,
                                      wikidata_dictionary_with_existing_cell_lines=wikidata,
                                      references=references,
                                      species=species,
                                      cell_line_categories=categories,
                                      diseases=diseases,
                                      cell_line_id="CVCL_2260")
        data, data_to_delete = cell_line.prepare_for_wikidata()
        print(data)
        print(data_to_delete)

        self.assertEqual(1, 1)


        self.assertEqual(cell_line.cell_line_id, "CVCL_2260")


    def test_update_line_on_wikidata_function(self):
        the_so_called_correspondance = utils.load_pickle_file(
            "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

        species = the_so_called_correspondance["species"]
        references = the_so_called_correspondance["references"]
        categories = utils.get_cell_line_category_to_wikidata("../project/category.txt")
        diseases = the_so_called_correspondance["diseases"]
        cellosaurus_dump_in_dictionary_format = utils.format_cellosaurus_dump_as_dictionary("../project/test_cellosaurus.txt")
        wikidata = utils.query_wikidata_for_cell_lines()
        releaseID = "Q87574023"
        login = wdi_login.WDLogin(WDUSER, WDPASS)

        cell_line = utils.CellossaurusCellLine(wdi_login_object=login,
                                      release_qid=releaseID,
                                      cellosaurus_dump=cellosaurus_dump_in_dictionary_format,
                                      wikidata_dictionary_with_existing_cell_lines=wikidata,
                                      references=references,
                                      species=species,
                                      cell_line_categories=categories,
                                      diseases=diseases,
                                      cell_line_id="CVCL_E548")
        prepared_data = cell_line.prepare_for_wikidata()
        print(prepared_data)
        cell_line.update_line_on_wikidata(data = prepared_data)


        self.assertEqual(cell_line.cell_line_id, "CVCL_E548")


class TestAuxiliaryFunctions(unittest.TestCase):

    def test_add_reference_to_wikidata(self):
        pubmed_id = "mock_id"
        utils.add_reference_to_wikidata(pubmed_id)
        self.assertEqual("bla", "bla")


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
