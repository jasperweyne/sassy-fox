# Sassy Fox
Sassy Fox is an analysis and insights tool for Helpless Kiwi. It uses the Kiwi
GraphQL API to fetch data used during analysis. It support authentication
through a session cookie, which allows for additional insights on restricted
data. It is built using [Streamlit](https://streamlit.io/).

# Usage
To start using Sassy Fox, go to the hosted version on [Streamlit Cloud](https://share.streamlit.io/jasperweyne/sassy-fox/main)
right now! Want to use a local installation? Follow the steps in the 
installation guide. 

# Installation
Make sure you have Python and Pip installed. You can verify this by running:
```bash
pip -V
```

It is advised to use a virtualenv as well. Afterwards, install Streamlit by
running `pip install streamlit`.

To start Sassy Fox, run:
```bash
streamlit run streamlit_app.py
```