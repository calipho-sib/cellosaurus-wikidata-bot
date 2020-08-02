# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata

Function to update wikidata cell lines is partially working. 


### Last known issues:

- Some publications are not on Wikidata yet 
(Need to code functions to add them to Wikidata)
- Need to integrate wdi_core.wdi_helpers.PubmedItem to code. 


#### Progress

- Refactored function that matches RX to Wikidata items.
- Pubmed and DOIs are now matched to Wikidata normally
- Issues in matching references and diseases are saved in an error folder
- Refactored taxon id query functions to query individually
- Refactored taxon id query functions to query once for all (improve performance)
- Publications that are on Wikidata now are normally added. 
- Found that Fatameh(https://phabricator.wikimedia.org/source/tool-fatameh/browse/master/) 
uses Wikidata Integrator (WDI) in the backend to add articles to Wikidata. 
- Found that WDI has a function called "wdi_core.wdi_helpers.PubmedItem" to add articles to Wikidata. 


### Notes:

CC, AG, ST are currently ignored

DR that is not from OBO is currently ignored

- 