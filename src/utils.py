#!/usr/bin/python3

from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login
from SPARQLWrapper import SPARQLWrapper, JSON
from pprint import pprint
import time
import calendar
from datetime import datetime, date
import json
import pickle
import os


def load_cell_line_category_to_wikidata(file):
    """
    Load manually prepared dictionary of 
    Cellosaurus categories and their Wikidata matches.
    """
    cell_line_category_to_wikidata = {}
    with open(file) as file:
        for line in file:
            line = line.split(" (")
            name_on_cellosaurus = line[0]
            category_qid = line[1].strip(")\n")
            cell_line_category_to_wikidata[name_on_cellosaurus] = category_qid
        return cell_line_category_to_wikidata


def write_list(filepath, list):
    with open(filepath, "w") as f:
        for item in list:
            f.write("%s\n" % item)


# Wrapper functions for pickle


def load_pickle_file(pickleFileName):
    """
    Loads a serialized pickle file.
    :param pickeFileName : YourFile.pickle
    :return : a dictionary wich contain YourFile.pickle informations
    """

    with open(pickleFileName, "rb") as file:
        dictionary = pickle.load(file)
    return dictionary


def save_pickle_file(dictionary, pickleFileName):
    """
    Saves a dictionary into a pickle file.
    :param dictionary : the dictionary that you want to serialize
    :param pickleFileName : the name of the file
    """
    with open(pickleFileName, "wb") as file:
        pickle.dump(dictionary, file)
