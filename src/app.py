import streamlit as st
from datetime import datetime
from . import data

def main():
    st.title('Kiwi - Analysetool')
    st.markdown("""Welkom bij de Kiwi analysetool. Met deze tool kan je in
    realtime analyses en grafieken genereren op basis van de beschikbaar
    gestelde data uit de Kiwi GraphQL API. Wil je zelf de ruwe data bekijken?
    Download dan een tool zoals bijvoorbeeld
    [GraphQL Playground](https://www.electronjs.org/apps/graphql-playground) en
    vul het API adres in.
    """)

    data_source = source()
    if data_source:
        src = data.Data(data_source['url'], data_source['token'])
        activities = src.registrations()
        st.table(activities)

        if src.authenticated:
            groups = src.groups()
            st.table(groups)

def source():
    # initialize session values
    if 'sources' not in st.session_state:
        st.session_state.sources = {}

    # no source added
    source_cnt = len(st.session_state.sources)
    if source_cnt == 0:
        st.markdown("""Er is nog geen Kiwi bron ingesteld. Stel deze
        hieronder in om te beginnen.""")
        source_form()
        return None
    
    # source view
    names = st.session_state.sources.keys()
    selected = None
    if source_cnt == 1:
        selected = list(names)[0]
    else:
        selected = st.radio("Selecteer een bron", names)

    if selected:
        now = datetime.now()
        api = f"API adres: {st.session_state.sources[selected]['url']}"
        st.markdown(f"""Bron: {selected} - {now.strftime('%d-%m-%Y %H:%M:%S')} - {api}""")
        
    # add source
    with st.expander("Beheer Kiwi bronnen"):
        delete_label = 'Huidige bron verwijderen' if source_cnt == 1 else 'Alle bronnen verwijderen'
        if st.button(delete_label):
            st.session_state.sources = {}
            st.experimental_rerun()

        source_form()

    # return selected url, if available
    if selected:
        return st.session_state.sources[selected]
    
    return None

def source_form():
    with st.form("source_selector"):
        st.markdown("Voeg een Kiwi bron toe")
        name = st.text_input("Naam", placeholder="Website")
        url = st.text_input("Adres (URL)", placeholder="https://kiwi.website.com")
        token = st.text_input("Sessie token (geavanceerd)", placeholder="Leeglaten indien onbekend")

        submitted = st.form_submit_button("Opslaan")
        if submitted:
            st.session_state.sources[name] = {
                'url': url + '/api/graphql/',
                'token': token if token != '' else None,
            }
            st.experimental_rerun()

if __name__ == "__main__":
    main()