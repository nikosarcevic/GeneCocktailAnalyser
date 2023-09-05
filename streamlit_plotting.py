import streamlit as st
from gca_streamlit import GeneCocktailAnalyser
import io

def display_and_download_plot(analyser, fig, plot_name):
    st.pyplot(fig)  # Display the plot

    # Save as PNG
    png_buf = get_image_bytes(fig, "png")
    st.download_button(
        label=f"Download {plot_name} (PNG)",
        data=png_buf,
        file_name=f"{analyser.dataset_name}_{plot_name}.png",
        mime="image/png",
    )

    # Save as PDF
    pdf_buf = get_image_bytes(fig, "pdf")
    st.download_button(
        label=f"Download {plot_name} (PDF)",
        data=pdf_buf,
        file_name=f"{analyser.dataset_name}_{plot_name}.pdf",
        mime="application/pdf",
    )

def get_image_bytes(fig, format):
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=300)
    buf.seek(0)
    return buf

# Streamlit UI and data input handling
data = st.file_uploader("Upload your data", type=["csv", "xlsx"])

if data:
    gca = GeneCocktailAnalyser(data)  # Create your GCA object
    plots = gca.plot_visualizations()

    for plot_name, fig in plots.items():
        display_and_download_plot(gca, fig, plot_name)
