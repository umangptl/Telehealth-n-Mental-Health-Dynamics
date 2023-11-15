import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from google.oauth2 import service_account
from google.cloud import bigquery


"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:.
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""
credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
# Create a BigQuery client
client = bigquery.Client(credentials=credentials)

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
# page_names = ["State Maps", "Charts", "Other Page"]
# page = st.sidebar.selectbox("Select a page", page_names)

# # Display content based on the selected page
# if page == "State Maps":
#     display_State_Maps_page()

# elif page == "Charts":
#     display_Charts_page()

# elif page == "Other Page":
#     display_other_page()

# else:
#     st.write(f"Page '{page}' not found. Please select a valid page.")
