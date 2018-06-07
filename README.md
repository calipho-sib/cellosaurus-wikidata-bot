# <center>Cellosaurus Wikidata Bot</center>

***************************
<p align="center">
  <img src="img/WikiCello.png" width="300"/>
</p>
***************************

**<center>Cellosaurus Bot allows to integrate cell lines from [Cellosaurus](https://web.expasy.org/cellosaurus/) to [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).**

**It was developed from the the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) library.</center>**
## Installation

First, you have to clone the bot from Git Hub and install the submodule WikidataIntegrator:

		git clone https://github.com/calipho-sib/cellosaurus-wikidata-bot.git
		cd cellosaurus-wikidata-bot
		git submodule init
		git submodule update
		cd WikidataIntegrator
		python setup.py install 
		
For test the correct installation, start a python console and execute the following:

	>>>from wikidataintegrator import wdi_core
	>>>my_first_wikidata_item = wdi_core.WDItemEngine(wd_item_id='Q5')
And print the json representation of the item:
	
	>>>my_first_wikidata_item.get_wd_json_representation()
## Requirements


### Cellosaurus release:


+ The wikidata item of the Cellosaurus release Item. ( example: [*Q27971192*](https://www.wikidata.org/wiki/Q27971192) ). If the item does not exist, [create it](https://www.wikidata.org/wiki/Special:NewItem).

## Run the bot

### Cellosaurus dump:

If you have already a dump of the Cellosaurus database in .txt format, you can use it. Move the file in **project/**.
If not, the bot will automatically upload it for you. 


To run the bot with the Wikidata relase id (#releaseid) and optionnaly the cellosaurus dump in .txt format (#cellosaurus.txt) :

	./Main.py #releaseid #cellosaurus.txt

## Structure

| | |
|:--:|:--|
| <img src="img/Bot_structure.png" style="width: 400px;"/>|  **conf/WikidataIntegrator** : the WikidataIntegrator library </br> **doc/ERRORS/species.txt** : species that are not in Wikidata </br> **doc/Fatameh_errors.txt** : errors that occur during references item creation with Fatameh </br>  **doc/ERRORS/diseases/more\_than_1.txt** : diseases (NCIt) that correspond to more than 1 item in Wikidata </br> **doc/ERRORS/diseases/not_in.txt** : diseases that are not in Wikidata </br> **project/cellosaurus.txt** : the provided or uploaded dump of Cellosaurus </br> **project/category.txt** : the cell lines categories in Cellosaurus with their correspondance to Wikidata items </br> **results/new_Qids.txt** : the new cell lines items in Wikidata that were created </br> **results/Qids\_2_delete.txt** : the Wikidata items that have to be deleted </br> **results/cell\_line_duplicate.txt** : cell lines that are in duplicate in Wikidata </br> **src/utils.py** : a python librairy used in **Main.py** </br> **Main.py** : the bot code </br> **ShEX_model/Wikidata\_Cellosaurus\_celllines.shex** : a shex model that define contrains on a cell line item |

## Main functions 

The Cellosaurus bot will:

+ Create Wikidata items for new cell lines in Cellosaurus release.
+ Update Wikidata items for changes in cell lines informations in Cellosaurus release.
+ Inform you for Wikidata cell lines items to delete (in **results/Qids_2_delete.txt**).
+ Inform you for Wikidata cell lines items that are in duplicate in Wikidata (in **results/cell_line_duplicate.txt**).

## Example

For Cellosaurus release 26: 

	./Main.py Q53439980
	>>------------------- Would you download a Cellosaurus dump?(y/n) -------------------
	y #if you do not have a cellosaurus dump

In this case, the bot will check the item id for the release, upload the last Cellosaurus release dump and start the integration of Cellosaurus data. 

	./Main.py Q53439980 /project/cellosaurus.txt 

In this case, the dump is provided, the bot will check the item id for the release, check the Cellosaurus dump and start the integration of Cellosaurus data.
