#!/bin/env bash
RELEASE=release_43
RELEASE_ID=Q114095342

mkdir $RELEASE
echo $RELEASE >> .gitignore
cd $RELEASE
wget -nc ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt
cd ..

#python3 prepare_files.py $RELEASE/cellosaurus.txt pickle_files errors
#python3 add_articles.py errors
python3 prepare_files.py $RELEASE/cellosaurus.txt pickle_files errors

python3 check_lines_on_wikidata.py $RELEASE/cellosaurus.txt pickle_files errors $RELEASE_ID

python3 update_wikidata.py $RELEASE/cellosaurus.txt pickle_files errors $RELEASE_ID