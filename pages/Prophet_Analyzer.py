import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from google.oauth2 import service_account
from google.cloud import bigquery


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


def generate_prophet_forecast(data):
    # Filter data for age groups
    df = data[data['Subgroup'].isin(['United States'])]
    st.title("Prophet predictions")
    # User selects indicator
    selected_indicator = st.radio("Select Indicator", df['Indicator'].unique())

    # Filter data based on user-selected indicator
    selected_data = df[df['Indicator'] == selected_indicator]
    df = selected_data.pivot(index='Time_Period_Start_Date',columns='Subgroup', values='Value')
    st.write(df)

    df_Prophet = df.reset_index().rename(columns={'Time_Period_Start_Date': 'ds', 'United States': 'y'})  # Rename columns as required by Prophet
    df_Prophet['ds'] = pd.to_datetime(df_Prophet['ds'])

    # Create and fit the model
    model = Prophet()
    model.fit(df_Prophet)

    # Create a DataFrame with future dates for prediction
    future = model.make_future_dataframe(periods=12, freq='W')  # Adjust the number of periods as needed

    # Make predictions
    forecast = model.predict(future)

    # Plot the forecast
    fig = model.plot(forecast)
    st.plotly_chart(fig)



# Main Streamlit app
st.title("Prophet Analysis of Indicator trend")

# Load data from BigQuery
data = load_data_from_bigquery()

generate_prophet_forecast(data)