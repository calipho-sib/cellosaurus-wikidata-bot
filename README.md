# <center>Wikidata Cellosaurus Bot</center>

***************************
<center><img src="src/SIB_logo.png" style="width: 200px;"/></center>
***************************

*<center>This bot was developed from the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) library. It allow to integrate cell lines data from [Cellosaurus](https://web.expasy.org/cellosaurus/) to [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).</center>*

## Installation

First, you have to clone the bot from Git Hub and install The wikidataIntegrator library:

		git clone <l'adresse http du git>
		cd CellosaurusWikiBot
		python setup.py install

## Requirements

### A Wikidata account:

+ An Wikidata account ( login and password ). If you do not have one, you can [create a Wikidata account](https://www.wikidata.org/w/index.php?title=Special:CreateAccount&returnto=Q27971192).

Fill your user id and password in the file **local.py**:

	#!/Users/leliadebornes/anaconda3/bin/python3

	WDUSER="#User"
	WDPASS="#Password"
*Replace #User and #Password by your user id and password in Wikidata.*

### Cellosaurus release:


+ The wikidata item of the Cellosaurus Item. ( example: [*Q27971192*](https://www.wikidata.org/wiki/Q27971192) ). If the item does not exist, [create it](https://www.wikidata.org/wiki/Special:NewItem).

## Run the bot

### Cellosaurus dump:

If you have already a dump of the Cellosaurus database in .txt format, you can use it. On the other hand, the bot will automatically will upload it for you. 


For run the bot with the Wikidata relase id (#releaseid) and optionnaly the cellosaurus dump in .txt format (#cellosaurus.txt) :

	./Main.py #releaseid #cellosaurus.txt




 
