import base64
from datetime import datetime
import io
import pandas as pd
import streamlit as st
import os
import tempfile
import warnings

import helpers
from gca_streamlit import GeneCocktailAnalyser
from helpers import analysis_page


# Set the page layout to wide
st.set_page_config(layout="wide")

# Suppress warnings
warnings.filterwarnings("ignore")

# Streamlit app title
st.title("Gene Cocktail Analyser")

st.write("Made by Niko Sarcevic for genetics colleagues")
st.write("Note: this is currently a quick solution and will be polished more in the near future")
st.write("Contact: www.nikosarcevic.com or github.com/nikosarcevic")

if st.sidebar.button("Intro"):
    st.write("This is the introduction to the Gene Cocktail Analyser.")

if st.sidebar.button("Analysis"):
    helpers.analysis_page()

# About
if st.sidebar.button("About"):
    st.write("Information about the Gene Cocktail Analyser and its purpose.")


