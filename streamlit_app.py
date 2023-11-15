import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from google.oauth2 import service_account
from google.cloud import bigquery

from pages.State_Maps import display_State_Maps_page
from pages.Charts import display_Charts_page
from pages.Other_Page import display_other_page


"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:.
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

st.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))
#========================sample end starting load bigquery data =========================
credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
# Create a BigQuery client
client = bigquery.Client(credentials=credentials)
# Load the Bay Area bike share data and cache it using st.cache_data
#========================load data =========================
@st.cache_data
def load_data_from_bigquery():
    # Define your BigQuery SQL query
    query = f"""
    SELECT *
    FROM `4weekdataset.TeleMed-Mental`
    """
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data
# Load data
data = load_data_from_bigquery()

# Display the data table
st.write("## TeleMed-Mental Data")
st.dataframe(data)

# Sidebar navigation
# Sidebar navigation
page_names = ["State Maps", "Charts", "Other Page"]
page = st.sidebar.selectbox("Select a page", page_names)

# Display content based on the selected page
if page == "State Maps":
    display_State_Maps_page()

elif page == "Charts":
    display_Charts_page()

elif page == "Other Page":
    display_other_page()

else:
    st.write(f"Page '{page}' not found. Please select a valid page.")
