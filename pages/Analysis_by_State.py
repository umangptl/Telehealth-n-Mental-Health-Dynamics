import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
from google.cloud import bigquery

# Load data from BigQuery
@st.cache_data
# Function to load data from BigQuery
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT Indicator, `Group`, State, Time_Period_End_Date, Value, Code
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data


# Function to create choropleth map
def create_choropleth_map(data, unique_indicators):
    st.title("Choropleth Map")

    filtered_data = data[(data['Group'] == 'By State') & (data['Indicator'] == selected_indicator)]

    # Calculate the mean value for each state and indicator combination
    mean_data = filtered_data.groupby('Code')['Value'].mean().reset_index()

    # Create choropleth map using Plotly graph objects
    fig = go.Figure(go.Choropleth(
                            locations=mean_data['Code'],  
                            z=mean_data['Value'], 
                            locationmode='USA-states',
                            colorscale='Viridis',
                            colorbar_title=f'Value Index',
    ))

    fig.update_layout(
                title_text=f'{selected_indicator}',
                geo_scope='usa',
                width=800,
                height=600 
    )

    st.plotly_chart(fig)

def create_chart(data, unique_indicators):
    st.title(f"**Compare Top 10 vs Bottom 10 States**")

    filtered_data = data[(data['Group'] == 'By State') & (data['Indicator'] == selected_indicator)]

    # Calculate the mean value for each state and indicator combination
    mean_data = filtered_data.groupby('State')['Value'].mean().reset_index()

    # Sort values based on the mean value
    mean_data = mean_data.sort_values(by='Value', ascending=False)

    # Select top and bottom states
    top_bottom_data = pd.concat([mean_data.head(10), mean_data.tail(10)])

    # Create horizontal bar chart using Plotly Express
    fig = px.bar(
            top_bottom_data, 
            x='Value', 
            y='State', 
            orientation='h', 
            color='Value',
            labels={'Value': f'Mean Value', 'State': 'State'},
            title=f'{selected_indicator}',
            color_continuous_scale='GnBu',
            height=600,  # Set the height of the chart
    )

    st.plotly_chart(fig)

def create_animation(data, unique_indicators):
    st.title(f"**States Animation over time**")

    state_group_df = data[data['Indicator'] == 'Needed Counseling or Therapy But Did Not Get It, Last 4 Weeks'].copy()
    Neededf = state_group_df[state_group_df['Group'] == 'By State'].copy()
    Neededf['Time_Period_End_Date'] = Neededf['Time_Period_End_Date'].astype(str)

    # Create choropleth map
    fig = px.choropleth(Neededf,
                    locations="Code",
                    color="Value",
                    animation_frame="Time_Period_End_Date",
                    locationmode='USA-states',
                    title='Needed Counseling or Therapy But Did Not Get It, Last 4 Weeks',
                    labels={'Value': 'Indicator Value', 'Indicator': 'Mental Health Indicator'},
                    color_continuous_scale="Rdbu",
                    range_color=(state_group_df['Value'].min(), state_group_df['Value'].max()))


    fig.update_layout(
        title_text=f'{selected_indicator}',
        geo_scope='usa',
        width=800,
        height=600 
    )

    st.plotly_chart(fig)

# Main Streamlit app
st.title("State Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

# Get unique indicators
unique_indicators = data['Indicator'].unique()
# Dropdown for selecting an indicator
selected_indicator = st.selectbox("Select Indicator", unique_indicators)

create_choropleth_map(data, unique_indicators)

create_chart(data, unique_indicators)

create_animation(data, unique_indicators)
