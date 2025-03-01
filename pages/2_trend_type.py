import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# Load your dataset
@st.cache_data
def load_data():
    # Replace with your dataset path
    data = pd.read_csv('Nifty_Features.csv')
    return data

# Train the model
@st.cache_resource
def train_model(data):
    # Define features and target
    features = [
        "open", "high", "low", "close", "volume", "day", "month", "year",
        "day_name", "pattern", "candle_color", "abs_move", "pct_move_day",
        "pct_move_3d", "pct_move_5d", "flag_close_range", "EMA_200", "EMA_50",
        "EMA_100", "flag_above_200EMA", "flag_above_50EMA", "flag_above_100EMA",
        "prev_close", "opening_category", "3m_high", "3m_low", "pts_from_3m_high",
        "pts_from_3m_low", "pct_from_3m_high", "pct_from_3m_low", "flag_all_time_high",
        "flag_prev_at_all_time_high"
    ]
    data['next_day_trend'] = (data['close'].shift(-1) > data['close']).astype(int)

    # Encode categorical variables
    categorical_columns = ["day_name", "pattern", "candle_color", "opening_category"]

    # Option 1: Label Encoding
    label_encoders = {}
    for col in categorical_columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])
        label_encoders[col] = le  # Save the encoder for later use

    st.write("Data loaded successfully.")
    st.write(data.head())
    # Drop the last row (since it won't have a next day value)
    data = data.dropna(subset=['next_day_trend'])

    target = "next_day_trend"  # Replace with your target column name

    X = data[features]
    y = data[target]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    st.write(f"Model Accuracy: {accuracy:.2f}")

    return model

# Main app
def main():
    st.title("Bullish/Bearish Trend Probability Predictor")
    st.write("Upload your dataset and predict the probability of the next day's trend.")

    # Load data
    data = load_data()

    # Train model
    model = train_model(data)

    # Input form for prediction
    st.sidebar.header("Input Features")
    input_features = {}
    for feature in [
        "open", "high", "low", "close", "volume", "day", "month", "year",
        "day_name", "pattern", "candle_color", "abs_move", "pct_move_day",
        "pct_move_3d", "pct_move_5d", "flag_close_range", "EMA_200", "EMA_50",
        "EMA_100", "flag_above_200EMA", "flag_above_50EMA", "flag_above_100EMA",
        "prev_close", "opening_category", "3m_high", "3m_low", "pts_from_3m_high",
        "pts_from_3m_low", "pct_from_3m_high", "pct_from_3m_low", "flag_all_time_high",
        "flag_prev_at_all_time_high"
    ]:
        input_features[feature] = st.sidebar.number_input(f"Enter {feature}", value=0.0)

    # Predict
    if st.sidebar.button("Predict"):
        input_df = pd.DataFrame([input_features])
        prediction = model.predict_proba(input_df)
        st.write(f"Probability of Bullish Trend: {prediction[0][1]:.2f}")
        st.write(f"Probability of Bearish Trend: {prediction[0][0]:.2f}")

if __name__ == "__main__":
    main()