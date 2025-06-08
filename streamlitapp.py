import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Bloomera.csv", parse_dates=["Date"], dayfirst=True)
    df = df.dropna(subset=["Date"])
    df["Engagements"] = pd.to_numeric(df["Engagements"], errors="coerce").fillna(0)
    df["Sentiment Score"] = pd.to_numeric(df["Sentiment Score"], errors="coerce").fillna(0)
    df.fillna("N/A", inplace=True)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.title("Filter Data 🌸")
platforms = ["All"] + sorted(df["Platform"].unique())
sentiments = ["All"] + sorted(df["Sentiment"].unique())
media_types = ["All"] + sorted(df["Media Type"].unique())
locations = ["All"] + sorted(df["Location"].unique())

platform_filter = st.sidebar.selectbox("Platform", platforms)
sentiment_filter = st.sidebar.selectbox("Sentiment", sentiments)
media_filter = st.sidebar.selectbox("Media Type", media_types)
location_filter = st.sidebar.selectbox("Location", locations)
start_date = st.sidebar.date_input("Start Date", df["Date"].min().date())
end_date = st.sidebar.date_input("End Date", df["Date"].max().date())

# Apply Filters
filtered_df = df.copy()
if platform_filter != "All":
    filtered_df = filtered_df[filtered_df["Platform"] == platform_filter]
if sentiment_filter != "All":
    filtered_df = filtered_df[filtered_df["Sentiment"] == sentiment_filter]
if media_filter != "All":
    filtered_df = filtered_df[filtered_df["Media Type"] == media_filter]
if location_filter != "All":
    filtered_df = filtered_df[filtered_df["Location"] == location_filter]

filtered_df = filtered_df[(filtered_df["Date"].dt.date >= start_date) & (filtered_df["Date"].dt.date <= end_date)]

st.title("📊 Campaign Analysis - Bloomera")
st.markdown("Visualisasi performa kampanye dan insight untuk strategi pemasaran. 🌷")

if filtered_df.empty:
    st.warning("Tidak ada data yang cocok dengan filter.")
else:
    # Sentiment Pie
    fig_sentiment = px.pie(filtered_df, names="Sentiment", title="Sentiment Breakdown")
    st.plotly_chart(fig_sentiment, use_container_width=True)

    # Engagement Over Time
    engagement_by_date = filtered_df.groupby(filtered_df["Date"].dt.date)["Engagements"].sum().reset_index()
    fig_trend = px.line(engagement_by_date, x="Date", y="Engagements", title="Engagement Trend Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Platform Engagements
    platform_engagements = filtered_df.groupby("Platform")["Engagements"].sum().reset_index()
    fig_platform = px.bar(platform_engagements, x="Platform", y="Engagements", title="Platform Engagements")
    st.plotly_chart(fig_platform, use_container_width=True)

    # Media Type Pie
    fig_media = px.pie(filtered_df, names="Media Type", title="Media Type Distribution")
    st.plotly_chart(fig_media, use_container_width=True)

    # Top Locations
    top_locations = filtered_df.groupby("Location")["Engagements"].sum().nlargest(5).reset_index()
    fig_location = px.bar(top_locations, x="Location", y="Engagements", title="Top 5 Locations by Engagement")
    st.plotly_chart(fig_location, use_container_width=True)

    # Summary Insight
    top_platform = platform_engagements.sort_values("Engagements", ascending=False)["Platform"].iloc[0]
    top_media = filtered_df["Media Type"].value_counts().idxmax()
    top_location = top_locations.iloc[0]["Location"]

    st.markdown("### 📌 Campaign Strategy Summary")
    st.info(f"""
    Berdasarkan data saat ini, platform **{top_platform}** memiliki engagement tertinggi. 
    Disarankan untuk meningkatkan frekuensi konten di platform tersebut, terutama dalam format **{top_media}**. 
    Lokasi dengan engagement tertinggi adalah **{top_location}**, sehingga strategi lokal bisa dimaksimalkan.
    """)

    # Export PDF Button
    with st.expander("📄 Export Summary to PDF"):
        if st.button("Export PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=f"Campaign Analysis Summary\n\nPlatform: {top_platform}\nMedia Type: {top_media}\nTop Location: {top_location}")
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            st.download_button("Download PDF", pdf_output.getvalue(), file_name="bloomera_summary.pdf", mime="application/pdf")
