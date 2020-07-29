# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata


## Current status:

Function to update wikidata cell lines is partially working. 


### Last known issues:

The references were not added to Wikidata

The NCI thesaurus term is saved as missing on wikidata, but it is there. 

#### Progress

- Refactored function that matches RX to Wikidata items.
- Pubmed and DOIs are now matched to Wikidata normally


### What is working: 

* [ZR-75-27](https://www.wikidata.org/wiki/Q54996118)
ID, AC, SY, DI, OX, SX and CA were properly added:

* [ZR-75-30](https://www.wikidata.org/wiki/Q54996119)
ID, AC, SY, DI, OX, SX and CA were properly added:

The references to OBO ontologies were properly added.
DR   BTO; BTO:0004915
DR   CLO; CLO_0009728
DR   EFO; EFO_0001263

* [ZR-75-9a1](https://www.wikidata.org/wiki/Q54996121)
ID, AC, SY, DI, OX, SX and CA were properly added:
HI (parent cell line) was properly added. 

* [ZR-75-B](https://www.wikidata.org/wiki/Q54996122)
ID, AC, SY, DI, OX, SX and CA were properly added:
HI (parent cell line) was properly added. 

### Notes:

CC, AG, ST are currently ignored

DR that is not from OBO is currently ignored

- 