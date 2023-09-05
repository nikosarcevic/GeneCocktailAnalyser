import base64
from datetime import datetime
import io
import pandas as pd
import streamlit as st
import os
import tempfile
import warnings
from gca_streamlit import GeneCocktailAnalyser


# Helper function to create a download link
def create_download_link(content: str, filename: str, link_label: str):
    b64 = base64.b64encode(content.encode()).decode()  # encode to base64
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_label}</a>'

def figure_to_base64(fig, format="png"):
    """Converts a Matplotlib figure to a base64 encoded string in a given format."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# Set the page layout to wide
st.set_page_config(layout="wide")

# Suppress warnings
warnings.filterwarnings("ignore")

# Streamlit app title
st.title("Gene Cocktail Analyser")
st.write("Made by Niko Sarcevic -- nikosarcevic.com")

st.text("First phase of the app: note it works it is just not pretty."
        "Make sure to just drag and drop your cocktail and filter files."
        "Filter files should have a column with mutation codons."
        "You can diplay the results and figs, save them to your machine")

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

        # Generate the report using the display_results method
        report_lines = analyser.display_results()
        output_str = "\n".join(report_lines)

        # Allow user to provide a custom name for the report
        filename_input = st.text_input("Enter name for the report:", "")

        # If the user hasn't provided a name, generate a default one based on the current date and time
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