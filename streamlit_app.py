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
st.write("""First of all during the analysis, there was a drastic change after the period Jun 23- Jul 5 for all indicators and thats because resources were being redirected to vaccinate people as “ CDC finds that the Pfizer-BioNTech and Moderna mRNA COVID-19 vaccines reduce the risk of infection with the SARS-CoV-2 virus by 91% and protect against severe illness and hospitalization if a breakthrough infection does occur”(CDC Museum Covid-19 Timeline). Which was announced on Jun 7.
         
•	This has mainly brought down the indicators of adults who had an appointment with a health professional over video or phone and households with children where any child had an appointment with a health professional over video or phone by 4-7% value.

•	This affected the other factors such as taking prescription medication for mental health, needing counseling or therapy but did not getting It, taking prescription medication for mental health and/or receiving counseling or therapy, receiving counseling or therapy could see some spike trend upwards. 
 """)
st.write("### Question 1: Access Disparities")
st.write("What are the underlying factors contributing to the gap between individuals who needed counseling or therapy but did not receive it and those who took prescription medication for mental health or had telemedicine appointments, considering demographic and socio-economic variables?")
st.write("""
         1.	Gender Disparities:

•	Females consistently show higher indicators, especially in the category of needing counseling or therapy but not receiving it. This emphasizes the potential gender-related barriers or preferences in seeking mental health support.

2.	Anxiety/Depression and Pet Adoption:
         
•	The observed increase in the need for counselors and therapists aligns with the reported surge in pet adoption during the pandemic. This correlation may indicate a link between mental health challenges and the desire for companionship or support, as evidenced by pet adoption trends. “More than 23 million American households — nearly 1 in 5 nationwide — adopted a pet during the pandemic” (Bogage, J. (2022, January 7))

3.	Disability Status:
         
•	While there's no major change in overall disability status, a drop in video appointments among adults with disabilities suggests potential challenges in accessing telemedicine for this demographic.

4.	Age and Education:
         
•	The highest indicators for taking prescription medication or receiving counseling/therapy are among individuals aged 18-29 and those with some college/bachelor's degrees. This highlights the significance of mental health support for younger adults and those with higher education levels.

5.	Ethnic Disparities:
         
•	Ethnic disparities are evident, with Asians having the lowest values overall. Whites show the highest indicators for taking prescription medication or receiving counseling/therapy. Blacks and Hispanics or Latinos, however, demonstrate a notable need for counseling or therapy that goes unmet.

6.	State-wise Analysis:
         
State-wise variations provide additional insights:
         
-	Oregon has the highest need for counseling or therapy not received.
         
-	The Washington District of Columbia has the highest indicators for video/phone appointments, received counseling or therapy, and took prescription medication or received counseling/therapy.
         
-	West Virginia shows the highest indicators for taking prescription medication or receiving counseling/therapy.
         
-	Hawaii consistently has the lowest indicators across various categories.

""")

st.write("### Question 2 Telemedicine Impact on Health Seeking Behavior:")
st.write("How does the availability and utilization of telemedicine impact the decision-making process for individuals who either took prescription medication or received counseling or therapy for mental health in the last 4 weeks, and are there discernible trends over time?")
st.write("""Based on the new understanding that the indicator M represents the combination of Took Prescription Medication for Mental Health (T) and Received Counseling or Therapy (R), and considering the breakdown by age, education level, and ethnicity, we can refine the analysis as follows:

1. By Age:
         
•    The trend confirms that the 18-29 age group has the highest values for both Took Prescription Medication for Mental Health and Received Counseling or Therapy, and this group contributes significantly to the overall M indicator.
         
•    The reasons behind this age group's higher engagement with mental health services could be explored more. Probable reasons include factors such as increased awareness, accessibility, or changing attitudes towards mental health.

2. By Education Level:
         
•    Confirming the trend that, while individual indicators may not show large differences, the overall trend for taking prescription Medication for Mental Health and/or receiving counseling or Therapy is relatively consistent across education levels.
         
•    The reasons for the similar trends and whether educational background influences the decision to combine medication and therapy needs further data and exploration.

3. By Ethnicity:
         
•    The data trend confirms that whites have the highest values for Took Prescription Medication for Mental Health and/or Received Counseling or Therapy, while Asians have the lowest values.
         
•    Reason could be potential cultural or systemic factors contributing to the observed differences, Futher strategies could be explored to address any disparities in mental health care utilization.""")

# References
st.header("References")
st.write("- [Data Visualisation Catalogue](https://datavizcatalogue.com/)")
st.write("- [Prophet documentation](https://facebook.github.io/prophet/docs/outliers.html")
st.write("- Centers for Disease Control and Prevention. (2023, March 15). CDC Museum Covid-19 Timeline. Centers for Disease Control and Prevention.")
st.write("[https://www.cdc.gov/museum/timeline/covid19.html]( https://www.cdc.gov/museum/timeline/covid19.html)")
st.write("- Bogage, J. (2022, January 7). Americans adopted millions of dogs during the coronavirus pandemic. now. Americans adopted millions of dogs during the pandemic. Now what do we do with them.")
st.write("[https://www.washingtonpost.com/business/2022/01/07/covid-dogs-return-to-work/](https://www.washingtonpost.com/business/2022/01/07/covid-dogs-return-to-work/ )")
st.write("Collab files shared in class:")
st.write("- [Collab Link 1](https://colab.research.google.com/drive/1y4zQl_SxA1DEbjI5XjBuxmXQrx5xI1vE?usp=sharing)")
st.write("- [Collab Link 2](https://drive.google.com/file/d/1zPfz3zma_EriCKvLMShM7jsg5aR_1Cpn/view?usp=sharing)")

