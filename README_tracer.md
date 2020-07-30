# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata

Function to update wikidata cell lines is partially working. 


### Last known issues:

The references are still not being added to Wikidata.
Need to code auxiliary functions. 

The new way of querying taxons has led to a bug. Taxon ids are not being updated.

The query for taxon ids is not scaling well for large cellosaurus dumps.

#### Progress

- Refactored function that matches RX to Wikidata items.
- Pubmed and DOIs are now matched to Wikidata normally
- Issues in matching references and diseases are saved in an error folder
- Refactored taxon id query functions to query individually
- Refactored taxon id query functions to query once for all (improve performance)


### Notes:

CC, AG, ST are currently ignored

DR that is not from OBO is currently ignored

- 