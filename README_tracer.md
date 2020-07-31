# README


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata

Function to update wikidata cell lines is partially working. 


### Last known issues:

- Some publications are not on Wikidata yet 
(Need to code functions to add them to Wikidata)
- The Fatameh tool, which was previously used to add publications to Wikidata,
 is not mantained anymore.
- Likely the best option would be to clone the Fatameh repository and try and
rebuild it as a python module (https://phabricator.wikimedia.org/source/tool-fatameh/browse/master/)


#### Progress

- Refactored function that matches RX to Wikidata items.
- Pubmed and DOIs are now matched to Wikidata normally
- Issues in matching references and diseases are saved in an error folder
- Refactored taxon id query functions to query individually
- Refactored taxon id query functions to query once for all (improve performance)
- Publications that are on Wikidata now are normally added. 


### Notes:

CC, AG, ST are currently ignored

DR that is not from OBO is currently ignored

- 
