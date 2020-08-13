# CellosaurusBot 2.0


The CellosaurusBot 2.0 is a 2020 remake of the CellosaurusBot developed in 2018. 

The Cellosaurus Bot allows to integrate cell lines from [Cellosaurus](https://web.expasy.org/cellosaurus/) to [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).

Its core engines are based on the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) library.


# Running the bot 

There are 3 main scripts for running the bot: 
* prepare_files.py
* check_lines_on_wikidata.py
* update_wikidata.py


First, you have to download the current release from the Cellosaurus website. The FTP link is:
ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt


This is the cellosaurus dump. The sequence of commands to add the info there to Wikidata is: 

The first script takes 3 arguments: 
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on wikidata 
were saved after running "prepare_files.py"
- 3rd: The folder for errors.

`python3 prepare_files.py project/cellosaurus.txt pickle_files errors `

This first script will match the IDs on the Cellosaurus dump to the current state of Wikidata (and a couple other things).

The second one takes 4, the original 3 + a fourth: 
- 4th: The QID for the Cellosaurus release on Wikidata   

`python3 check_lines_on_wikidata.py project/cellosaurus.txt pickle_files errors Q96794096`

It checks if any cell line in the current realease is absent on Wikidata. It then adds all the missing cell lines to Wikidata. 



The third updates the info for all cell lines on Wikidata, including the new ones: 
`python3 check_lines_on_wikidata.py project/cellosaurus.txt pickle_files errors Q96794096`

