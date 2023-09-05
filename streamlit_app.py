import streamlit as st
import pandas as pd
import os
import tempfile
import warnings
from gca_streamlit import GeneCocktailAnalyser

# Set the page layout to wide
st.set_page_config(layout="wide")

# Suppress warnings
warnings.filterwarnings("ignore")

# Streamlit app title
st.title("Gene Cocktail Analyser")

uploaded_cocktail = st.file_uploader("Upload Cocktail File (CSV)", type=["csv"])
uploaded_filters = st.file_uploader("Upload Filters File (CSV)", type=["csv"])

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

        analyser = GeneCocktailAnalyser(temp_cocktail.name, temp_filters.name)
        analyser.process_data()
        st.write("Uploaded files processed!")

        if st.button("Display Results"):
            st.write("Displaying results...")
            results = analyser.display_results()
            for line in results:
                st.text(line)

        if st.button("Plot Visualizations"):
            st.write("Plotting visualizations...")

            fig1 = analyser.plot_summary_data()
            st.pyplot(fig1, width=400, height=400)

            fig2 = analyser.plot_frequency_of_matches()
            st.pyplot(fig2, width=400, height=400)

            fig3 = analyser.plot_heatmap()
            st.pyplot(fig3, width=400, height=400)

        # Cleanup temporary files
        os.remove(temp_cocktail.name)
        os.remove(temp_filters.name)
