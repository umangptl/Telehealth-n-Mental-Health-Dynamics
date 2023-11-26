import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data
def load_data_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials)

    # Define your BigQuery SQL query to fetch only necessary columns
    query = f"""
    SELECT Indicator, `Group`, Subgroup, Time_Period_Start_Date, Value
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

def plot_ridge_data(data):
    df = data[data['Group'].isin(['By Presence of Symptoms of Anxiety/Depression', 'By Disability status'])]

    st.title("Ridge Plot")
    fig_overview = px.area(df, x='Time_Period_Start_Date', y='Value', color='Subgroup', line_group='Indicator',
                       labels={'Value': 'Density'})
    fig_overview.update_layout(legend=dict(orientation='h', y=1.35, x=0))
    st.plotly_chart(fig_overview)

def plot_stream_graph(data):
    st.title("Stream Graph")
    df = data[data['Group'].isin(['By Presence of Symptoms of Anxiety/Depression', 'By Disability status'])]

    # Get unique indicators for the selectbox widget
    available_indicators = df['Indicator'].unique()

    # Allow the user to select indicators dynamically
    selected_indicator = st.selectbox("Select Indicator", available_indicators, index=0)

    # Filter data based on the selected indicator
    df_selected = df[df['Indicator'] == selected_indicator]

    # Pivot the DataFrame for display
    df_pivot = df_selected.pivot(index='Subgroup', columns='Time_Period_Start_Date', values='Value')

    st.table(df_pivot)

    custom_colors = px.colors.qualitative.Plotly
    # Generate Stream Graph for Detailed Comparison
    fig_stream = px.area(df_selected, x='Time_Period_Start_Date', y='Value', color='Subgroup',
                        line_group='Indicator', color_discrete_sequence=custom_colors)
    fig_stream.update_layout(legend=dict(orientation='h', y=1.5, x=0))
    st.plotly_chart(fig_stream)

def plot_grouped_bar_chart(data):
    st.title("Grouped Bar Chart ")
    df = data[data['Group'].isin(['By Presence of Symptoms of Anxiety/Depression', 'By Disability status'])]

    # Get unique time periods for the selectbox widget
    available_time_periods = df['Time_Period_Start_Date'].unique()

    # Allow the user to select a time period dynamically
    selected_time_period = st.selectbox("Select Time Period", available_time_periods, index=0)

    # Filter data based on the selected time period
    df_selected = df[df['Time_Period_Start_Date'] == selected_time_period]

    # Truncate x-axis labels
    df_selected['Subgroup'] = df_selected['Subgroup'].apply(lambda x: x[:15])  # Adjust the number of characters as needed

    # Pivot the DataFrame for display
    df_pivot = df_selected.pivot(index='Indicator', columns='Subgroup', values='Value')

    st.table(df_pivot)

    # Generate Grouped Bar Chart for Subgroup Comparison with adjusted labels
    fig_bar_chart = px.bar(df_selected, x='Subgroup', y='Value', color='Indicator',
                           labels={'Value': 'Percentage'},
                           barmode='group',
                           template='presentation')

    # Customize layout to separate the legend and adjust x-axis labels 
    fig_bar_chart.update_layout(legend=dict(orientation='h', y=1.5, x=0),
                                xaxis=dict(tickangle=-45, tickmode='array', tickvals=list(range(len(df_selected['Subgroup']))),
                                           ticktext=df_selected['Subgroup']))

    st.plotly_chart(fig_bar_chart)

# Main Streamlit app
st.write("### Anxiety/Depression and Disability status Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

plot_ridge_data(data)

plot_stream_graph(data)

plot_grouped_bar_chart(data)


