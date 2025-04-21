import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import io

# Load model
model = joblib.load("model_rf_80.pkl")

# Styling for page
st.set_page_config(page_title="Sistem Prediksi Kualitas Udara", layout="wide")
st.markdown("""
    <style>
        .block-container {
            max-width: 850px;
            margin: auto;
            padding: 1.5rem;
            background-color: #f9f9f9;
            border-radius: 10px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
    </style>
""", unsafe_allow_html=True)

# Judul aplikasi
st.markdown("<h1 class='title-style'>Sistem Prediksi Kualitas Udara Jakarta Timur</h1>", unsafe_allow_html=True)
st.markdown("""
Prediksi dilakukan berdasarkan Nilai Indeks Standar Pencemar Udara (ISPU). ISPU adalah nilai yang digunakan untuk menggambarkan kondisi kualitas udara berdasarkan dampaknya terhadap kesehatan manusia dan lingkungan. ISPU sendiri adalah angka yang tidak mempunyai satuan dengan kegunaan untuk menggambarkan keadaan kualitas udara sekitar area tertentu dan  didasarkan pada dampak terhadap kesehatan manusia, nilai estetika, dan makhluk hidup lainnya 
""")

rename_columns = {
    "pm_sepuluh": "PM10",
    "pm_duakomalima": "PM2.5",
    "sulfur_dioksida": "SO2",
    "karbon_monoksida": "CO",
    "ozon": "O3",
    "nitrogen_dioksida": "NO2",
    "max": "Max",
    "prediksi": "Prediksi",
    "selisih": "Selisih",
    "status": "Status"
}

# Inisialisasi session state
if 'prediksi_manual' not in st.session_state:
    st.session_state.prediksi_manual = None

# Fungsi untuk menentukan kategori dan warna berdasarkan nilai ISPU
def get_kategori_ispu(nilai):
    if nilai <= 50:
        return "Baik", "green"
    elif nilai <= 100:
        return "Sedang", "blue"
    elif nilai <= 200:
        return "Tidak Sehat", "orange"
    elif nilai <= 300:
        return "Sangat Tidak Sehat", "red"
    else:
        return "Berbahaya", "black"

def highlight_kategori(val):
    warna = {
        "Baik": "color: green;",
        "Sedang": "color: blue;",
        "Tidak Sehat": "color: orange;",
        "Sangat Tidak Sehat": "color: red;",
        "Berbahaya": "color: black;"
    }
    return warna.get(val, "")

# Pilihan metode input
tab1, tab2 = st.tabs(["Input Manual", "Unggah CSV"])

with tab1:
    st.subheader("Masukkan Nilai Parameter Pencemar Udara")

    pm10 = st.number_input("PM10 (Particulate Matter 10)", min_value=0.0, max_value=500.0, step=1.0, key="pm10")
    pm25 = st.number_input("PM2.5 (Particulate Matter 2.5)", min_value=0.0, max_value=500.0, step=1.0, key="pm25")
    so2 = st.number_input("SO2 (Sulfur Dioksida)", min_value=0.0, max_value=500.0, step=1.0, key="so2")
    co = st.number_input("CO (Karbon Monoksida)", min_value=0.0, max_value=500.0, step=1.0, key="co")
    o3 = st.number_input("O3 (Ozon)", min_value=0.0, max_value=500.0, step=1.0, key="o3")
    no2 = st.number_input("NO2 (Nitrogen Dioksida)", min_value=0.0, max_value=500.0, step=1.0, key="no2")

    input_data = pd.DataFrame([[pm10, pm25, so2, co, o3, no2]],
                              columns=["pm_sepuluh", "pm_duakomalima", "sulfur_dioksida", "karbon_monoksida", "ozon", "nitrogen_dioksida"])

    if st.button("Prediksi Kualitas Udara"):
        prediction = model.predict(input_data)[0]
        st.session_state.prediksi_manual = prediction
        st.success(f"Prediksi Nilai ISPU: {prediction:.2f}")
        kategori, warna = get_kategori_ispu(prediction)
        st.markdown(f"<span style='color:{warna}; font-weight:bold;'>Kategori Kualitas Udara: {kategori}</span>", unsafe_allow_html=True)


    # Tampilkan hasil prediksi jika sudah tersedia
    if st.session_state.prediksi_manual is not None:
        actual_value = st.number_input("Masukkan Nilai Aktual ISPU", min_value=0.0, step=0.1, key="actual_manual")
        st.markdown(f"**Hasil Prediksi:** {st.session_state.prediksi_manual:.2f}")

        if actual_value:
            tolerance = 1.2033  # toleransi sebesar nilai rmse
            selisih = abs(st.session_state.prediksi_manual - actual_value)
            if selisih > tolerance:
                st.warning("Perlu evaluasi, Prediksi dan nilai aktual berbeda cukup jauh.")
            else:
                st.success("Tidak perlu dievaluasi, Prediksi dan nilai aktual tidak berbeda jauh.")

            # Visualisasi bar chart
            fig, ax = plt.subplots()
            values = [st.session_state.prediksi_manual, actual_value]
            bars = ax.bar(['Prediksi', 'Aktual'], values, color=['skyblue', 'lightgreen'])

            # Label nilai
            for bar in bars:
                yval = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    yval - (yval * 0.05),  # posisi sedikit di bawah puncak batang
                    f'{yval:.2f}',
                    ha='center',
                    va='top',
                    fontsize=10,
                    fontweight='bold',
                    color='white'
                )

            ax.set_ylabel('Nilai ISPU')
            ax.set_title('Perbandingan Prediksi dan Aktual')
            st.pyplot(fig)


