from datetime import datetime
import os
import warnings
import streamlit as st
from helpers import create_download_link, figure_to_base64, process_files

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

uploaded_cocktail, uploaded_filters = upload_files()

if uploaded_cocktail and uploaded_filters:
    analyser, temp_cocktail, temp_filters = process_files(uploaded_cocktail, uploaded_filters)
    st.write("Uploaded files processed!")

    # Generate the report using the display_results method
    report_lines = analyser.display_results()
    output_str = "\n".join(report_lines)
    filename_input = st.text_input("Enter name for the report:", "")
    filename = filename_input if filename_input else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    # Button to download the report as a TXT file
    if st.button("Download Report as TXT"):
        link = create_download_link(output_str, filename, "Click here to download the report")
        st.markdown(link, unsafe_allow_html=True)

    # Another button to unveil/display the report on the Streamlit app
    if st.button("Display Report"):
        st.text(output_str)

    if st.button("Plot Visualizations"):
        st.write("Plotting visualizations...")
        fig1 = analyser.plot_summary_data()
        st.pyplot(fig1, width=400, height=400)
        encoded_fig1 = figure_to_base64(fig1)
        plot1_filename = f"{filename_input}_summary_plot.png" if filename_input else "summary_plot.png"
        st.markdown(
            f'<a href="data:image/png;base64,{encoded_fig1}" download="{plot1_filename}">Download Summary Plot</a>',
            unsafe_allow_html=True)

        fig2 = analyser.plot_frequency_of_matches()
        st.pyplot(fig2, width=400, height=400)
        encoded_fig2 = figure_to_base64(fig2)
        plot2_filename = f"{filename_input}_histogram.png" if filename_input else "histogram.png"
        st.markdown(
            f'<a href="data:image/png;base64,{encoded_fig2}" download="{plot2_filename}">Download Histogram Plot</a>',
            unsafe_allow_html=True)

        fig3 = analyser.plot_heatmap()
        st.pyplot(fig3, width=400, height=400)
        encoded_fig3 = figure_to_base64(fig3)
        plot3_filename = f"{filename_input}_heatmap.png" if filename_input else "heatmap.png"
        st.markdown(
            f'<a href="data:image/png;base64,{encoded_fig3}" download="{plot3_filename}">Download Heatmap Plot</a>',
            unsafe_allow_html=True)

    # Cleanup temporary files
    os.remove(temp_cocktail.name)
    os.remove(temp_filters.name)

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Analysis", "Intro", "About"])

if menu == "Intro":
    st.sidebar.text("This is the introduction to the Gene Cocktail Analyser.")
elif menu == "About":
    st.sidebar.text("Information about the Gene Cocktail Analyser and its purpose.")
