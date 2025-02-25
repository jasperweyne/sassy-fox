import streamlit as st
import plotly.express as px
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

        page = 'Actueel'
        if src.authenticated:
            st.markdown("### Navigatie")
            pages = ['Actueel', 'Gebruiker']
            page = st.radio('Selecteer pagina', pages)
            st.header(page)

        if page == 'Gebruiker':
            user_view(src)
        else:
            basic_view(src)

def basic_view(src: data.Data):
    registrations = src.registrations()
    activities = registrations['name'].unique()

    col1, col2 = st.columns(2)
    col1.metric("Aantal zichtbare activiteiten", len(activities))
    col2.metric("Totaal aantal aanmeldingen", len(registrations))

    with st.expander('Filter activiteiten'):
        activities = st.multiselect('Weergeven Activiteiten', activities, default=activities)
    registrations = registrations[registrations['name'].isin(activities)]

    fig_regs = px.histogram(
        registrations,
        x='name',
        title='Aanmeldingen per activiteit',
        labels={'name':'Activiteit'}
    )
    st.write(fig_regs)

    registrations = registrations.sort_values('registrations:created')
    registrations['cumulative'] = registrations.groupby('name').cumcount()
    fig_time = px.line(
        registrations,
        x='registrations:created',
        y='cumulative',
        color='name',
        title='Aanmeldingen over tijd',
        labels={'registrations:created':'Datum', 'cumulative':'Aanmeldingen', 'name':'Activiteit'}
    )
    st.write(fig_time)

def user_view(src: data.Data):
    relations = src.user_relations()
    registrations = src.user_registrations()

    col1, col2, col3 = st.columns(3)
    col1.metric("Totaal aantal groepen", len(relations))
    col2.metric("Totaal aantal aanmeldingen", len(registrations))
    col3.metric("Totale bijdrage activiteiten", f"€ {registrations['option:price'].sum() / 100}")

    bins = st.slider('Aantal datumgroepen', 2, 100)
    fig_activities = px.histogram(
        registrations,
        x="activity:start",
        marginal="rug",
        title='Aantal aanmeldingen over tijd',
        labels={'activity:start':'Periode'},
        nbins=bins
    )
    st.write(fig_activities)

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
            st.rerun()

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
            st.rerun()

if __name__ == "__main__":
    main()