import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- Helper functions for insights ---
def get_top_sentiments(df):
    counts = df['sentiment'].value_counts().head(3)
    return [f"{sentiment}: {count}" for sentiment, count in counts.items()]

def get_engagement_trend_insights(df):
    trend = df.groupby('date')['engagements'].sum()
    increase = trend.pct_change().fillna(0)
    top_dates = trend.sort_values(ascending=False).head(3)
    insights = [f"Highest engagement on {date.strftime('%Y-%m-%d')}: {val}" for date, val in top_dates.items()]
    if increase.iloc[-1] > 0:
        insights.append(f"Engagements increased by {increase.iloc[-1]*100:.2f}% recently")
    else:
        insights.append(f"Engagements decreased by {abs(increase.iloc[-1]*100):.2f}% recently")
    return insights[:3]

def get_platform_engagements_insights(df):
    platform_sum = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{platform}: {val} engagements" for platform, val in platform_sum.items()]

def get_media_type_mix_insights(df):
    media_counts = df['media_type'].value_counts().head(3)
    return [f"{media}: {count} entries" for media, count in media_counts.items()]

def get_top_locations_insights(df):
    location_sum = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3)
    return [f"{location}: {val} engagements" for location, val in location_sum.items()]

# --- PDF generation helper ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(34, 85, 34)  # dark green
        self.cell(0, 10, 'Interactive Media Intelligence Dashboard Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(255, 241, 196)  # soft yellow
        self.set_text_color(204, 0, 102)  # pinkish
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(51, 51, 51)  # dark grey
        self.multi_cell(0, 10, body)
        self.ln()

# --- Streamlit UI and logic ---

st.set_page_config(
    page_title="🌷 Interactive Media Intelligence Dashboard 🌷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS styles for a soft cottage floral theme with fallen flowers background
page_bg = """
<style>
    body {
        background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        color: #2f4f4f; /* dark slate gray */
        padding-top: 20px;
    }
    /* Main container with subtle white transparent background */
    .main {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 25px 35px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    /* Headings in soft green */
    h1, h2, h3 {
        color: #4caf50; /* soft green */
        font-weight: 700;
    }
    /* Subheadings in pink */
    h4 {
        color: #e91e63; /* pink */
        font-weight: 600;
    }
    /* Buttons with pastel pink background and green text */
    .stButton > button {
        background-color: #ffccbc; /* soft pink-orange */
        color: #388e3c; /* dark green */
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 700;
        font-size: 17px;
        border: none;
        box-shadow: 0 4px 6px rgba(255, 192, 203, 0.4);
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ffe0b2; /* soft yellow */
        color: #2e7d32;
        cursor: pointer;
    }
    /* Markdown text styling */
    .stMarkdown p {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #37474f; /* dark slate blue */
    }
    /* Plotly chart container adjustments */
    .element-container {
        border-radius: 16px !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        background-color: #ffffff;
        padding: 12px;
        margin-bottom: 25px;
    }
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# Wrap the whole content with main container div
st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown("# 🌷 Interactive Media Intelligence Dashboard 🌷")
st.markdown("Upload your CSV file with columns: Date, Platform, Sentiment, Location, Engagements, Media Type 📁")

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required_cols = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV is missing required columns. Found: {list(df.columns)}")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isnull().any():
        st.warning("Some 'Date' values could not be parsed and were removed.")
        df = df.dropna(subset=['date'])

    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)

    st.markdown("### Cleaned Data Preview")
    st.dataframe(df.head())

    st.markdown("### Sentiment Breakdown 🥧")
    fig_sentiment = px.pie(
        df, names='sentiment', title="Sentiment Breakdown",
        color_discrete_sequence=px.colors.sequential.Pinkyl
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.markdown("**Insights:**")
    for insight in get_top_sentiments(df):
        st.markdown(f"- {insight}")

    st.markdown("### Engagement Trend Over Time 📈")
    df_sorted = df.sort_values('date')
    engagement_trend = df_sorted.groupby('date')['engagements'].sum().reset_index()
    fig_engagement = px.line(
        engagement_trend, x='date', y='engagements', 
        title="Engagement Trend Over Time", 
        line_shape='spline', markers=True,
        color_discrete_sequence=["#81c784"]  # soft green
    )
    st.plotly_chart(fig_engagement, use_container_width=True)

    st.markdown("**Insights:**")
    for insight in get_engagement_trend_insights(df):
        st.markdown(f"- {insight}")

    st.markdown("### Platform Engagements 📊")
    platform_engagement = df.groupby('platform')['engagements'].sum().reset_index().sort_values('engagements', ascending=False)
    fig_platform = px.bar(
        platform_engagement, x='platform', y='engagements', 
        title="Platform Engagements",
        color='platform',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("**Insights:**")
    for insight in get_platform_engagements_insights(df):
        st.markdown(f"- {insight}")

    st.markdown("### Media Type Mix 🥧")
    fig_media = px.pie(
        df, names='media_type', title="Media Type Mix",
        color_discrete_sequence=px.colors.sequential.RdPu
    )
    st.plotly_chart(fig_media, use_container_width=True)

    st.markdown("**Insights:**")
    for insight in get_media_type_mix_insights(df):
        st.markdown(f"- {insight}")

    st.markdown("### Top 5 Locations by Engagements 📍")
    top_locations = df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_location = px.bar(
        top_locations, x='location', y='engagements', 
        title="Top 5 Locations by Engagements",
        color='location',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_location, use_container_width=True)

    st.markdown("**Insights:**")
    for insight in get_top_locations_insights(df):
        st.markdown(f"- {insight}")

    st.markdown("### Strategy Ideas 💡")
    st.markdown(
        """
        - Prioritize platforms and media types with highest engagement to optimize content focus.  
        - Leverage positive sentiment peaks to plan marketing campaigns.  
        - Concentrate geo-targeted efforts on top locations to boost local engagement.  
        - Plan content and promotions around dates with low engagement to balance trends.  
        """
    )

    # PDF report generator
    def create_pdf():
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title("Interactive Media Intelligence Dashboard Report")
        pdf.chapter_body("Summary of data insights and visualizations:")

        pdf.chapter_title("Sentiment Breakdown Insights")
        pdf.chapter_body("\n".join(get_top_sentiments(df)))

        pdf.chapter_title("Engagement Trend Insights")
        pdf.chapter_body("\n".join(get_engagement_trend_insights(df)))

        pdf.chapter_title("Platform Engagement Insights")
        pdf.chapter_body("\n".join(get_platform_engagements_insights(df)))

        pdf.chapter_title("Media Type Insights")
        pdf.chapter_body("\n".join(get_media_type_mix_insights(df)))

        pdf.chapter_title("Top Locations Insights")
        pdf.chapter_body("\n".join(get_top_locations_insights(df)))

        pdf.chapter_title("Strategy Ideas")
        pdf.chapter_body(
            "- Prioritize platforms and media types with highest engagement.\n"
            "- Leverage positive sentiment peaks to plan marketing campaigns.\n"
            "- Concentrate geo-targeted efforts on top locations.\n"
            "- Plan content/promotions around low engagement dates."
        )

        return pdf.output(dest='S').encode('latin1')

    st.markdown("### Download Your Report")
    if st.button("Generate PDF Report"):
        pdf_bytes = create_pdf()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="media_dashboard_report.pdf" style="font-size:16px; color:#388e3c; font-weight:bold;">📥 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown('<br><br><p style="font-size:18px; font-weight:600; color:#a0522d;">Hope it helps! ^^ 🌸🌼</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
