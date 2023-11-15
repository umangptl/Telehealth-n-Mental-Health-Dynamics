import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import matplotlib.pyplot as plt
from google.oauth2 import service_account
from google.cloud import bigquery

@st.cache_data
# Function to load data from BigQuery
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

def create_choropleth_map(data, selected_indicator):
    # Filter data for the selected indicator and 'Group' is 'by state'
    filtered_data = data[(data['Group'] == 'by state') & (data['Indicator'] == selected_indicator)]

    # Create choropleth map
    fig = px.choropleth(filtered_data,
                        locations="State",  # Assuming "State" is the column representing the geographic location
                        color="Value",
                        hover_name="State",
                        locationmode='USA-states',
                        title=f'{selected_indicator}')

    # Update layout if needed
    fig.update_layout(
        title_text=f'{selected_indicator}', 
        geo_scope='usa')

    return fig

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


us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands": "VI",
}

# invert the dictionary
abbrev_to_us_state = dict(map(reversed, us_state_to_abbrev.items()))

def nametoabb(name):
  return us_state_to_abbrev[name]

state_group_df = data[data['Group'] == 'By State'].copy()
state_group_df["code"] = state_group_df["Subgroup"].apply(nametoabb)
state_group_df.head()

state_group_df = data[data['Indicator'] == 'Received Counseling or Therapy, Last 4 Weeks'].copy()
Receivedf = state_group_df[state_group_df['Group'] == 'By State'].copy()
Receivedf["code"] = Receivedf["Subgroup"].apply(nametoabb)

# Assuming 'Receivedf' is your DataFrame
state_group_df = Receivedf.copy()

# Assuming 'usa' is a GeoDataFrame of the United States
usa = gpd.read_file(gplt.datasets.get_path('usa'))

# Merge your data with the GeoDataFrame
merged_data = usa.set_index('id').join(state_group_df.set_index('code'))

# Plot the choropleth map
fig, ax = plt.subplots(figsize=(10, 8))
gplt.choropleth(
    merged_data,
    hue='Value',
    cmap='viridis',
    legend=True,
    legend_kwargs={'orientation': 'horizontal'},
    ax=ax
)

# Show the plot
st.pyplot(fig)