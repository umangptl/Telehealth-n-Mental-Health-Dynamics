import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from google.oauth2 import service_account
from google.cloud import bigquery


"""
# Welcome to Streamlit!
"""
st.title("Choropleth Map")
# Load data in the main app file
@st.cache_data
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
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
