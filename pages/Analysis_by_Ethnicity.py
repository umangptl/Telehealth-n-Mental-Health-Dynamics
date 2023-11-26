import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

@st.cache_data
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT Indicator, `Group`, Subgroup, Time_Period_Label, Time_Period_End_Date, Value, Code
    FROM `4weekdataset.dataset`
    """

    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data


def plot_value_by_time_period(data):
    st.title("Sunburst Chart")
    data = data[data['Group'].isin(['By Race/Hispanic ethnicity'])]
    unique_time_periods = data['Time_Period_End_Date'].unique()
    selected_time_period = st.select_slider("Select 4 Week Time Period End Date", options=unique_time_periods)

    selected_data = data[data['Time_Period_End_Date'] == selected_time_period]
    df = selected_data
    df['Subgroup'] = df['Subgroup'].str.replace(r'Non-Hispanic', '')
    df['Subgroup'] = df['Subgroup'].str.replace(r', o', 'O')
    fig = px.sunburst(df, path=['Subgroup', 'Indicator'], values='Value')
    fig.update_layout(width=800, height=800)
    st.plotly_chart(fig)

def plot_value_by_indicator(df):
    st.title("Donut Chart")

    df = df[df['Group'].isin(['By Race/Hispanic ethnicity'])]
    df['Indicator'] = df['Indicator'].str.replace(r', Last 4 Weeks', '')
    selected_indicator = st.radio("Select Indicator", df['Indicator'].unique())
    filtered_df = df[df['Indicator'] == selected_indicator]
    avg_df = filtered_df.groupby(['Indicator', 'Subgroup'])['Value'].mean().reset_index()

    fig = px.pie(avg_df, values='Value', names='Subgroup', hole=0.5,
                 labels={'Value': 'Average Value'})

    fig.update_layout(title='Donut Plot of Average Values per Subgroup')

    st.plotly_chart(fig)

def plot_value_by_race(data):
    st.title("Stacked Bar Chart")

    df = data[data['Group'].isin(['By Race/Hispanic ethnicity'])]
    unique_indicators = df['Subgroup'].unique()
    selected_time_period = st.selectbox("Select Subgroup", unique_indicators)

    # Filter data based on user-selected indicator
    selected_data = df[df['Subgroup'] == selected_time_period]

    fig = px.bar(selected_data, x='Time_Period_Label', y='Value', color='Indicator',
                 labels={'Value': 'Value', 'Indicator': 'Indicators'},
                 title='Stacked Bar Plot with Indicators and Time Periods')
    fig.update_layout(width=1000, height=550)

    st.plotly_chart(fig)

# Main Streamlit app
st.title("Ethnicity Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

plot_value_by_time_period(data)
plot_value_by_indicator(data)
plot_value_by_race(data)
