import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from google.oauth2 import service_account
from google.cloud import bigquery


"""
# Telehealth-n-Mental-Health-Dynamics Analysis
### Team Members
- Umang Patel
- Abhilash Tayade

### Data sets:
- [Mental Health Care in the Last 4 Weeks](https://catalog.data.gov/dataset/mental-health-care-in-the-last-4-weeks)
    - Took Prescription Medication for Mental Health
    - Needed Counseling or Therapy But Did Not Get It
    - Took Prescription Medication for Mental Health And/Or Received Counseling or Therapy
    - Received Counseling or Therapy

- [Telemedicine Use in the Last 4 Weeks](https://catalog.data.gov/dataset/telemedicine-use-in-the-last-4-weeks-5229c)
    - Adults Who Had an Appointment with a Health Professional Over Video or Phone 
    - Households With Children Where Any Child Had an Appointment with a Health Professional Over Video or Phone 


#### Collab EDA - [Collab Link](https://colab.research.google.com/drive/17297HG3a7O9vq_F0o9qIwRAGgdigMj_a?usp=sharing)

"""
# Load data in the main app file
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

def create_treemap(data):
    # Calculate the mean value for each subgroup
    df_mean = data.groupby(['Indicator', 'Group', 'Subgroup', 'State'])['Value'].mean().reset_index()

    st.title("TreeMap  data Overview")

    # Create Treemap
    fig_treemap = px.treemap(df_mean, path=['Indicator', 'Group', 'Subgroup', 'State'], values='Value',
                             color='Value', color_continuous_scale='Viridis')

    # Adjust the size of the Treemap
    fig_treemap.update_layout(height=700, width=800)

    st.plotly_chart(fig_treemap)


# Load data
data = load_data_from_bigquery()

#selected_time_period = st.selectbox("Select Time Period Label", data['Time_Period_Label'].unique())
create_treemap(data)

# Display the data table
st.write("## Data Set")
st.dataframe(data)

# Key Questions
st.header("Key Questions")
st.write("### Question 1: Access Disparities")
st.write("What are the underlying factors contributing to the gap between individuals who needed counseling or therapy but did not receive it and those who took prescription medication for mental health or had telemedicine appointments, considering demographic and socio-economic variables?")
st.write("Answer coming soon ")

st.write("### Question 2: Telemedicine Impact on Health Seeking Behavior")
st.write("How does the availability and utilization of telemedicine impact the decision-making process for individuals who either took prescription medication or received counseling or therapy for mental health in the last 4 weeks, and are there discernible trends over time?")
st.write("Answer coming soon ")

# References
st.header("References")
st.write("- [Data Visualisation Catalogue](https://datavizcatalogue.com/)")
st.write("Collab files shared in class:")
st.write("- [Collab Link 1](https://colab.research.google.com/drive/1y4zQl_SxA1DEbjI5XjBuxmXQrx5xI1vE?usp=sharing)")
st.write("- [Collab Link 2](https://drive.google.com/file/d/1zPfz3zma_EriCKvLMShM7jsg5aR_1Cpn/view?usp=sharing)")

