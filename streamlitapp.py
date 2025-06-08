import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# --- CSS: Cottage Flowery Theme with readability ---
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');

body {
    background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-attachment: fixed;
    font-family: 'Quicksand', sans-serif;
    color: #2f2f2f;
}

.main-container {
    background: rgba(255, 255, 255, 0.92); /* Sedikit transparan untuk efek cottage */
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

h1, h2, h3 {
    color: #4CAF50; /* Soft Green */
    font-weight: 700;
}

h4 {
    color: #FFC0CB; /* Soft Pink */
}

.stButton > button {
    background-color: #FFC0CB; /* Soft Pink */
    color: #4CAF50; /* Soft Green */
    border: none;
    border-radius: 12px;
    padding: 8px 20px;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.3s ease; /* Transisi halus */
}

.stButton > button:hover {
    background-color: #FFFACD; /* Soft Yellow */
    color: #E91E63; /* Slightly darker pink for hover */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.element-container {
    background: #FFFFFF; /* Putih bersih */
    border-radius: 16px;
    box-shadow: 0 6px 12px rgba(0,0,0,0.08); /* Shadow lebih lembut */
    padding: 12px;
    margin-bottom: 25px;
}

/* Custom styles for selectbox, date input, and other widgets */
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFACD; /* Soft Yellow */
    border-radius: 8px;
    border: 1px solid #FFC0CB; /* Soft Pink border */
}
.stDateInput input {
    background-color: #FFFACD; /* Soft Yellow */
    border-radius: 8px;
    border: 1px solid #FFC0CB; /* Soft Pink border */
}
.stFileUploader section {
    background-color: #E0FFE0; /* Lighter Green */
    border-radius: 10px;
    border: 1px dashed #4CAF50;
    padding: 15px;
}
</style>
"""

st.set_page_config(page_title="🌷 Cottage Campaign Dashboard", layout="wide")
st.markdown(page_bg, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("## 🐝 Campaign Analysis Dashboard 🌼")
st.markdown("*Visualisasikan performa kampanye dan dapatkan insight yang bisa ditindaklanjuti!* 🍃")

# --- File upload
uploaded_file = st.file_uploader("📁 Unggah file CSV Anda", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    required = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required):
        st.error(f"Kolom yang diperlukan tidak lengkap: {list(df.columns)}. Pastikan ada 'date', 'platform', 'sentiment', 'location', 'engagements', 'media_type'. ⚠️")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0).astype(int)
    df.dropna(subset=['date'], inplace=True)

    # --- Filters
    st.markdown("### 🎯 Filter Data Anda ✏️")
    platforms = ['Semua'] + sorted(df['platform'].dropna().unique())
    sentiments = ['Semua'] + sorted(df['sentiment'].dropna().unique())
    locations = ['Semua'] + sorted(df['location'].dropna().unique())
    media_types = ['Semua'] + sorted(df['media_type'].dropna().unique())

    col1, col2, col3, col4 = st.columns(4)
    f_platform = col1.selectbox("Platform 📱", platforms)
    f_sentiment = col2.selectbox("Sentimen 😊", sentiments)
    f_location = col3.selectbox("Lokasi 📍", locations)
    f_media = col4.selectbox("Tipe Media 🎞️", media_types)

    col5, col6 = st.columns(2)
    start_date = col5.date_input("Tanggal Mulai 🗓️", df['date'].min().date())
    end_date = col6.date_input("Tanggal Akhir 🗓️", df['date'].max().date())

    filtered = df.copy()
    if f_platform != 'Semua':
        filtered = filtered[filtered['platform'] == f_platform]
    if f_sentiment != 'Semua':
        filtered = filtered[filtered['sentiment'] == f_sentiment]
    if f_location != 'Semua':
        filtered = filtered[filtered['location'] == f_location]
    if f_media != 'Semua':
        filtered = filtered[filtered['media_type'] == f_media]
    filtered = filtered[(filtered['date'].dt.date >= start_date) & (filtered['date'].dt.date <= end_date)]

    # --- Helper insights
    def get_top_sentiments(df):
        if df.empty: return ["Tidak ada data sentimen. 😔"]
        return [f"🔎 **{s}**: {c}" for s, c in df['sentiment'].value_counts().head(3).items()]
    
    def get_trends(df):
        if df.empty: return ["Tidak ada data tren. 📉"]
        trend = df.groupby('date')['engagements'].sum()
        if trend.empty: return ["Tidak ada data tren. 📉"]
        
        # Ensure there's enough data for pct_change
        if len(trend) > 1:
            increase = trend.pct_change().fillna(0)
            recent_trend_icon = '⬆️' if increase.iloc[-1] > 0 else '⬇️' if increase.iloc[-1] < 0 else '↔️'
            recent_trend_text = f"📊 Tren terbaru: {recent_trend_icon} **{abs(increase.iloc[-1]*100):.2f}%**"
        else:
            recent_trend_text = "📊 Data kurang untuk analisis tren. "

        top = trend.sort_values(ascending=False).head(3)
        out = [f"📈 Tertinggi pada **{d.strftime('%Y-%m-%d')}**: **{v}**" for d, v in top.items()]
        out.append(recent_trend_text)
        return out
    
    def get_platforms(df):
        if df.empty: return ["Tidak ada data platform. 📱"]
        return [f"📱 **{p}**: **{v}** engagement" for p, v in df.groupby('platform')['engagements'].sum().sort_values(ascending=False).head(3).items()]
    
    def get_media_mix(df):
        if df.empty: return ["Tidak ada data tipe media. 🎞️"]
        return [f"🎞️ **{m}**: **{v}** entri" for m, v in df['media_type'].value_counts().head(3).items()]
    
    def get_locations(df):
        if df.empty: return ["Tidak ada data lokasi. 📍"]
        return [f"📍 **{l}**: **{v}** engagement" for l, v in df.groupby('location')['engagements'].sum().sort_values(ascending=False).head(3).items()]

    # --- Display charts
    st.markdown("## 📊 Visualisasi & Insight Utama ✨")
    if filtered.empty:
        st.warning("Tidak ada data yang tersedia untuk filter yang dipilih. Coba sesuaikan filter Anda. 🧐")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🧁 Sentimen Kampanye")
            fig1 = px.pie(filtered, names='sentiment', title='', color_discrete_sequence=px.colors.sequential.Plotly3) # Changed color palette
            fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=1)))
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("---")
            st.markdown("#### Insight Sentimen 💬")
            for s in get_top_sentiments(filtered):
                st.markdown(f"- {s}")
        
        with col2:
            st.markdown("#### 🌱 Tren Engagement Harian")
            trend = filtered.groupby('date')['engagements'].sum().reset_index()
            fig2 = px.line(trend, x='date', y='engagements', line_shape='spline', markers=True, color_discrete_sequence=['#4CAF50']) # Soft Green line
            fig2.update_layout(xaxis_title="Tanggal 🗓️", yaxis_title="Jumlah Engagement 👍")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("---")
            st.markdown("#### Insight Tren 📈")
            for t in get_trends(filtered):
                st.markdown(f"- {t}")

        st.markdown("---")
        st.markdown("### 🗂️ Analisis Platform & Tipe Media 🚀")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### 🌟 Engagement per Platform")
            platform_eng = filtered.groupby('platform')['engagements'].sum().reset_index()
            fig3 = px.bar(platform_eng, x='platform', y='engagements', color='platform', color_discrete_sequence=px.colors.qualitative.Pastel) # Pastel colors
            fig3.update_layout(xaxis_title="Platform 🌐", yaxis_title="Total Engagement 👍")
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("---")
            st.markdown("#### Platform Teratas 🏆")
            for p in get_platforms(filtered):
                st.markdown(f"- {p}")
        with col4:
            st.markdown("#### 📸 Distribusi Tipe Media")
            fig4 = px.pie(filtered, names='media_type', title='', color_discrete_sequence=px.colors.sequential.RdPu) # Red-Purple sequence
            fig4.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=1)))
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown("---")
            st.markdown("#### Campuran Media 🖼️")
            for m in get_media_mix(filtered):
                st.markdown(f"- {m}")

        st.markdown("---")
        st.markdown("### 🗺️ Lokasi dengan Engagement Teratas")
        loc = filtered.groupby('location')['engagements'].sum().sort_values(ascending=False).head(5).reset_index()
        fig5 = px.bar(loc, x='location', y='engagements', color='location', color_discrete_sequence=px.colors.qualitative.D3) # D3 colors
        fig5.update_layout(xaxis_title="Lokasi 🌎", yaxis_title="Total Engagement 👍")
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("---")
        st.markdown("#### Insight Lokasi 🏡")
        for l in get_locations(filtered):
            st.markdown(f"- {l}")

        # --- PDF Generator
        class PDFReport(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.set_text_color(76, 175, 80) # Soft Green
                self.cell(0, 10, 'Laporan Insight Kampanye 🌼', 0, 1, 'C')
                self.ln(5)
            def chapter_title(self, title):
                self.set_font('Arial', 'B', 12)
                self.set_text_color(255, 192, 203) # Soft Pink
                self.cell(0, 10, title, 0, 1)
                self.set_text_color(0, 0, 0) # Back to black for body
            def chapter_body(self, body):
                self.set_font('Arial', '', 11)
                self.multi_cell(0, 7, body)
                self.ln(3)
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, f'Halaman {self.page_no()}/{{nb}}', 0, 0, 'C')

        def create_pdf():
            pdf = PDFReport()
            pdf.alias_nb_pages()
            pdf.add_page()
            
            pdf.chapter_title("Ringkasan Sentimen Kampanye 💬")
            pdf.chapter_body("\n".join(get_top_sentiments(filtered)))
            
            pdf.chapter_title("Tren Engagement Kampanye 📈")
            pdf.chapter_body("\n".join(get_trends(filtered)))
            
            pdf.chapter_title("Platform Teratas Berdasarkan Engagement 📱")
            pdf.chapter_body("\n".join(get_platforms(filtered)))
            
            pdf.chapter_title("Ringkasan Tipe Media 🎞️")
            pdf.chapter_body("\n".join(get_media_mix(filtered)))
            
            pdf.chapter_title("Lokasi dengan Engagement Teratas 📍")
            pdf.chapter_body("\n".join(get_locations(filtered)))
            
            return pdf.output(dest='S').encode('latin1')

        st.markdown("---")
        st.markdown("### 📤 Ekspor Laporan 📄")
        if st.button("Download Laporan PDF 📥"):
            b64 = base64.b64encode(create_pdf()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="laporan_kampanye_cottage.pdf">Klik untuk Mengunduh Laporan PDF Anda! ⬇️</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("Laporan PDF Anda siap diunduh! 🎉")

st.markdown("<hr><p style='text-align:center'>🌷 Semoga ini membantu! Dibuat dengan ❤️ oleh Zulfa 🐣</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
