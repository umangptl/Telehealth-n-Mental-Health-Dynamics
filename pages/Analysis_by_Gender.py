import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
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

def plot_gender_data(data):
    # Filter data for Male and Female subgroups
    gender_data = data[data['Subgroup'].isin(['Male', 'Female'])]

    # Get unique indicators and create a color palette
    unique_indicators = gender_data['Indicator'].unique()
    color_palette = sns.color_palette('husl', n_colors=len(unique_indicators))

    # Plotting
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.lineplot(x='Time_Period_Start_Date', y='Value', hue='Indicator', style='Subgroup',
                 data=gender_data, palette=color_palette, markers=True, dashes=False)

    ax.set_title('Values Over Time for Male and Female Subgroups by Indicator')
    ax.set_xlabel('Time_Period_Start_Date')
    ax.set_ylabel('Value')
    ax.legend(bbox_to_anchor=(0.5, 1.1), loc='lower center', ncol=len(unique_indicators)//2)
    ax.grid(True)
    
    # Display the plot in Streamlit
    st.pyplot(fig)

# Function to plot mean value by indicator and gender
def plot_value_by_indicator_and_gender(data):
    # Filter data for gender groups
    gender_data = data[data['Group'].isin(['By Sex'])]

    # Get unique genders and indicators
    unique_genders = gender_data['Subgroup'].unique()

    # User selects gender
    selected_gender = st.selectbox("Select Gender", unique_genders)

    # Filter data based on user-selected gender
    selected_data = data[data['Subgroup'] == selected_gender]

    st.write(f"**Value by Indicator for {selected_gender} over Time**")
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
        legend=dict(title='Indicator', yanchor="top", y=1.5, xanchor="left", x=0),
        barmode='group',
        width=20*40,  
        height=10*40,  
    )
    bar_chart.update_xaxes(title_text='Time Period Start Date')
    bar_chart.update_yaxes(showticklabels=False)


    st.plotly_chart(bar_chart, use_container_width=True)

def plot_value_by_indicator(data):
    # Filter data for gender groups
    gender_data = data[data['Group'].isin(['By Sex'])]

    # Get unique indicators and time periods
    unique_indicators = gender_data['Indicator'].unique()

    # User selects indicator
    selected_indicator = st.selectbox("Select Indicator", unique_indicators)

    # Filter data based on user-selected indicator
    selected_data = gender_data[gender_data['Indicator'] == selected_indicator]

    selected_data['Subgroup'] = pd.Categorical(selected_data['Subgroup'], categories=['Female', 'Male'], ordered=True)
    selected_data.sort_values(by=['Time_Period_Start_Date', 'Subgroup'], inplace=True)

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
        #legend=dict(title='Gender', yanchor="bottom", y=0, xanchor="left", x=0),
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

# Additional comparison graph
plot_value_by_indicator_and_gender(data)

plot_value_by_indicator(data)