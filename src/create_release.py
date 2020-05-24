import utils
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from local import WDUSER, WDPASS


cellosaurus_dump_in_dictionary_format = utils.CellosaurusToDictionary("../project/test_cellosaurus.txt")
cellosaurus_informations_to_wikidata_ids = utils.correspondance(cellosaurus_dump_in_dictionary_format)
print(cellosaurus_dump_in_dictionary_format)
utils.save_pickle_file(cellosaurus_informations_to_wikidata_ids, "../tests/cellosaurus_informations_to_wikidata_ids.pickle")

the_so_called_correspondance = cellosaurus_informations_to_wikidata_ids
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
utils.save_pickle_file(Release, "../tests/release_object_before_refactoring.pickle")