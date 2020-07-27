# README for tracer bullet


Readme/log for tracer bullet development of the bot to reconcile the
Cellosaurus database to Wikidata


## Current status:

Function to update wikidata cell lines is partially working. 


### Last known issues:

The references for [ZR-75-27](https://www.wikidata.org/wiki/Q54996118) were not added to Wikidata. 
RX   DOI=10.1016/B978-0-12-333530-2.50009-5;
RX   PubMed=688225;

The references for [ZR-75-30](https://www.wikidata.org/wiki/Q54996119) were not added to Wikidata. 
RX   DOI=10.1016/B978-0-12-333530-2.50009-5;
RX   PubMed=688225;
RX   PubMed=3335022;
RX   PubMed=11044355;
RX   PubMed=11414198;
RX   PubMed=16397213;
RX   PubMed=16541312;
RX   PubMed=17157791;
RX   PubMed=19582160;
RX   PubMed=19593635;
RX   PubMed=20070913;
RX   PubMed=20164919;
RX   PubMed=22460905;
RX   PubMed=23151021;
RX   PubMed=23260012;
RX   PubMed=23601657;
RX   PubMed=24009699;
RX   PubMed=24094812;
RX   PubMed=24176112;
RX   PubMed=25485619;
RX   PubMed=25960936;
RX   PubMed=25984343;
RX   PubMed=27397505;
RX   PubMed=28196595;
RX   PubMed=23260012;
RX   PubMed=30894373;
RX   PubMed=31068700;
RX   PubMed=31395879;


The references for [ZR-75-9a1](https://www.wikidata.org/wiki/Q54996121) were not added to Wikidata. 

RX   PubMed=2713239;

The references for [ZR-75-B](https://www.wikidata.org/wiki/Q54996122) were not added to Wikidata. 

RX   PubMed=6178756;
RX   PubMed=17157791;
RX   PubMed=18516279;
RX   PubMed=24094812;
RX   PubMed=24162158;
RX   PubMed=24176112;
RX   PubMed=25960936;

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