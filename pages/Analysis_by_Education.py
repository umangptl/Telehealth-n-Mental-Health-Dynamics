import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
from itertools import cycle
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from google.oauth2 import service_account
from google.cloud import bigquery

sns.set(style="darkgrid", palette="pastel")

# Load data from BigQuery
@st.cache_data
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT Indicator, `Group`, Subgroup, Time_Period_Label, Time_Period_Start_Date, Value
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

def plot_sunburst_chart(data):
    st.title("Sunburst Chart: Indicators, Education Levels, and Time Frames")

    # Sample data preparation, replace with your actual data and column names
    df = data[data['Group'].isin(['By Education'])]

    # Create Sunburst Chart using Plotly Express
    fig = px.sunburst(df, 
                      path=['Indicator', 'Subgroup', 'Time_Period_Start_Date'],
                      values='Value',
                      title="Sunburst Chart: Indicators, Education Levels, and Time Frames",
                      color_discrete_sequence=px.colors.qualitative.Light24)
    fig.update_layout(width=800, height=800)

    # Display the chart
    st.plotly_chart(fig)

def plot_proportional_area_chart(data):
    st.title("Proportional Area Chart")

    # Sample data preparation, replace with your actual data and column names
    df = data[data['Group'].isin(['By Education'])]

    # Get unique education levels
    unique_education_levels = df['Subgroup'].unique()

    # User selects education level
    selected_education_level = st.selectbox("Select Education Level", unique_education_levels)

    # Filter data based on user-selected education level
    selected_data = df[df['Subgroup'] == selected_education_level]

    selected_data['Indicator'] = selected_data['Indicator'].apply(lambda x: x[:25])

    pivoted_data_table = selected_data.pivot_table(index='Indicator', columns='Time_Period_Start_Date', values='Value', aggfunc='first')

    # Display the table
    st.write(pivoted_data_table)

    # Create Proportional Area Chart using Plotly Express
    fig = px.scatter(selected_data, 
                     x='Time_Period_Start_Date', 
                     y='Indicator',
                     size='Value',
                     color='Value',
                     color_continuous_scale='matter',
                     labels={'Value': 'Size of Square', 'Time_Period_Start_Date': 'Time Period'},
                     title=f"Proportional Area Chart for {selected_education_level}")

    # Display the chart
    st.plotly_chart(fig)

def plot_value_by_indicator(data):
    # Filter data for age groups
    df = data[data['Group'].isin(['By Education'])]
    unique_indicators = df['Indicator'].unique()
    st.title("Heat Matrix")
    # User selects indicator
    selected_time_period = st.selectbox("Select Indicator", unique_indicators)

    # Filter data based on user-selected indicator
    selected_data = df[df['Indicator'] == selected_time_period]
    df = selected_data.pivot(index='Subgroup', columns='Time_Period_Label', values='Value')
    df = df.reset_index()
    st.write(df)

    df.set_index("Subgroup", inplace=True)

    # Draw heat matrix using Plotly Express
    fig = px.imshow(df.values, labels=dict(x="Time Period", y="Subgroup", color="Value"),
                    x=df.columns, y=df.index, color_continuous_scale='YlGn')

    # Display the figure
    st.plotly_chart(fig)

# Main Streamlit app
st.title("Education Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

plot_sunburst_chart(data)

plot_proportional_area_chart(data)
# Plot Heatmap for Detailed Comparison
plot_value_by_indicator(data)