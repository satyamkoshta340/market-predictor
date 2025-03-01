import streamlit as st
import pandas as pd
import yfinance as yf
import os
import subprocess

st.set_page_config(page_title="Market Probability Analyzer", layout="wide")

st.title("🏠 Welcome to the Market Probability Analyzer App")
st.write("Navigate using the sidebar to explore different feature's probability.")

# File path for the data
FILE_PATH = "NIFTY50_Daily.csv"
NIFTY_TICKER = "^NSEI"
POST_UPDATE_SCRIPT = "Nifty50_Features.py"  # Path to the script to run

# Function to check and update data
def update_nifty_data():
    nifty50 = yf.Ticker(NIFTY_TICKER)

    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH, parse_dates=["date"])
        max_date = df["date"].max()
        st.write(max_date, pd.Timestamp.today().normalize())
        if max_date >= pd.Timestamp.today().normalize():
            return "✅ Data is already up to date."

        # Fetch new data from the next day
        start_date = (max_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        new_data = nifty50.history(start=start_date, end=pd.Timestamp.today().strftime("%Y-%m-%d"))

        if not new_data.empty:
            new_data.reset_index(inplace=True)
            new_data.columns = new_data.columns.str.lower()  # Convert all column names to lowercase

            # Drop "dividends" and "stock splits" columns if they exist
            new_data = new_data.drop(columns=["dividends", "stock splits"], errors="ignore")

            # Ensure date format consistency
            new_data["date"] = pd.to_datetime(new_data["date"]).dt.date

            # Remove duplicates (keep only new records)
            new_data = new_data[~new_data["date"].isin(df["date"])]

            if not new_data.empty and new_data["date"].min() > max_date:
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(FILE_PATH, index=False)

                try:
                    subprocess.run(["python", POST_UPDATE_SCRIPT], check=True)
                    return "✅ Data Updated Successfully! ✅ Post-Update Script Executed!"
                except Exception as e:
                    return f"✅ Data Updated, but ❌ Post-Update Script Error: {str(e)}"
            else:
                return "⚠️ No new unique data available."
            
        else:
            return "⚠️ No new data available."
    else:
        # If file doesn't exist, download full data
        df = nifty50.history(period="5y")
        df.reset_index(inplace=True)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df.to_csv(FILE_PATH, index=False)
        return "🆕 New file created with full data!"
    

# Update button
if st.button("🔄 Update Data"):
    message = update_nifty_data()
    st.success(message)

    # Refresh Data AFTER Update
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        st.write("### 📊 Updated Data Preview")
        st.dataframe(df.tail(5))  # Show last 5 rows

# Initial Load and Display of Existing Data
elif os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    st.write("### Current Data Preview")
    st.dataframe(df.tail(5))  # Show last 5 rows
else:
    st.write("⚠️ No existing data found. Click 'Update Data' to download.")