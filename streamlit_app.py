# streamlit_app.py

import streamlit as st
import pandas as pd
import os
import tempfile
import warnings
from gene_cocktail_analyser import GeneCocktailAnalyser

# Suppress warnings
warnings.filterwarnings("ignore")

# Streamlit app title
st.title("Gene Cocktail Analyser")

uploaded_cocktail = st.file_uploader("Upload Cocktail File (CSV)", type=["csv"])
cocktail_filename = uploaded_cocktail.name if uploaded_cocktail else None

uploaded_filters = st.file_uploader("Upload Filters File (CSV)", type=["csv"])
filters_filename = uploaded_filters.name if uploaded_filters else None

if uploaded_cocktail and uploaded_filters:
    with tempfile.TemporaryDirectory() as tmpdirname:

        # Set the current working directory to the temp directory
        os.chdir(tmpdirname)

        cocktail_df = pd.read_csv(uploaded_cocktail)
        filters_df = pd.read_csv(uploaded_filters)

        # Write cocktail_df to a temporary CSV
        temp_cocktail = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        cocktail_df.to_csv(temp_cocktail.name, index=False)

        # Write filters_df to a temporary CSV
        temp_filters = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        filters_df.to_csv(temp_filters.name, index=False)

        # Now pass the temporary file names to the GeneCocktailAnalyser
        analyser = GeneCocktailAnalyser(temp_cocktail.name, temp_filters.name)
        analyser.process_data()
        st.write("Uploaded files processed!")

        # Display results and plot visualizations
        if st.button("Display Re    sults"):
            st.write("Displaying results...")
            analyser.display_results()

        if st.button("Plot Visualizations"):
            st.write("Plotting visualizations...")
            analyser.plot_visualizations()
            st.write("Visualizations plotted!")

        # Once done with the analyser, delete the temporary files
        os.remove(temp_cocktail.name)
        os.remove(temp_filters.name)
