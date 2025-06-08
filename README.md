# 🌸 Cottage Campaign Dashboard

## Deskripsi Singkat
**Cottage Campaign Dashboard** adalah aplikasi web berbasis Streamlit yang dirancang untuk menganalisis performa kampanye media sosial dengan visualisasi interaktif. Dashboard ini membantu kreator, manajer kampanye, dan analis media untuk memahami tren, persebaran sentimen, serta engagement publik terhadap konten yang dipublikasikan di berbagai platform media sosial.

### 🎯 Tujuan Proyek
Proyek ini dikembangkan sebagai bagian dari praktik profesional dalam Produksi Media, khususnya dalam mengintegrasikan **analisis data dan storytelling visual**. Aplikasi ini bertujuan mendukung proses pengambilan keputusan berbasis data (data-driven decision making) dengan tampilan yang estetik dan ramah pengguna.

---

## ✨ Fitur Utama

- ✅ **Upload CSV Data**: Mudah mengunggah data kampanye Anda (format CSV).
- ✅ **Filter Interaktif**: Filter berdasarkan tanggal, platform, sentimen, lokasi, dan jenis media.
- ✅ **Visualisasi Dinamis**:
  - Grafik tren engagement dari waktu ke waktu.
  - Pie chart sentimen dan media type.
  - Bar chart platform dan lokasi terpopuler.
- ✅ **Top 3 Insights Otomatis**: Di bawah setiap visualisasi, ditampilkan 3 insight utama.
- ✅ **Desain Estetik Bertema Soft Pink**: Antarmuka yang nyaman dilihat dan ramah presentasi.
- ✅ **Tanpa Bubble Kosong**: UI bersih dan fokus hanya pada informasi penting.

---

## 🧰 Tech Stack

Berikut adalah alat dan pustaka yang digunakan dalam pengembangan aplikasi ini:

| Komponen                       | Deskripsi                                                                              |
|-------------------------------|----------------------------------------------------------------------------------------|
| **[Streamlit](https://streamlit.io/)**            | Framework utama untuk membangun aplikasi dashboard berbasis Python.                  |
| **[Plotly](https://plotly.com/python/)**          | Untuk membuat visualisasi data yang interaktif dan responsif.                        |
| **[OpenAI GPT (ChatGPT)](https://platform.openai.com/)** | Untuk menganalisis dan merangkum insight otomatis (opsional).                        |
| **[OpenRouter AI](https://openrouter.ai/)**       | Alternatif API gateway untuk akses AI model lainnya.                                 |
| **[GitHub](https://github.com/)**                 | Version control dan kolaborasi pengembangan kode secara terbuka.                     |
| **[Streamlit Community Cloud](https://streamlit.io/cloud)** | Platform deployment gratis untuk aplikasi berbasis Streamlit.                        |
| **[OpenAI SDK](https://github.com/openai/openai-python)** | SDK untuk mengakses layanan GPT dari aplikasi Python.                                |

---

## 🔗 Demo Aplikasi (Live)

Klik link berikut untuk mencoba aplikasi secara langsung:

👉 [https://nama-streamlit-app.streamlit.app](https://nama-streamlit-app.streamlit.app)  
*(Gantilah link di atas dengan link deploy Anda di Streamlit Cloud)*

---

## 📂 Struktur Folder

```plaintext
├── app.py                  # Main Streamlit app
├── data/                   # Folder untuk data contoh (jika ada)
├── assets/                 # Gambar, ikon, dll.
├── README.md               # Dokumen ini
└── requirements.txt        # Daftar dependensi Python
