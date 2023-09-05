import base64
import io
import os
import tempfile
from datetime import datetime
import pandas as pd
from gca_streamlit import GeneCocktailAnalyser


def create_download_link(content: str, filename: str, link_label: str) -> str:
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_label}</a>'


def figure_to_base64(fig, format="png") -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format=format)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def process_files(uploaded_cocktail, uploaded_filters):
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)

        cocktail_df = pd.read_csv(uploaded_cocktail)
        filters_df = pd.read_csv(uploaded_filters)

        temp_cocktail = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_filters = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')

        cocktail_df.to_csv(temp_cocktail.name, index=False)
        filters_df.to_csv(temp_filters.name, index=False)

        analyser = GeneCocktailAnalyser(temp_cocktail.name, temp_filters.name)
        analyser.process_data()

        return analyser, temp_cocktail, temp_filters
