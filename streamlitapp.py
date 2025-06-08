import streamlit as st
import pandas as pd

REQUIRED_COLUMNS = ['sentiment']

def validate_csv_columns(df):
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, missing_cols
    return True, []

def main():
    st.set_page_config(page_title="Sentiment Analysis Upload", page_icon="📝")
    st.title("Sentiment Analysis CSV Upload")
    st.markdown(
        """
        Upload CSV file yang berisi kolom **Sentiment**.
        File akan diproses jika kolom tersebut tersedia.
        """
    )

    uploaded_file = st.file_uploader("Upload file CSV di sini", type=["csv"])

    if uploaded_file is not None:
        try:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin1')

            # Normalisasi kolom supaya case dan spasi tidak bermasalah
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace('\xa0', ' ')
            df.columns = df.columns.str.lower()

            st.write("Kolom yang terdeteksi:", df.columns.tolist())

            valid, missing_cols = validate_csv_columns(df)

            if not valid:
                st.error(f"Error: Kolom yang dibutuhkan hilang: {missing_cols}")
            else:
                st.success("File berhasil diupload!")
                st.dataframe(df.head())

                # TODO: proses data di sini sesuai kebutuhanmu

        except Exception as e:
            st.error(f"Error saat memproses file: {e}")

if __name__ == "__main__":
    main()
