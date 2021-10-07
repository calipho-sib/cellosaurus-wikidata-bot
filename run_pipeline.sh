#!/bin/env bash
python3 prepare_files.py release_39/cellosaurus.txt pickle_files errors
python3 add_articles.py errors
python3 prepare_files.py release_39/cellosaurus.txt pickle_files errors


python3 check_lines_on_wikidata.py release_39/cellosaurus.txt pickle_files errors Q100993240