import streamlit as st
import pandas as pd
import altair as alt 
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import gemini 



st.set_page_config(layout="wide", page_title="Customer Churn Analysis Dashboard", page_icon="📊")


st.title('Customer Churn Analysis Dashboard')
st.markdown('This 2 tabs dashboard provides insights into customer churn for a telecommunications company. Use the filters on the left to customize the data view. You can also ask questions about the dataset using the chat feature at the bottom of the page!')

st.markdown(' ')

df = pd.read_csv('Telco_customer_churn.csv')

st.sidebar.header('Customer Filters')


contract_filter = st.sidebar.multiselect(
    'Select a Contract Type:',
    options=df['Contract'].unique(),
    default=df['Contract'].unique()
)



internet_service_filter = st.sidebar.multiselect(
    'Select an Internet Service Type:',
    options=df['Internet Service'].unique(),
    default=df['Internet Service'].unique()
)

tenure_filter = st.slider(
    'Select Tenure Months:',
    min_value=int(df['Tenure Months'].min()),
    max_value=int(df['Tenure Months'].max()),
    value=(int(df['Tenure Months'].min()), int(df['Tenure Months'].max()))
)


filtered_df = df[
  (df['Contract'].isin(contract_filter)) &
  (df['Internet Service'].isin(internet_service_filter)) &
  (df['Tenure Months'] >= tenure_filter[0]) & (df['Tenure Months'] <= tenure_filter[1])
]

total_customers = filtered_df.shape[0] 

# Calculating the Churn Rate per each Contract Type
churn_rate_by_contract = filtered_df.groupby('Contract')['Churn Value'].mean().reset_index()

churn_rate_by_contract_chart = alt.Chart(churn_rate_by_contract).mark_bar().encode(
    y=alt.X('Contract:N', title=''),
    x=alt.Y('Churn Value:Q', title='Churn Rate', axis=alt.Axis(format='%')),
    color='Churn Value'
).properties(
    title=''
)


churn_rate_by_internet_service = filtered_df.groupby('Internet Service')['Churn Value'].mean().reset_index()
churn_rate_by_internet_service_chart = alt.Chart(churn_rate_by_internet_service).mark_bar().encode(
    y=alt.X('Internet Service:N', title=''),
    x=alt.Y('Churn Value:Q', title='Churn Rate', axis=alt.Axis(format='%')),
    color='Churn Value'
).properties(
    title=''
)

churn_reasons = filtered_df[filtered_df['Churn Reason'] != 'Don\'t know'].groupby('Churn Reason')['Count'].sum().sort_values(ascending=False).reset_index().head()

tab1, tab2 = st.tabs(["Churn Overview", "Deep Dive"])


with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Total Customers",
            value=filtered_df.shape[0],
          

        )
    with col2:
         churn_rate = filtered_df['Churn Value'].mean()
         st.metric(
         label="Overall Churn Rate",
         value=f"{churn_rate:.1%}" # Format as a percentage
    )
    st.subheader('Churn Rate by Contract Type')
    st.altair_chart(churn_rate_by_contract_chart, use_container_width=True)
    st.subheader('Churn Rate by Internet Service Type')
    st.altair_chart(churn_rate_by_internet_service_chart, use_container_width=True)

  
with tab2:

  st.subheader('Top #5 Churn Reasons ')

  st.write("This chart shows the top 5 reasons customers cited for churning. 'Dissatisfaction' and 'Attitude of service provider' are the most common reasons.")  
  churn_reasons_count = alt.Chart(churn_reasons).mark_bar().encode( 
      y=alt.X('Churn Reason', title='', sort='-x'),
      x=alt.Y('Count', title=''),
      color='Count'
      ).properties(
          title = ''
      )

  
  st.altair_chart(churn_reasons_count, use_container_width=True)
  
  st.subheader("Drill-Down: Monthly Charges for Fiber Optic Customers")
  st.write("This chart shows a surprising insight: customers with Fiber Optic service who churned often had lower monthly charges than those who stayed.")

    # 1. Filter for Fiber Optic customers from the main filtered_df
  fiber_customers = filtered_df[filtered_df['Internet Service'] == 'Fiber optic']

    # 2. Create a figure and axis object
  fig, ax = plt.subplots(figsize=(5, 2))

    # 3. Create the box plot using Seaborn
  sns.boxplot(
        data=fiber_customers,
        x='Churn Label',
        y='Monthly Charges',
        ax=ax
    )
  ax.set_title('Monthly Charges: Churned vs. Non-Churned Fiber Optic Customers')
  ax.set_xlabel('Customer Churned?')
  ax.set_ylabel('Monthly Charges ($)')

    # 4. Display the plot in your Streamlit app
  st.pyplot(fig, use_container_width=True)
  iber_customers = filtered_df[filtered_df['Internet Service'] == 'Fiber optic'].copy()

# 2. Create the price brackets using pd.cut
  bins = [0, 70, 95, 120]
  labels = ['Low-Tier ($0-70)', 'Mid-Tier ($70-95)', 'High-Tier ($95+)']
  fiber_customers['PriceBracket'] = pd.cut(
    fiber_customers['Monthly Charges'],
    bins=bins,
    labels=labels
 )

# 3. Calculate the churn rate for the new brackets
  churn_by_bracket = fiber_customers.groupby('PriceBracket')['Churn Value'].mean().reset_index()

  st.subheader("Churn Rate by Price Bracket for Fiber Optic Customers")
  st.write("This chart reveals that Fiber Optic customers in the Low-Tier price bracket have the highest churn rate, suggesting that lower-cost plans may be associated with higher churn.")
# 4. Create the Altair bar chart
  bracket_chart = alt.Chart(churn_by_bracket).mark_bar().encode(
    y=alt.X('PriceBracket:N', title='Price Bracket', sort='-x'),
    x=alt.Y('Churn Value:Q', title='Churn Rate', axis=alt.Axis(format='%')), 
    color='PriceBracket'
).properties(
    title=''
)
  st.markdown("\n\n\n\n\n")
# 5. Display the chart
  st.altair_chart(bracket_chart, use_container_width=True)
gemini.add_gemini_chatbot(filtered_df)
