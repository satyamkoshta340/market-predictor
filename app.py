import streamlit as st
import pandas as pd
import numpy as np

# Set the title
st.title("📊 Streamlit Dashboard Example")

# Sidebar
st.sidebar.header("Settings")
option = st.sidebar.selectbox("Select Chart Type", ["Line Chart", "Bar Chart", "Scatter Plot"])

# Generate sample data
st.subheader("Random Data Overview")
df = pd.DataFrame(
    np.random.randn(50, 3),
    columns=["A", "B", "C"]
)
st.write(df.head())

# Display chart based on selection
st.subheader(f"{option}")

if option == "Line Chart":
    st.line_chart(df)
elif option == "Bar Chart":
    st.bar_chart(df)
else:
    st.scatter_chart(df)

# Add interactive widgets
if st.checkbox("Show raw data"):
    st.write(df)
