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
    SELECT *
    FROM `4weekdataset.dataset`
    """
    
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

def plot_value_by_time_period(data):
    # Filter data for age groups
    df = data[data['Group'].isin(['By Age'])]
    unique_indicators = df['Time_Period_Label'].unique()
    st.title("Nightingale Rose Chart")

    # User selects indicator
    selected_time_period = st.selectbox("Select Time Period", unique_indicators)

    # Filter data based on user-selected time period
    selected_data = df[df['Time_Period_Label'] == selected_time_period]
    df = selected_data.pivot(index='Indicator', columns='Subgroup', values='Value')
    st.write(df)

    fig = go.Figure()

    for subgroup in df.columns:
        fig.add_trace(go.Barpolar(
            r=list(df[subgroup]),
            theta=list(df.index),
            name=subgroup,
            marker_color=f'rgb({hash(subgroup) % 256}, {hash(subgroup + "line") % 256}, {hash(subgroup + "fill") % 256})',
            marker_line_color="black",
            hoverinfo=['all'],
            opacity=0.7
        ))

    fig.update_layout(
        font_size=12,
        legend_font_size=15,
        polar_angularaxis_rotation=90,
        width=700,
        height=700,

        polar=dict(
            bgcolor="rgb(223, 223, 223)",
            angularaxis=
            dict(
                linewidth=3,
                showline=True,
                linecolor='black'
            ),
            radialaxis=
            dict(
                showline=True,
                linewidth=2,
                gridcolor="white",
                gridwidth=2,
            )
        ),
    )
    st.write(fig)

def plot_value_by_indicator(data):
    # Filter data for age groups
    df = data[data['Group'].isin(['By Age'])]
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
                    x=df.columns, y=df.index, color_continuous_scale='Viridis')

    # Display the figure
    st.plotly_chart(fig)

def plot_value_by_age_group(data):
    df = data[data['Group'].isin(['By Age'])]
    unique_indicators = df['Subgroup'].unique()
    st.title("Stream Graph")

    # User selects indicator
    selected_time_period = st.selectbox("Select Subgroup", unique_indicators)

    # Filter data based on user-selected indicator
    selected_data = df[df['Subgroup'] == selected_time_period]
    df = selected_data.pivot(index='Indicator', columns='Time_Period_Label', values='Value')
    df = df.reset_index()
    df.set_index("Indicator", inplace=True)
    st.write(df)

    df_tidy = df.T.reset_index()
    df_tidy.rename(columns={'Time_Period_Label': 'index'}, inplace=True)

    # Create a stream graph using plotly.graph_objects
    fig = go.Figure()

    for index, row in df_tidy.iterrows():
        fig.add_trace(go.Scatter(
            x=df_tidy.columns[1:],
            y=row[1:],
            mode='lines',
            stackgroup='one',
            name=row['index']
        ))
    fig.update_layout(
        width=900,
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    # Display the figure
    st.plotly_chart(fig)

# Main Streamlit app
st.title("Age Analysis")

# Load data from BigQuery
data = load_data_from_bigquery()

plot_value_by_time_period(data)
plot_value_by_indicator(data)
plot_value_by_age_group(data)