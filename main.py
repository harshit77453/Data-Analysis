import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt 
import plotly.express as px

# Add this after your background CSS or imports
st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #4CAF50;  /* Green background; change to any hex/color */
        color: white;  /* Text color */
        border: none;  /* Remove default border */
        padding: 10px 20px;  /* Padding for better look */
        border-radius: 5px;  /* Rounded corners */
        font-size: 16px;  /* Font size */
    }
    .stButton > button:hover {
        background-color: #45a049;  /* Darker green on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stDownloadButton > button {
        background-color: #2196F3;  /* Blue background; change to any hex/color */
        color: white;  /* Text color */
        border: none;  /* Remove default border */
        padding: 10px 20px;  /* Padding for better look */
        border-radius: 5px;  /* Rounded corners */
        font-size: 16px;  /* Font size */
    }
    .stDownloadButton > button:hover {
        background-color: #1976D2;  /* Darker blue on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Background 
st.markdown(
    """
    <script>
    document.body.style.backgroundColor = '#e0f7fa';
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Set background color */
    .stApp {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Style headers */
    h1, h2, h3 {
        color: #222f3e;
        font-weight: 700;
    }
    /* Table style */
    .css-1d391kg {
        border-radius: 8px;
        box-shadow: 0 5px 10px rgba(0,0,0,0.12);
    }
    /* Style the download button */
    .stDownloadButton > button {
        background-color: #0d6efd;
        color: white;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stDownloadButton > button:hover {
        background-color: #084298;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add sidebar background color style early in your script
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #f8f0ff;  /* Light blue background */
    }
    [data-testid="stSidebar"] div {
        color: #4b0082;  /* Dark blue text */
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Load cleaned data (from previous steps)
df = pd.read_csv('C:/Users/Harshit Chauhan/Desktop/Data_dashboard-Project/Data/train.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'],dayfirst=True, errors='coerce')
df['Month'] = df['Order Date'].dt.to_period('M')
df['Year'] = df['Order Date'].dt.year  # Add year for category chart


# App title
st.title("Sales Data Dashboard")

# In sidebar
dark_mode = st.sidebar.checkbox("Enable Dark Mode")
if dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #2b2b2b; color: white; }
        .stApp { background-color: #8e8e8e; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Interactive Filters (at the top for easy access)
st.sidebar.header("Filters")

date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=df['Order Date'].min().date(),
    max_value=df['Order Date'].max().date(),
    value=(df['Order Date'].min().date(), df['Order Date'].max().date())
)
start_date, end_date = date_range
start_date = st.sidebar.date_input("Start Date", df['Order Date'].min())
end_date = st.sidebar.date_input("End Date", df['Order Date'].max())
selected_categories = st.sidebar.multiselect("Select Categories", df['Category'].unique(), default=df['Category'].unique())
top_n = st.sidebar.slider("Number of Top Products", 5, 20, 10)

# Filter data based on selections
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date)) &
    (df['Category'].isin(selected_categories))
]

if st.sidebar.button("Apply Filters"):
    st.success("Filters applied!")
    st.balloons()
    # st.snow()

# Display filtered data
st.header("Raw Data (Filtered)")
st.dataframe(filtered_df.head(10))

# Download Botton
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name='filtered_sales_data.csv',
    mime='text/csv'
)

# KPIs (updated dynamically)
st.header("Key Metrics")
total_sales = filtered_df['Sales'].sum()
st.metric("Total Sales", f"${total_sales:.2f}")
target_sales = 5000000  # Example target; make it user-inputtable
progress = min(total_sales / target_sales, 1.0)
st.progress(progress)
st.write(f"Sales Progress: {progress*100:.1f}% of target (${target_sales})")

# Monthly Trend Chart (dynamic line plot)
st.header("Monthly Sales Trend")
if not filtered_df.empty:
    monthly_sales = filtered_df.groupby('Month')['Sales'].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly_sales.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Monthly Sales Trend')
    ax.set_xlabel('Month')
    ax.set_ylabel('Sales Amount')
    st.pyplot(fig)
else:
    st.write("No data available for selected filters.")

# Top Products Chart (dynamic horizontal bar, adjustable top N)
st.header("Top Products")
if not filtered_df.empty:
    top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(top_n).reset_index()
    chart = alt.Chart(top_products).mark_bar().encode(
        x='Sales',
        y=alt.Y('Product Name', sort='-x'),
        color='Sales'
    ).properties(title=f'Top {top_n} Products')
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available for selected filters.")

# Sales by Category (dynamic bar chart per year)
st.header("Sales by Category (Per Year)")
if not filtered_df.empty:
    sales_by_cat_year = filtered_df.groupby(['Year', 'Category'])['Sales'].sum().unstack()
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sales_by_cat_year.plot(kind='bar', ax=ax3)
    ax3.set_title('Sales Per Year in Each Category')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Sales Amount')
    st.pyplot(fig3)
else:
    st.write("No data available for selected filters.")

# Pie Chart for Category Percentage (dynamic, with toggle for exploded view)
st.header("Sales Percentage by Category")
show_exploded = st.checkbox("Explode Pie Chart")
if not filtered_df.empty:
    sales_by_cat = filtered_df.groupby('Category')['Sales'].sum()
    fig4, ax4 = plt.subplots(figsize=(8, 8))
    explode = [0.1 if show_exploded else 0] * len(sales_by_cat)  # Explode if checked
    ax4.pie(sales_by_cat, labels=sales_by_cat.index, autopct='%1.1f%%', startangle=90, explode=explode)
    ax4.set_title('Sales Percentage by Category')
    st.pyplot(fig4)
else:
    st.write("No data available for selected filters.")

# Dictionary mapping full state names to abbreviations
state_name_to_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

st.header("Sales by State Overview")
# Assuming filtered_df is your filtered dataframe containing 'State' and 'Sales' columns
if 'State' in filtered_df.columns and not filtered_df.empty:
    # Aggregate sales per state
    sales_by_state = filtered_df.groupby('State')['Sales'].sum().reset_index()
    # Map full state names to abbreviations for the plotly map
    sales_by_state['State_Abbrev'] = sales_by_state['State'].map(state_name_to_abbrev)
    # Filter out states that couldn't be mapped
    sales_by_state = sales_by_state.dropna(subset=['State_Abbrev'])
    if not sales_by_state.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Sales by State Map")
            fig = px.choropleth(
                sales_by_state,
                locations='State_Abbrev',
                locationmode='USA-states',
                color='Sales',
                scope='usa',
                title='Sales by State',
                color_continuous_scale='Blues',
                hover_name='State',
                hover_data={'Sales': ':.2f'}
            )
            fig.update_layout(
                geo=dict(
                    showlakes=True,
                    lakecolor='rgb(255,255,255)',
                ),
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Sales Summary")
            st.write(f"Unique states: {sales_by_state['State_Abbrev'].nunique()}")
            with st.expander("View state-wise sales data table"):
                st.dataframe(sales_by_state[['State', 'Sales']].sort_values(by='Sales', ascending=False))
    else:
        st.write("No valid state data after mapping.")
else:
    st.write("No state data available for map.")


st.markdown("""
    <style>
    /* Make body take full height */
    html, body, #root > div {
        height: 100%;
    }
    /* Container flex ensures footer sticks */
    .app-container {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    /* Content pushes footer down */
    .main {
        flex: 1 0 auto;
    }
    /* Fixed footer style */
    footer {
        position: fixed;
        bottom: 0;
        left: 18rem;  /* width of sidebar; adjust if needed */
        right: 0;
        background-color: #f0f2f6;
        padding: 0.75rem 1rem;
        text-align: center;
        color: #444;
        border-top: 1px solid #e4e4e4;
        font-size: 14px;
        z-index: 9999;
    }
    /* Optional: margin bottom for main container so content isn't hidden under footer */
    .main > div.block-container {
        padding-bottom: 3rem;
    }
    </style>
    <footer>
        © 2024 Harshit Chauhan | Built with Streamlit <a href="https://github.com/harshit77453" target="_blank" rel="noopener noreferrer">View Source</a>
    </footer>
""", unsafe_allow_html=True)
