import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google.oauth2 import service_account
from google.cloud import bigquery

# Load data from BigQuery
@st.cache_data
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT *
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

