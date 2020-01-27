# NCBI_API_KEY needs to be set ahead of metapub load
import os
os.environ["NCBI_API_KEY"] = "e58792b53033b8b644acf76c745486831907"

import lxml
from metapub import PubMedFetcher
from metapub import PubMedArticle
import Levenshtein
import streamlit as st
import pandas as pd
import requests

st.title("Metapub Toolkit")

st.header("Pubmed Advanced Search")

fetch = PubMedFetcher()

search = st.text_input("Pubmed Search", value="central governor")
retmax = st.number_input("Maximum search hits", value=15)

@st.cache
def search_pubmed(*args, **kwargs):
    return fetch.pmids_for_query(*args, **kwargs)

@st.cache(hash_funcs={PubMedArticle: id})
def get_article(pmid):
    return fetch.article_by_pmid(pmid)

@st.cache
def get_citedby(pmid):
    req = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id={}&id={}".format(pmid, pmid))
    out = []
    if req is not None:
        stuff = lxml.etree.fromstring(req.content)
        for event, elem in lxml.etree.iterwalk(stuff, events=('end',), tag='Id'): 
            out.append(elem.text)
    return out



pmids = []
if search: 
    st.write("Hang on a sec while we fetch those articles...")
    pmids = search_pubmed(search, retmax=retmax)

st.subheader("Search Results")

# use Levenshtein distance to determine each article's relevance
#   to the search phrase.

#res = {'relevance': [], 'pmid': [], 'title': [], 'url': [], 'year': [], 'cost': []}
res = {'relevance': [], 'pmid': [], 'title': [], 'cit_count': [], 'year': []}


for pmid in pmids:
    art = get_article(pmid)
    cits = get_citedby(pmid) 

    res['relevance'].append(Levenshtein.distance(search, art.title))
    res['pmid'].append(pmid)
    res['title'].append(art.title)
    res['cit_count'].append(len(cits))
    res['year'].append(art.year)
    #res['cost'].append(0)
    #res['url'].append(art.url)

if res:
    # start already sorted on relevance
    df = pd.DataFrame(res)
    st.dataframe(df)



