#!/usr/bin/python3
from utils import DeserializeData, SerializeData , correspondance, categories, Set, Create_Update, CellosaurusToDictionary, QueryingWikidata, add_reference_to_wikidata
import os


os.chdir("/home/lubianat/Documents/cellosaurus-wikidata-bot")


cellosaurus_dump_in_dictionary_format = CellosaurusToDictionary("./project/test_cellosaurus.txt")
cellosaurus_informations_to_wikidata_ids = correspondance(cellosaurus_dump_in_dictionary_format)

SerializeData(cellosaurus_informations_to_wikidata_ids,"src/test_full_cellosaurus_to_wikidata.pickle")