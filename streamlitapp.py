import streamlit as st
import pandas as pd

REQUIRED_COLUMNS = ['Sentiment Score']

def validate_csv_columns(df):
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, missing_cols
    return True, []

def main():
    st.title("CSV Upload and Sentiment Score Check")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            # Try reading with utf-8, fallback to latin1 if fails
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin1')

            valid, missing_cols = validate_csv_columns(df)

            if not valid:
                st.error(f"Error: Missing required columns: {missing_cols}")
            else:
                st.success("File uploaded successfully!")
                st.dataframe(df.head())

                # Place your processing logic here

        except Exception as e:
            st.error(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()
