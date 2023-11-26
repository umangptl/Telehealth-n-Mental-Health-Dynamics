import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
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
    SELECT Indicator, `Group`, Subgroup, Time_Period_Start_Date, Value, Phase
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

def plot_gender_data(data):
    # Filter data for Male and Female subgroups
    gender_data = data[data['Subgroup'].isin(['Male', 'Female'])]

    st.title("Parallel Sets")
    #Create dimensions
    indicator_dim = go.parcats.Dimension(values=gender_data['Indicator'].apply(lambda x: x[:28]), label="Indicator")
    subgroup_dim = go.parcats.Dimension(values=gender_data['Subgroup'], label="Subgroup")
    value_dim = go.parcats.Dimension(values=gender_data['Time_Period_Start_Date'], label="Time Period")

    # Convert 'Subgroup' to colors
    color_mapping = {'Male': '#0047ff', 'Female': '#F603A3'}
    color = gender_data['Subgroup'].map(color_mapping)

    fig = go.Figure(data=[go.Parcats(
        dimensions=[subgroup_dim, indicator_dim, value_dim],
        line={'color': color},
        hoveron='color', hoverinfo='count+probability',
        labelfont={'size': 18, 'family': 'Times'},
        tickfont={'size': 16, 'family': 'Times'},
        arrangement='freeform',
    )])
    fig.update_layout(title_text='Male and Female overview over Indicators and Time Period')


    # Display the Parcats plot
    st.plotly_chart(fig)

def plot_gender_compare_data(data):
    # Filter data for Male and Female subgroups
    gender_data = data[data['Subgroup'].isin(['Male', 'Female'])]

    st.title("Line Graph")

    # Get unique indicators and create a color palette
    unique_indicators = gender_data['Indicator'].unique()
    selected_indicators = st.multiselect("Select Indicators", unique_indicators, default=unique_indicators)

    # Filter data based on selected indicators
    filtered_data = gender_data[gender_data['Indicator'].isin(selected_indicators)]

    # Create Line Chart using Plotly Express with a specific template
    fig = px.line(filtered_data, x='Time_Period_Start_Date', y='Value', color='Indicator', line_shape='linear',
                  markers=True, line_dash='Subgroup',  # Different line styles for Male and Female
                  labels={'Value': 'Value'},
                  template='plotly_dark')  # Use a built-in dark template, you can choose other templates as well

    # Customize legend position
    fig.update_layout(legend=dict(orientation='h', y=2, x=0), xaxis_title='Time_Period_Start_Date', yaxis_title='Value')

    # Display the plot in Streamlit
    st.plotly_chart(fig)
    

def plot_value_by_indicator_and_gender(data):
    # Filter data for gender groups
    gender_data = data[data['Subgroup'].isin(['Male', 'Female'])]

    st.title("Multi-set Bar Chart Over Indicator")
    # Get unique genders and indicators
    unique_genders = gender_data['Subgroup'].unique()

    # User selects gender
    selected_gender = st.selectbox("Select Gender", unique_genders)

    # Filter data based on user-selected gender
    selected_data = data[data['Subgroup'] == selected_gender]

    st.write(f"**Value by Indicator for {selected_gender} over Time**")

    # Pivot the data for a cleaner display in the table
    pivoted_data_table = selected_data.pivot_table(index='Indicator', columns='Time_Period_Start_Date', values='Value', aggfunc='first')

    # Display the table
    st.write("Data Table:")
    st.write(pivoted_data_table)

    # Create a bar chart for the selected gender with grouped bars for each indicator
    bar_chart = px.bar(
        selected_data,
        x='Time_Period_Start_Date',
        y='Value',
        color='Indicator',
        width=800,
        hover_data=[],
    )
    bar_chart.update_layout(
        legend=dict(title='Time Period Start Date', yanchor="top", y=1.5, xanchor="left", x=0),
        barmode='group',
        width=20*40,  
        height=10*40,  
    )
    bar_chart.update_xaxes(title_text='Indicator')
    bar_chart.update_yaxes(showticklabels=False)

    st.plotly_chart(bar_chart, use_container_width=True)

def plot_value_by_indicator(data):
    # Filter data for gender groups
    gender_data = data[data['Group'].isin(['By Sex'])]
    
    st.title("Multi-set Bar Chart Over Genders")

    # Get unique indicators and time periods
    unique_indicators = gender_data['Indicator'].unique()

    # User selects indicator
    selected_indicator = st.selectbox("Select Indicator", unique_indicators)

    # Filter data based on user-selected indicator
    selected_data = gender_data[gender_data['Indicator'] == selected_indicator]

    selected_data['Subgroup'] = pd.Categorical(selected_data['Subgroup'], categories=['Female', 'Male'], ordered=True)
    selected_data.sort_values(by=['Time_Period_Start_Date', 'Subgroup'], inplace=True)

    # Pivot the data for a cleaner display in the table
    pivoted_data_table = selected_data.pivot_table(index='Subgroup', columns='Time_Period_Start_Date', values='Value', aggfunc='first')

    # Display the table
    st.write("Data Table:")
    st.write(pivoted_data_table)

    # Create a grouped bar chart for the selected indicator with bars for male and female
    grouped_bar_chart = px.bar(
        selected_data,
        x='Time_Period_Start_Date',
        y='Value',
        color='Subgroup',  # Subgroup contains gender information
        title=f'Value by Gender for {selected_indicator} over Time',
        width=800,
        hover_data=[],
        color_discrete_map={'Male': 'blue', 'Female': 'pink'}
    )

    grouped_bar_chart.update_layout(
        # legend=dict(title='Gender', yanchor="bottom", y=0, xanchor="left", x=0),
        barmode='group',  # Group bars for male and female
        width=20*40,
        height=10*40,
        xaxis={'categoryorder': 'array', 'categoryarray': ['Female', 'Male']}
    )
    grouped_bar_chart.update_xaxes(title_text='Time Period Start Date')
    grouped_bar_chart.update_yaxes(showticklabels=False)

    st.plotly_chart(grouped_bar_chart, use_container_width=True)

# Main Streamlit app
st.title("Gender Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

# Assuming 'data_merged' is your DataFrame
plot_gender_data(data)

plot_gender_compare_data(data)

# Additional comparison graph
plot_value_by_indicator_and_gender(data)

plot_value_by_indicator(data)