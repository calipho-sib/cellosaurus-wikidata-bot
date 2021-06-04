# <center>Cellosaurus Wikidata Bot</center>

***************************
<p align="center">
  <img src="img/WikiCello.png" width="300"/>
</p>
***************************

**<center>Cellosaurus Bot allows to integrate cell lines from [Cellosaurus](https://web.expasy.org/cellosaurus/) to [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).**

**It was developed based on the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) library.</center>**

## Main functions 

The Cellosaurus bot will:

+ Create Wikidata items for new cell lines in Cellosaurus release.
+ Update Wikidata items for changes in cell lines informations in Cellosaurus release.
# Running the bot 

The bot is based on the dumps of the Cellosaurus database. The first step for making the integration is to download the dump of the current release from the Cellosaurus website. The FTP link is:

ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt

You can create a folder for the release and add it there. Here is an example for release 36:

`mkdir release_36
echo release_36 >> .gitignore
cd release_36
wget ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.txt
`

Now that you have the file, it is worth taking a look at it on your text editor. 

There are 3 main scripts that process the release and integrate to Wikidata: 
* __prepare_files.py__
* __check_lines_on_wikidata.py__
* __update_wikidata.py__

The goal of __prepare_files.py__ is to parse the dump and save a Python object that contains the cell line information in a Wikidata-compatible format. 

It takes 3 arguments: 
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on wikidata 
were saved after running "prepare_files.py"
- 3rd: The folder for errors.

For example:
`python3 prepare_files.py release_38/cellosaurus.txt pickle_files errors `

Some articles might not be on Wikidata at the time of the release. These will be logged under the folder for errors.

For adding articles to Wikidata, run:
`python3 add_articles.py errors `

After that, re-run prepare_files to effectively used the newly added articles in the Cellosaurus integration.

The goal of * __check_lines_on_wikidata.py__ is to check if each cell line in the current release is present on Wikidata. Then, it adds to Wikidata the information about any cell lines that are missing.

The second one takes 4 arguments:  
- 1st: The path to the .txt of the Cellosaurus dump
- 2nd: The path to the folder where the pickle file and cell lines on Wikidata were saved after running __prepare_files.py__
- 3rd: The folder for errors.
- 4th: The QID for the Cellosaurus release on Wikidata   

You will have to check Wikidata manually for the ID of the release. For release 36, the ID is [Q100993240](https://www.wikidata.org/wiki/Q100993240).
For release 36, it is [Q106915727](https://www.wikidata.org/wiki/Q106915727).

Notice that you will need the Wikidata user and password of the CellosaurusBot for that operation. The script looks for it in `src/local.py`.  Notice that the credentials should not be commited to GitHub.

For example:
`python3 check_lines_on_wikidata.py release_36/cellosaurus.txt pickle_files errors Q100993240`


Now that all the cell lines are represented on Wikidata, we can update the information for all of them (including inter-cell line links):

`python3 update_wikidata.py release_36/cellosaurus.txt pickle_files errors Q100993240`

# Acknowledgments

The CellosaurusBot now is a 2020 remake of the CellosaurusBot developed in 2018. 
The following people contributed directly to this project:

* Amos Bairoch
* Lelia Debornes
* Tiago Lubiana
* Andra Waagmeester