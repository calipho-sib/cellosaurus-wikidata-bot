# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata


## Current status:

Function to update wikidata cell lines is partially working. 


### Last known issues:

The references for [ZR-75-27](https://www.wikidata.org/wiki/Q54996118) were not added to Wikidata. 
RX   DOI=10.1016/B978-0-12-333530-2.50009-5;
RX   PubMed=688225;

The run of the code froze after updating the first (out of 4) test cell lines.

### What is working: 

DI, OX, SX and CA were properly added:
DI   NCIt; C4194; Invasive ductal carcinoma, not otherwise specified
OX   NCBI_TaxID=9606; ! Homo sapiens

### Notes:

Information in "CC" is currently ignored:
CC   Doubling time: 144 hours, at 14th passage (PubMed=688225).
CC   Derived from metastatic site: Pleural effusion
AG is currently ignored


- 