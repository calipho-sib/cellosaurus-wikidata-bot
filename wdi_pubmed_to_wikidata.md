# Using Wikidata Integrator to add articles to Wikidata

In this tutorial, I will show how to use the Wikidata Integrator to add an entry for an biomedical article from PubMed to Wikidata via its PubMed id.

First, let's see what happens for a PMID which is already there. 

The example PMID will be 32180547, which points to the article [Wikidata as a knowledge graph for the life sciences
](https://elifesciences.org/articles/52614).

The credentials for Wikidata are in src.local stored in the variables "WDUSER" and "WDPASS."



```python
import wikidataintegrator as wdi
from src.local import WDUSER, WDPASS


pubmed_id = 32180547
login_instance = wdi.wdi_login.WDLogin(WDUSER, WDPASS)

item = wdi.wdi_helpers.publication.europepmc_api_to_publication(pubmed_id, id_type="pmid")


```

    https://www.wikidata.org/w/api.php
    Successfully logged in as CellosaurusBot



```python
print(item)
```

    <wikidataintegrator.wdi_helpers.publication.Publication object at 0x7f3d653d5c88>


In the previous steps, we built the structure of the article in Wikidata Integrator, 
but it still hasn't been sent to Wikidata.

Let's run the function to try and add it to WIikidata. If it is already on Wikidata,
we get a tuple containing the Wikidata item, an empty list and a "True" response:


```python
item.get_or_create(login_instance)
```




    ('Q87830400', [], True)



Now let's try it with an PMID which is not on Wikidata yet. 
I will look for articles that have just been published.

The article [ChAdOx1 nCoV-19 vaccine prevents SARS-CoV-2 pneumonia in rhesus macaque](https://www.nature.com/articles/s41586-020-2608-y) is
very important, but it still isn't on Wikidata. I've searched for its title on [PubMed](https://pubmed.ncbi.nlm.nih.gov/32731258/) and got its PMID:
32731258.

Let's do it!


```python
pubmed_id = 32731258
login_instance = wdi.wdi_login.WDLogin(WDUSER, WDPASS)

item = wdi.wdi_helpers.publication.europepmc_api_to_publication(pubmed_id, id_type="pmid")

item.get_or_create(login_instance)
```

    https://www.wikidata.org/w/api.php
    Successfully logged in as CellosaurusBot
    Error while writing to Wikidata
    {'error': {'code': 'modification-failed', 'info': 'Must be at least one character long', 'messages': [{'name': 'wikibase-validator-too-short', 'parameters': ['1', ''], 'html': {'*': 'Must be at least one character long'}}], '*': 'See https://www.wikidata.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/mailman/listinfo/mediawiki-api-announce&gt; for notice of API deprecations and breaking changes.'}, 'servedby': 'mw1289'}





    ('',
     ['unknown publication type, assuming publication'],
     wikidataintegrator.wdi_core.WDApiError({'error': {'code': 'modification-failed',
                                              'info': 'Must be at least one character long',
                                              'messages': [{'name': 'wikibase-validator-too-short',
                                                'parameters': ['1', ''],
                                                'html': {'*': 'Must be at least one character long'}}],
                                              '*': 'See https://www.wikidata.org/w/api.php for API usage. Subscribe to the mediawiki-api-announce mailing list at &lt;https://lists.wikimedia.org/mailman/listinfo/mediawiki-api-announce&gt; for notice of API deprecations and breaking changes.'},
                                             'servedby': 'mw1289'}))



Oh no, we had an API error!
