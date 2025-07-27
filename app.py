import streamlit as st
import pandas as pd
import joblib
import mysql.connector
from mysql.connector import Error

#saving prediction to Mysql database
def save_prediction_to_mysql(bhk, sqft, location, price):
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = conn.cursor()
        query = "INSERT INTO predictions (bhk, sqft, location, predicted_price) VALUES (%s, %s, %s, %s)"
        values = (bhk, sqft, location, price)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"MySQL Error: {e}")
        return False

# Loading model and feature columns
model = joblib.load('house_price_model.pkl')
model_columns = joblib.load('model_columns.pkl')

# Extracting unique locations
location_columns = [col.replace('location_', '') for col in model_columns if 'location_' in col]

# Page configuration
st.set_page_config(page_title="🏡 House Price Predictor", page_icon="📈", layout="centered")

# Sidebar
st.sidebar.title("💡 About")
st.sidebar.markdown("""
This interactive web app estimates **house prices** based on:

- 🛏️ Number of Bedrooms (BHK)  
- 📐 Total Area (in sqft)  
- 📍 Property Location

The app uses a **Random Forest Regressor**, trained on real housing data, for accurate and flexible predictions.

---

**Tech Stack:**  
Python · Pandas · Scikit-learn · Streamlit · MySQL""")

# Main UI
st.title("🏠 House Price Prediction")
st.markdown("### Enter the details below to estimate the house price")

# Input sliders and dropdown
col1, col2 = st.columns(2)

with col1:
    bhk = st.slider("🛏️ Number of Bedrooms (BHK)", 1, 5, 3)

with col2:
    sqft = st.slider("📐 Square Footage", min_value=300, max_value=5000, value=1200, step=50)

location = st.selectbox("📍 Location", sorted(location_columns))

# Predict button
if st.button("🔍 Predict Price"):
    # Create input dataframe with zeros
    input_data = pd.DataFrame(columns=model_columns)
    input_data.loc[0] = 0
    input_data.at[0, 'bhk'] = bhk
    input_data.at[0, 'sqft'] = sqft

    # Encode location
    loc_col = f'location_{location}'
    if loc_col in model_columns:
        input_data.at[0, loc_col] = 1

    # Predicting 
    price = model.predict(input_data)[0]

    # Format price 
    formatted_price = f"₹ {round(price):,}"
    st.success("✅ Estimated House Price")
    st.markdown(f"### 💰 **{formatted_price}**")
    saved = save_prediction_to_mysql(bhk, sqft, location, round(price))
    if saved:
      st.success("✅ Prediction saved to database.")


