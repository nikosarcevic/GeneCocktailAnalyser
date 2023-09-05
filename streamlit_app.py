import streamlit as st
import pandas as pd
import os
import tempfile
import warnings
from gca_streamlit import GeneCocktailAnalyser

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
            st.write("\n".join(results))

        if st.button("Plot Visualizations"):
            st.write("Plotting visualizations...")
            # Assuming plot_visualizations will create a plot using matplotlib or similar
            # Update plot_visualizations to return the created figure
            fig = analyser.plot_visualizations()
            st.pyplot(fig)

        # Cleanup temporary files
        os.remove(temp_cocktail.name)
        os.remove(temp_filters.name)
