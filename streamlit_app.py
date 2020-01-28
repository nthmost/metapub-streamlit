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


search_options = open("pubmed_search_options.txt").readlines()
st.sidebar.title("Reference")
st.sidebar.header("Pubmed Advanced Query Tags")
for opt in search_options:
    st.sidebar.markdown(opt)

st.title("Metapub Research Assistant")

fetch = PubMedFetcher()

search = st.text_input("Pubmed Advanced Query Engine")
retmax = st.number_input("Maximum search hits", value=15)

# Placeholder for search progress bar
latest_iteration = st.empty()
bar = st.progress(0)

@st.cache(show_spinner=False)
def search_pubmed(*args, **kwargs):
    return fetch.pmids_for_query(*args, **kwargs)

@st.cache(show_spinner=False, hash_funcs={PubMedArticle: lambda x: x.pmid})
def get_article(pmid):
    return fetch.article_by_pmid(pmid)

@st.cache(show_spinner=False)
def get_citedby(pmid):
    req = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id={}&id={}".format(pmid, pmid))
    out = []
    if req is not None:
        try:
            stuff = lxml.etree.fromstring(req.content)
            for event, elem in lxml.etree.iterwalk(stuff, events=('end',), tag='Id'): 
                out.append(elem.text)
        except Exception as err:
            st.write(err)
    return out

pmids = []
if search: 
    latest_iteration.text("Performing NCBI search...")
    bar.progress(5)
    pmids = search_pubmed(search, retmax=retmax)
    bar.progress(95)

st.subheader("Search Results")


#res = {'relevance': [], 'pmid': [], 'title': [], 'url': [], 'year': [], 'cost': []}
res = {'relevance': [], 'pmid': [], 'title': [], 'cit_count': [], 'year': []}


# use Levenshtein distance to determine each article's relevance
#   to the search phrase. This could be replaced by something smarter.
it = 0
num_pmids = len(pmids)
for pmid in pmids:
    art = get_article(pmid)
    cits = get_citedby(pmid) 

    it += 1
    latest_iteration.text(f"Getting PMID {pmid} (article {it}/{num_pmids})")
    bar.progress(100 * int((it/num_pmids)))

    res['relevance'].append(Levenshtein.distance(search, art.title))
    res['pmid'].append(pmid)
    res['title'].append(art.title)

    # lower cit count by 2 to compensate for self-mentions in the eutils XML return.
    res['cit_count'].append(len(cits) - 2)
    res['year'].append(art.year)
    #res['cost'].append(0)
    #res['url'].append(art.url)

if res:
    latest_iteration.text("Done! See results below.")
    # start already sorted on relevance
    df = pd.DataFrame(res)
    #st.dataframe(df)
    st.dataframe(df.style.highlight_max())
    #st.table(res, sort="relevance")

    ## show a chart 
    #st.bar_chart(df)

