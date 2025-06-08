import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Campaign Analysis Dashboard 🌸",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
# (Streamlit doesn't support complex CSS animations like the drifting flowers easily,
# but we can style the rest of the app for a clean, professional look.)
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #fdfbf6; /* A very light, warm off-white */
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f0f9f3; /* Light green background */
        border-right: 2px solid #d4edda;
    }

    [data-testid="stSidebar"] h2 {
        color: #4A6151; /* Dark green text */
    }

    /* Main content styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: #4A6151;
    }

    /* Style for metric cards */
    .metric-card {
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(210, 231, 218, 0.9);
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.04);
        text-align: center;
    }
    .metric-card .metric-label {
        font-size: 1rem;
        font-weight: 500;
        color: #5D7A68;
    }
    .metric-card .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #4A6151;
    }
</style>
""", unsafe_allow_html=True)


# --- Data Loading and Caching ---
@st.cache_data
def load_data(uploaded_file):
    """
    Load data from an uploaded CSV file, clean it, and return a pandas DataFrame.
    Caches the result to avoid reloading and reprocessing on every interaction.
    """
    if uploaded_file is None:
        return None
    try:
        # To handle different file encodings
        string_data = StringIO(uploaded_file.getvalue().decode('utf-8'))
        df = pd.read_csv(string_data)
        
        # Data Cleaning and Preparation
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0)
        df['Sentiment Score'] = pd.to_numeric(df['Sentiment Score'], errors='coerce').fillna(0)
        
        # Fill missing categorical data
        for col in ['Platform', 'Sentiment', 'Media Type', 'Location']:
            if col in df.columns:
                df[col] = df[col].fillna('N/A')
            else:
                # If a required column is missing, create it with 'N/A'
                df[col] = 'N/A'
        
        # Drop rows with invalid dates as they are essential for time-series analysis
        df.dropna(subset=['Date'], inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Error processing the file: {e}. Please ensure it's a valid CSV file with the expected columns.")
        return None

# --- Plotly Chart Base Layout ---
def get_base_layout():
    """Returns a base layout configuration for Plotly charts for consistent styling."""
    return go.Layout(
        height=400,
        showlegend=True,
        margin=dict(t=60, b=60, l=70, r=50),
        font=dict(family='Inter, sans-serif', color='#5D7A68'),
        paper_bgcolor='rgba(255, 255, 255, 0.7)',
        plot_bgcolor='rgba(240, 249, 243, 0.7)',
        title_font=dict(color='#4A6151', size=18),
        xaxis=dict(
            title_font=dict(color='#5D7A68', size=14),
            tickfont=dict(color='#5D7A68'),
            gridcolor='rgba(209, 227, 216, 0.5)',
            linecolor='rgba(156, 175, 163, 0.7)'
        ),
        yaxis=dict(
            title_font=dict(color='#5D7A68', size=14),
            tickfont=dict(color='#5D7A68'),
            gridcolor='rgba(209, 227, 216, 0.5)',
            linecolor='rgba(156, 175, 163, 0.7)'
        ),
        legend=dict(
            font=dict(color='#5D7A68'),
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(209, 227, 216, 0.7)'
        )
    )

# --- Main App ---
def main():
    # --- Sidebar for Filters and File Upload ---
    with st.sidebar:
        st.header("Campaign Analysis Setup 🌿")
        
        uploaded_file = st.file_uploader("Upload your CSV Data File 📜", type=['csv'])
        
        df_original = load_data(uploaded_file)
        
        df = df_original
        
        if df is not None:
            st.success(f"{len(df)} records loaded successfully!")
            
            st.markdown("---")
            st.header("Filter Your Data 🧪")
            
            # Platform Filter
            platforms = ['All'] + sorted(df['Platform'].unique().tolist())
            selected_platform = st.selectbox("Platform", platforms)
            
            # Sentiment Filter
            sentiments = ['All'] + sorted(df['Sentiment'].unique().tolist())
            selected_sentiment = st.selectbox("Sentiment", sentiments)
            
            # Media Type Filter
            media_types = ['All'] + sorted(df['Media Type'].unique().tolist())
            selected_media_type = st.selectbox("Media Type", media_types)
            
            # Location Filter
            locations = ['All'] + sorted(df['Location'].unique().tolist())
            selected_location = st.selectbox("Location", locations)
            
            # Date Range Filter
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            selected_date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

            # --- Applying Filters ---
            df_filtered = df.copy()
            if selected_platform != 'All':
                df_filtered = df_filtered[df_filtered['Platform'] == selected_platform]
            if selected_sentiment != 'All':
                df_filtered = df_filtered[df_filtered['Sentiment'] == selected_sentiment]
            if selected_media_type != 'All':
                df_filtered = df_filtered[df_filtered['Media Type'] == selected_media_type]
            if selected_location != 'All':
                df_filtered = df_filtered[df_filtered['Location'] == selected_location]
            if len(selected_date_range) == 2:
                start_date, end_date = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
                df_filtered = df_filtered[(df_filtered['Date'] >= start_date) & (df_filtered['Date'] <= end_date)]
        else:
            df_filtered = None

    # --- Main Dashboard Area ---
    st.title("Campaign Analysis Dashboard 🌸")
    st.markdown("Visualizing campaign performance and extracting actionable insights.")

    if df_filtered is None:
        st.info("👋 Welcome! Please upload a CSV file using the sidebar to get started.")
        st.markdown("Your CSV should contain columns like `Date`, `Platform`, `Engagements`, `Sentiment`, `Media Type`, and `Location`.")
        return

    if df_filtered.empty:
        st.warning("🤷‍♀️ No data matches the current filter criteria. Try adjusting your filters!")
        return
        
    # --- Key Metrics (KPIs) ---
    st.markdown("### 📈 Key Performance Indicators")
    total_engagements = int(df_filtered['Engagements'].sum())
    avg_sentiment_score = round(df_filtered['Sentiment Score'].mean(), 2)
    total_posts = len(df_filtered)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Engagements</div><div class="metric-value">{total_engagements:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Average Sentiment Score</div><div class="metric-value">{avg_sentiment_score}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Posts</div><div class="metric-value">{total_posts}</div></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Visualizations ---
    st.header("Campaign Visualizations 📊")

    # Define chart colors
    pie_colors = ['#FADADD', '#FFF2CC', '#D4EDDA', '#E8DAEF', '#D1E8F6']
    bar_color_1 = '#A8D8B9'
    bar_color_2 = '#F8C8DC'
    line_color = '#B0C2F2'
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment Breakdown
        st.subheader("Sentiment Breakdown")
        sentiment_counts = df_filtered['Sentiment'].value_counts()
        fig_sentiment = go.Figure(data=[go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values, hole=0.4, marker=dict(colors=pie_colors))])
        fig_sentiment.update_layout(get_base_layout(), title='Sentiment Breakdown 🌸')
        st.plotly_chart(fig_sentiment, use_container_width=True)
        st.markdown("""
        - **Insight 1:** ✨ The majority of content generates positive sentiment, indicating strong brand appeal.
        - **Insight 2:** 🤔 A small percentage of negative sentiment exists, which could be an opportunity to address specific customer concerns.
        - **Insight 3:** 💡 Neutral sentiment posts might benefit from content adjustments to drive stronger emotional responses.
        """)


        # Platform Engagements
        st.subheader("Platform Engagements")
        platform_engagements = df_filtered.groupby('Platform')['Engagements'].sum().sort_values(ascending=False)
        fig_platform = px.bar(platform_engagements, x=platform_engagements.index, y=platform_engagements.values, labels={'x':'Platform', 'y':'Total Engagements'})
        fig_platform.update_traces(marker_color=bar_color_1)
        fig_platform.update_layout(get_base_layout(), title='Platform Engagements 🚀')
        st.plotly_chart(fig_platform, use_container_width=True)
        top_platform = platform_engagements.index[0] if not platform_engagements.empty else "[Platform]"
        st.markdown(f"""
        - **Insight 1:** 🏆 **{top_platform}** consistently drives the highest engagement, making it a primary channel for content distribution.
        - **Insight 2:** 🛠️ Platforms with lower engagement might require a revised content strategy tailored to their audience demographics.
        - **Insight 3:** 🌐 Diversifying content across multiple platforms helps reach a broader audience, even if engagement varies.
        """)

        # Top 5 Locations by Engagement
        st.subheader("Top 5 Locations")
        location_engagements = df_filtered.groupby('Location')['Engagements'].sum().nlargest(5).sort_values(ascending=False)
        fig_location = px.bar(location_engagements, x=location_engagements.index, y=location_engagements.values, labels={'x':'Location', 'y':'Total Engagements'})
        fig_location.update_traces(marker_color=bar_color_2)
        fig_location.update_layout(get_base_layout(), title='Top 5 Locations 🌍')
        st.plotly_chart(fig_location, use_container_width=True)
        top_locs = location_engagements.index[:2].tolist() if len(location_engagements) >= 2 else ["[Location 1]", "[Location 2]"]
        st.markdown(f"""
        - **Insight 1:** 📍 **{top_locs[0]}** and **{top_locs[1]}** are key geographical hubs for engagement, indicating strong regional interest.
        - **Insight 2:** 🎯 Tailoring content or campaigns to specific top locations could further enhance local relevance and engagement.
        - **Insight 3:** 🌍 Understanding the demographics of top locations can inform future marketing efforts.
        """)

    with col2:
        # Engagement Trend Over Time
        st.subheader("Engagement Trend")
        engagement_by_date = df_filtered.groupby(df_filtered['Date'].dt.date)['Engagements'].sum()
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=engagement_by_date.index, y=engagement_by_date.values, mode='lines+markers', name='Engagements', line=dict(color=line_color, width=2.5), marker=dict(size=8, color='#FADADD')))
        fig_trend.update_layout(get_base_layout(), title='Engagement Trend Over Time 📈', xaxis_title='Date', yaxis_title='Total Engagements')
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("""
        - **Insight 1:** 📈 Engagements show a general upward trend over time, suggesting growing audience interest or effective long-term strategies.
        - **Insight 2:** 🚀 Significant spikes in engagement often correlate with specific campaigns or viral content, highlighting successful initiatives.
        - **Insight 3:** 🧐 Identifying periods of low engagement can help in optimizing content scheduling or exploring new content formats.
        """)


        # Media Type Mix
        st.subheader("Media Type Mix")
        media_type_counts = df_filtered['Media Type'].value_counts()
        fig_media = go.Figure(data=[go.Pie(labels=media_type_counts.index, values=media_type_counts.values, hole=0.4, marker=dict(colors=pie_colors))])
        fig_media.update_layout(get_base_layout(), title='Media Type Mix 🎨')
        st.plotly_chart(fig_media, use_container_width=True)
        most_common_media = media_type_counts.index[0] if not media_type_counts.empty else "[Media Type]"
        st.markdown(f"""
        - **Insight 1:** 🌟 **{most_common_media}** is the most frequently used and likely preferred content format by the audience.
        - **Insight 2:** 🎨 Exploring underutilized media types could uncover new avenues for audience engagement and content innovation.
        - **Insight 3:** 🔄 A balanced mix of media types can cater to diverse audience preferences and keep content fresh.
        """)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Campaign Strategy Summary ---
    st.header("Campaign Strategy Summary 📝")
    top_platform = df_filtered.groupby('Platform')['Engagements'].sum().idxmax() if not df_filtered.empty else "[Top Platform]"
    most_common_media = df_filtered['Media Type'].mode()[0] if not df_filtered.empty else "[Most Common Media Type]"
    top_location = df_filtered.groupby('Location')['Engagements'].sum().idxmax() if not df_filtered.empty else "[Top Location]"
    
    summary_text = (
        f"Based on the current data, the key actions should focus on leveraging **{top_platform}**'s high engagement "
        f"by increasing content frequency and exploring more **{most_common_media}** formats. Additionally, targeted "
        f"campaigns for **{top_location}** could yield significant results. Addressing negative sentiment proactively and "
        "optimizing content for platforms with lower engagement are also crucial steps. More detailed strategies "
        "can be formulated once specific campaign goals are defined."
    )
    st.markdown(summary_text)

    # --- Footer ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5D7A68;'>Made with 💖 using Streamlit</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5D7A68; font-size: 0.8em;'>Adapted by Zulfa Nur Aina Putri</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

