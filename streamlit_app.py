# NCBI_API_KEY needs to be set ahead of metapub load
import os
os.environ["NCBI_API_KEY"] = "e58792b53033b8b644acf76c745486831907"

from metapub import PubMedFetcher
from metapub import PubMedArticle
import Levenshtein
import streamlit as st
import pandas as pd

st.title("Metapub Toolkit")

st.header("Pubmed Advanced Search")

fetch = PubMedFetcher()

search = st.text_input("Pubmed Search", value="central governor")


@st.cache
def search_pubmed(*args, **kwargs):
    return fetch.pmids_for_query(*args, **kwargs)

@st.cache(hash_funcs={PubMedArticle: id})
def get_article(pmid):
    return fetch.article_by_pmid(pmid)


pmids = []
if search: 
    st.write("Hang on a sec while we fetch those articles...")
    pmids = search_pubmed(search, retmax=15)

st.subheader("Search Results")

# use Levenshtein distance to determine each article's relevance
#   to the search phrase.

res = {'pmid': [], 'relevance': [], 'title': [], 'url': [], 'year': [], 'cost': []}


for pmid in pmids:
    art = get_article(pmid)

    res['pmid'].append(pmid)
    res['title'].append(art.title)
    res['url'].append(art.url)
    res['relevance'].append(Levenshtein.distance(search, art.title))
    res['year'].append(art.year)
    res['cost'].append(0)

if res:
    df = pd.DataFrame(res)
    st.dataframe(df)



