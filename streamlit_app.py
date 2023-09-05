import os
import warnings
import streamlit as st
import tempfile
import pandas as pd
from datetime import datetime
from helpers import create_download_link, figure_to_base64, process_files
from gca_streamlit import GeneCocktailAnalyser

def setup_page():
    st.set_page_config(layout="wide")
    st.title("Gene Cocktail Analyser")

def upload_files():
    uploaded_cocktail = st.file_uploader("Upload Cocktail File (CSV)", type=["csv"])
    uploaded_filters = st.file_uploader("Upload Filters File (CSV)", type=["csv"])
    return uploaded_cocktail, uploaded_filters

# Streamlit App
setup_page()
warnings.filterwarnings("ignore")

# Sidebar sections
st.sidebar.header("Menu")

# Analysis
if st.sidebar.button("Analysis"):
    uploaded_cocktail, uploaded_filters = upload_files()

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

            # Allow user to provide a custom name for the report
            filename_input = st.text_input("Enter name for the report:", "")

            # If the user hasn't provided a name, generate a default one based on the current date and time
            filename = filename_input if filename_input else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            if st.button("Download Report as TXT"):
                # Generate the report using the display_results method
                report_lines = analyser.display_results()
                output_str = "\n".join(report_lines)
                link = create_download_link(output_str, filename, "Click here to download the report")
                st.markdown(link, unsafe_allow_html=True)

            if st.button("Display Report"):
                report_lines = analyser.display_results()
                output_str = "\n".join(report_lines)
                st.text(output_str)

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

# Intro
if st.sidebar.button("Intro"):
    st.write("This is the introduction to the Gene Cocktail Analyser.")


# About
if st.sidebar.button("About"):
    st.write("Information about the Gene Cocktail Analyser and its purpose.")

    st.write("Made by Niko Sarcevic, Newcastle University")
    st.write("Visit www.nikosarcevic.com or github.com/nikosarcevic")