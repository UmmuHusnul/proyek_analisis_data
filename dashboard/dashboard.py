import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Membaca data yang sudah diolah
# Pastikan Anda sudah mengganti path dataset sesuai dengan file yang Anda miliki
day_data = pd.read_csv("day_data.csv")
hour_data = pd.read_csv("hour_data.csv")

# Judul dashboard
st.header('Dicoding Collection: Proyek Analisis Data  :sparkles:')

# Menampilkan deskripsi analisis
st.write("""
    Pada dashboard ini, Anda dapat melihat hasil analisis data pengguna sepeda
    berdasarkan faktor cuaca, musim, dan waktu. Berikut adalah beberapa visualisasi
    dan informasi yang telah dianalisis.
""")

# Pilih jenis analisis yang ingin ditampilkan
option = st.selectbox(
    "Pilih Jenis Analisis",
    ["Pengaruh Cuaca dan Musim", "Pola Aktivitas Pengguna Sepeda", "Visualisasi Data"]
)

# Pengaruh Cuaca dan Musim
if option == "Pengaruh Cuaca dan Musim":
    st.subheader("Pengaruh Cuaca dan Musim terhadap Jumlah Pengguna Sepeda")

    # Buat visualisasi menggunakan seaborn atau matplotlib
    fig, ax = plt.subplots()
    sns.boxplot(x='season', y='total_users', data=day_data, ax=ax)
    ax.set_title('Pengaruh Musim terhadap Jumlah Pengguna Sepeda')
    st.pyplot(fig)

# Pola Aktivitas Pengguna Sepeda
elif option == "Pola Aktivitas Pengguna Sepeda":
    st.subheader("Pola Aktivitas Pengguna Sepeda Berdasarkan Waktu dan Hari")

    # Buat heatmap untuk aktivitas berdasarkan jam
    activity_hour = day_data.groupby('hour')['total_users_hour'].sum()
    fig, ax = plt.subplots()
    sns.heatmap(activity_hour.values.reshape(-1, 1), annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Aktivitas Pengguna Sepeda per Jam')
    st.pyplot(fig)

# Visualisasi Data
elif option == "Visualisasi Data":
    st.subheader("Distribusi Pengguna Sepeda per Kategori")

    # Kategori pengguna berdasarkan jumlah pengguna sepeda
    bins = [0, 500, 1000, 2000, day_data['total_users_hour'].max()]
    labels = ['Low', 'Medium', 'High', 'Very High']
    day_data['user_category'] = pd.cut(day_data['total_users_hour'], bins=bins, labels=labels)

    # Menampilkan distribusi kategori
    category_distribution = day_data['user_category'].value_counts()
    st.write("Distribusi Kategori Pengguna Sepeda:")
    st.bar_chart(category_distribution)

# Menambahkan footer
st.write("""
    Dashboard ini dibuat untuk menyajikan hasil analisis data pengguna sepeda
    yang dapat membantu dalam memahami pola penggunaan sepeda berdasarkan faktor cuaca,
    musim, dan waktu.
""")
