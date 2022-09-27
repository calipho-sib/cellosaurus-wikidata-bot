#!/usr/bin/python3


"""
Updates the Wikidata items relative to the cells in the Cellosaurus dump of interest. 

It takes 3 arguments: 
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on wikidata 
were saved after running "prepare_files.py"
- 3rd: The folder for errors.
- 4th: The QID for the Cellosaurus release on Wikidata   

 Example:
 $python3 update_wikidata.py project/test_cellosaurus.txt dev/pickle_files dev/errors Q87574023 
 """

import json
import os
import pickle
import sys
import time
from pprint import pprint

import pandas as pd
import requests
from SPARQLWrapper import JSON, SPARQLWrapper
from tqdm import tqdm
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login

import src.utils as utils
from src.cellosaurusbot import *
from src.format import format_cellosaurus_dump_as_dictionary
from src.local import WDPASS, WDUSER
from src.query import *
from src.utils import *
from src.wdi_wrapper import *


def main():

    # -----------------INPUT-------------------------#

    cellosaurus_dump_path = sys.argv[1]
    assert cellosaurus_dump_path, "You need to add a Cellosaurus Dump"

    cellosaurus_dump_in_dictionary_format = format_cellosaurus_dump_as_dictionary(
        cellosaurus_dump_path
    )

    url = "https://w.wiki/3Uxc"
    session = requests.Session()  # so connections are recycled
    resp = session.head(url, allow_redirects=True)
    url_sparql = resp.url.replace(
        "https://query.wikidata.org/#", "https://query.wikidata.org/sparql?query="
    )
    r = requests.get(url_sparql, params={"format": "json"})
    df = pd.json_normalize(r.json()["results"]["bindings"])
    print(df)
    print(df.columns)
    login = wdi_login.WDLogin(WDUSER, WDPASS)

    df["qid"] = [url.split("/")[4] for url in df["item.value"]]

    for cellosaurus_id in tqdm(cellosaurus_dump_in_dictionary_format):

        if cellosaurus_id in df["cellosaurus.value"].values:
            print("==========")
            if (
                cellosaurus_dump_in_dictionary_format[cellosaurus_id]["hPSCreg"]
                == "NULL"
            ):
                print(f"Bad id for cell line {cellosaurus_id}")
                data_to_add_to_wikidata = [
                    wdi_core.WDBaseDataType.delete_statement("P9554")
                ]
                data_to_add_to_wikidata.append(
                    wdi_core.WDExternalID(value=cellosaurus_id, prop_nr="P3289")
                )

                df_now = df[df["cellosaurus.value"] == cellosaurus_id]
                properties_to_append_value = ["P3289"]
                wd_item = wdi_core.WDItemEngine(
                    wd_item_id=df_now["qid"].values[0],
                    data=data_to_add_to_wikidata,
                    append_value=properties_to_append_value,
                )
                a = wd_item.write(login, bot_account=True,)
                print(a)


if __name__ == "__main__":
    main()

