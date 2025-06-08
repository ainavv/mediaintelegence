import streamlit as st
import pandas as pd
import plotly.express as px

# --- Style: Soft Pink Background + Minimalist Container ---
st.set_page_config(page_title="🌸 Cottage Campaign Dashboard", layout="wide")

page_style = """
<style>
body {
    background-color: #fce4ec;  /* soft pink */
    color: #4a148c;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
}

.main-container {
    background-color: white;
    border-radius: 15px;
    padding: 30px;
    margin: 30px auto;
    max-width: 1100px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

h1, h2, h3 {
    color: #880e4f;
    margin-bottom: 20px;
}

h4 {
    margin-top: 25px;
    color: #ad1457;
}

.stButton > button {
    background-color: #ec407a;
    color: white;
    font-weight: 600;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.stButton > button:hover {
    background-color: #d81b60;
}

/* Hide empty Streamlit bubbles */
[data-testid="stVerticalBlock"] > div > div:empty {
    display: none !important;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Container to wrap everything nicely
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.title("🌸 Cottage Campaign Dashboard")
    st.write("Visualize campaign performance and extract actionable insights.")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if not uploaded_file:
        st.info("Please upload a CSV file to start analysis.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"Missing columns in your data: {missing}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
    df.dropna(subset=['date'], inplace=True)

    if df.empty:
        st.warning("No valid data found after processing.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # Filter Sidebar (in container to avoid extra bubbles)
    with st.expander("Filter Data", expanded=True):
        cols1, cols2, cols3, cols4 = st.columns(4)
        platform_filter = cols1.selectbox("Platform", options=["All"] + sorted(df['platform'].dropna().unique()))
        sentiment_filter = cols2.selectbox("Sentiment", options=["All"] + sorted(df['sentiment'].dropna().unique()))
        location_filter = cols3.selectbox("Location", options=["All"] + sorted(df['location'].dropna().unique()))
        media_filter = cols4.selectbox("Media Type", options=["All"] + sorted(df['media_type'].dropna().unique()))

        date_cols1, date_cols2 = st.columns(2)
        start_date = date_cols1.date_input("Start Date", df['date'].min().date())
        end_date = date_cols2.date_input("End Date", df['date'].max().date())

    # Apply Filters
    filtered_df = df.copy()
    if platform_filter != "All":
        filtered_df = filtered_df[filtered_df['platform'] == platform_filter]
    if sentiment_filter != "All":
        filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['location'] == location_filter]
    if media_filter != "All":
        filtered_df = filtered_df[filtered_df['media_type'] == media_filter]

    filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date <= end_date)]

    if filtered_df.empty:
        st.warning("No data matches your filters. Please adjust.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # --- Visualizations & Insights ---
    st.header("Visualizations and Insights")

    # 1. Sentiment Pie Chart + Top 3 Sentiments
    st.subheader("Sentiment Breakdown")
    fig_sentiment = px.pie(filtered_df, names='sentiment', color_discrete_sequence=px.colors.sequential.Pinkyl)
    st.plotly_chart(fig_sentiment, use_container_width=True)

    top_sentiments = filtered_df['sentiment'].value_counts().head(3)
    st.markdown("**Top 3 Sentiments:**")
    for sentiment, count in top_sentiments.items():
        st.write(f"- {sentiment}: {count} mentions")

    # 2. Engagement Trend Line Chart + Insights
    st.subheader("Engagement Over Time")
    engagement_trend = filtered_df.groupby('date')['engagements'].sum().reset_index()
    fig_trend = px.line(engagement_trend, x='date', y='engagements', markers=True,
                        title="Engagement Trend Over Time",
                        color_discrete_sequence=['#ad1457'])
    st.plotly_chart(fig_trend, use_container_width=True)

    top_engagement_days = engagement_trend.sort_values(by='engagements', ascending=False).head(3)
    st.markdown("**Top 3 Days by Engagement:**")
    for idx, row in top_engagement_days.iterrows():
        st.write(f"- {row['date'].date()}: {row['engagements']} engagements")

    # 3. Platform Bar Chart + Top Platforms
    st.subheader("Engagement by Platform")
    platform_engagement = filtered_df.groupby('platform')['engagements'].sum().reset_index()
    fig_platform = px.bar(platform_engagement, x='platform', y='engagements',
                          color='platform', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_platform, use_container_width=True)

    top_platforms = platform_engagement.sort_values(by='engagements', ascending=False).head(3)
    st.markdown("**Top 3 Platforms:**")
    for idx, row in top_platforms.iterrows():
        st.write(f"- {row['platform']}: {row['engagements']} total engagements")

    # 4. Media Type Pie Chart + Top Media Types
    st.subheader("Media Type Distribution")
    fig_media = px.pie(filtered_df, names='media_type', color_discrete_sequence=px.colors.sequential.RdPu)
    st.plotly_chart(fig_media, use_container_width=True)

    top_media = filtered_df['media_type'].value_counts().head(3)
    st.markdown("**Top 3 Media Types:**")
    for media, count in top_media.items():
        st.write(f"- {media}: {count} posts")

    # 5. Location Bar Chart + Top Locations
    st.subheader("Top Locations by Engagement")
    location_engagement = filtered_df.groupby('location')['engagements'].sum().reset_index().sort_values(by='engagements', ascending=False).head(5)
    fig_location = px.bar(location_engagement, x='location', y='engagements',
                          color='location', color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_location, use_container_width=True)

    top_locations = location_engagement.head(3)
    st.markdown("**Top 3 Locations:**")
    for idx, row in top_locations.iterrows():
        st.write(f"- {row['location']}: {row['engagements']} engagements")

    st.markdown('</div>', unsafe_allow_html=True)
