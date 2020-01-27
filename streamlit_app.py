from metapub import PubMedFetcher

import streamlit as st

st.title("Metapub Toolkit")

st.header("Pubmed Advanced Search")

fetch = PubMedFetcher()

search = st.text_input("Pubmed Search")

results = []
if search: 
    results = fetch.pmids_for_query(search)

st.subheader("Search Results")

for pmid in results:
    art = fetch.article_by_pmid(pmid)
    st.write("[{}]({})".format(art.title, art.url))


