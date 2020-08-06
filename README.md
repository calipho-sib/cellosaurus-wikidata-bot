# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata

Function to update wikidata cell lines is partially working. 


### Last known issues:

- Some publications are not on Wikidata yet 
(Need to code functions to add them to Wikidata)
- Need to integrate wdi_core.wdi_helpers.PubmedItem to code. 
- Need to plan 2-step process (add to Wikidata, and then update all lines)
- Fix errors with NCIT when preparing files
- Fix code to not re-run queries to wikidata. 


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
- Found out that that function is deprecated. Currently this is covered by another set of 
functions that are described [here](https://github.com/SuLab/WikidataIntegrator/blob/adb4ab7f23b3a080dcf2f038191dd3d23c511418/wikidataintegrator/wdi_helpers/publication.py)
- Reorganized code in utils.py in different source files, which are slightly easier to navigate now. 
- Prepared code to add new lines when they are missing.

### Runs for release 35 ###

I have loaded cellosaurus release 35. There are  18183 unique references on the dump. 
This leads to 3-4 hours of required Wikidata queries. 
It is possible that a local database search would be more appropriate, due to the large number of requests. 

Luckly, this has to be run only once. Then I can save and check in the matches for future reference.

### Notes:

CC, AG, ST are currently ignored

DR that is not from OBO is currently ignored

- 