with tab2:
    st.subheader("Unggah File CSV")
     # Tambahkan petunjuk CSV di sini
    st.markdown("""
    #### 📌 Format CSV yang Diperlukan:
    Silakan unggah file CSV dengan kolom-kolom sebagai berikut:

    - **pm_sepuluh**
    - **pm_duakomalima**
    - **sulfur_dioksida**
    - **karbon_monoksida**
    - **ozon**
    - **nitrogen_dioksida**
    - **max** (opsional)

    Contoh isi file:
    ```
    pm_sepuluh,pm_duakomalima,sulfur_dioksida,karbon_monoksida,ozon,nitrogen_dioksida
    50,30,12,1.5,100,35  
    70,45,20,2.0,80,40
    ```

    **Catatan:** File harus dalam format `.csv` dan berisi angka-angka numerik saja.
    """)
    uploaded_file = st.file_uploader("Pilih file CSV", type="csv")

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)

            # Prediksi
            predictions = model.predict(data[["pm_sepuluh", "pm_duakomalima", "sulfur_dioksida",
                                            "karbon_monoksida", "ozon", "nitrogen_dioksida"]])
            data["prediksi"] = predictions

            # Tambahkan kategori dan warna
            data["Kategori"], data["Warna"] = zip(*data["prediksi"].apply(get_kategori_ispu))


            if "max" in data.columns:
                st.success("Kolom nilai aktual ditemukan. Melakukan evaluasi...")

                data["selisih"] = abs(data["prediksi"] - data["max"])
                data["status"] = data.apply(lambda row: "Tidak perlu evaluasi"
                                            if abs(row["prediksi"] - row["max"]) <= 1.2033 else "Perlu Evaluasi", axis=1)

                # Rename untuk ditampilkan
                display_df = data.rename(columns=rename_columns)
                st.subheader("Hasil Prediksi dan Evaluasi:")
                styled_eval_df = display_df[["PM10", "PM2.5", "SO2", "CO", "O3", "NO2", "Max", "Prediksi", "Kategori", "Selisih", "Status"]].reset_index(drop=True).style.applymap(highlight_kategori, subset=["Kategori"])
                st.dataframe(styled_eval_df)
                 # Mengunduh hasil prediksi
                output_excel = io.BytesIO()
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    display_df.to_excel(writer, index=False, sheet_name='Hasil Prediksi')

                # Kembalikan posisi ke awal agar bisa dibaca saat download
                output_excel.seek(0)

                st.download_button(
                    label="📥 Unduh Hasil Prediksi dalam Format Excel",
                    data=output_excel,
                    file_name="hasil_prediksi_ISPU.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # Grafik prediksi vs aktual
                st.subheader("Visualisasi Prediksi vs Aktual")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(data.index, data["prediksi"], label="Prediksi", color="skyblue")
                ax.plot(data.index, data["max"], label="Aktual", color="lightgreen")
                ax.set_xlabel("Index Data")
                ax.set_ylabel("Nilai ISPU")
                ax.set_title("Perbandingan Prediksi dan Aktual")
                ax.legend()
                st.pyplot(fig)

            else:
                st.success("Menampilkan hasil prediksi (tanpa evaluasi karena kolom 'max' tidak tersedia).")
                display_df = data.rename(columns=rename_columns)
                st.subheader("Hasil Prediksi:")
                styled_df = display_df[["PM10", "PM2.5", "SO2", "CO", "O3", "NO2", "Prediksi", "Kategori"]].reset_index(drop=True).style.applymap(highlight_kategori, subset=["Kategori"])
                st.dataframe(styled_df)
                # Mengunduh hasil prediksi
                output_excel = io.BytesIO()
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    display_df.to_excel(writer, index=False, sheet_name='Hasil Prediksi')

                # Kembalikan posisi ke awal agar bisa dibaca saat download
                output_excel.seek(0)

                st.download_button(
                    label="📥 Unduh Hasil Prediksi dalam Format Excel",
                    data=output_excel,
                    file_name="hasil_prediksi_ISPU.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        except Exception as e:
            st.error(f"Gagal memproses karena: {e}")

# Penjelasan kategori ISPU
with st.expander("Lihat Penjelasan Kategori ISPU"):
    st.markdown("""
    <style>
    .ispu-table td, .ispu-table th {
        border: 1px solid #ddd;
        padding: 8px;
    }
    .ispu-table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 10px;
    }
    .ispu-table tr:nth-child(even){background-color: #f2f2f2;}
    .ispu-table tr:hover {background-color: #ddd;}
    .ispu-table th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #003262;
        color: white;
    }
    </style>

    <table class='ispu-table'>
        <tr>
            <th>Indeks</th>
            <th>Kategori</th>
            <th>Keterangan</th>
        </tr>
        <tr>
            <td>0 - 50</td>
            <td style="color:green;"><b>Baik</b></td>
            <td>Tidak berdampak pada kesehatan manusia dan hewan, serta tidak merusak lingkungan.</td>
        </tr>
        <tr>
            <td>51 - 100</td>
            <td style="color:blue;"><b>Sedang</b></td>
            <td>Tidak berdampak pada kesehatan manusia, tetapi bisa berdampak pada estetika atau tanaman.</td>
        </tr>
        <tr>
            <td>101 - 200</td>
            <td style="color:orange;"><b>Tidak Sehat</b></td>
            <td>Mulai berdampak pada kelompok sensitif dan spesies tertentu.</td>
        </tr>
        <tr>
            <td>201 - 300</td>
            <td style="color:red;"><b>Sangat Tidak Sehat</b></td>
            <td>Berisiko terhadap sebagian kelompok populasi yang terpapar.</td>
        </tr>
        <tr>
            <td>> 300</td>
            <td style="color:black;"><b>Berbahaya</b></td>
            <td>Tingkat yang dianggap berbahaya dan dapat memengaruhi kesehatan semua populasi.</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
