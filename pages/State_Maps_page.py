import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from google.cloud import bigquery

# Function to load data from BigQuery
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT Group, Subgroup, Indicator, Value
    FROM `4weekdataset.TeleMed-Mental`
    WHERE Group = 'By State'
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

# Function to create choropleth map
def create_choropleth_map(data, selected_indicator):
    # Filter data for the selected indicator
    indicator_data = data[data['Indicator'] == selected_indicator]

    # Create choropleth map
    fig = px.choropleth(indicator_data,
                        locations="Subgroup",  # Assuming "Subgroup" corresponds to the state abbreviation
                        color="Value",
                        hover_name="State",
                        locationmode='USA-states',
                        title=f'{selected_indicator}')

    # Update layout if needed
    fig.update_layout(
        title_text=f'{selected_indicator}', 
        geo_scope='usa')

    return fig

# Load data
data = load_data_from_bigquery()

st.title("Choropleth Map")
st.write("Select an indicator to visualize on the map:")

# Get unique indicators
unique_indicators = data['Indicator'].unique()

# Dropdown for selecting an indicator
selected_indicator = st.selectbox("Select Indicator", unique_indicators)

# Create choropleth map
with st.spinner("Generating choropleth map..."):
    fig = create_choropleth_map(data, selected_indicator)
    st.plotly_chart(fig)
