import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='darkgrid')

# Helper functions untuk analisis dataset
def daily_user_stats(df):
    """Statistik pengguna harian berdasarkan kategori."""
    daily_stats = df.groupby(['dteday', 'user_category']).total_users.sum().reset_index()
    return daily_stats

def hourly_user_distribution(df):
    """Distribusi pengguna per jam berdasarkan kategori."""
    hourly_distribution = df.groupby(['hr', 'user_category_hour']).total_users.sum().reset_index()
    return hourly_distribution

# Menghitung rata-rata jumlah pengguna berdasarkan musim
def calculate_season_avg_users(df):
    season_avg_users = df.groupby('season')['total_users'].mean().reset_index()
    season_avg_users.rename(columns={'total_users': 'avg_users'}, inplace=True)
    season_avg_users['season'] = season_avg_users['season'].map({0: 'Spring', 1: 'Summer', 2: 'Fall', 3: 'Winter'})
    return season_avg_users

# Menghitung rata-rata jumlah pengguna berdasarkan kondisi cuaca
def calculate_weather_avg_users(df):
    weather_avg_users = df.groupby('weather_condition')['total_users'].mean().reset_index()
    weather_avg_users.rename(columns={'total_users': 'avg_users'}, inplace=True)
    weather_avg_users['weather_condition'] = weather_avg_users['weather_condition'].map(
        {0: 'Clear', 1: 'Cloudy', 2: 'Rainy', 3: 'Stormy'})
    return weather_avg_users

# Menghitung rata-rata jumlah pengguna berdasarkan jam dan hari dalam seminggu
def calculate_hourly_weekday_avg(df):
    hourly_weekday_avg = df.groupby(['weekday', 'hr'])['total_users'].mean().reset_index()
    hourly_weekday_avg.rename(columns={'total_users': 'avg_users'}, inplace=True)
    
    # Mapping nama hari ke string
    weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    hourly_weekday_avg['weekday'] = hourly_weekday_avg['weekday'].map(weekday_map)
    
    return hourly_weekday_avg

def create_combined_rfm_df(day_data, hour_data):
    # Menghitung RFM untuk day_data
    rfm_day = day_data.groupby(by="user_category", as_index=False).agg({
        "dteday": "max", 
        "total_users": "sum", 
    })
    rfm_day.columns = ["user_category", "last_usage_date_day", "monetary_day"]
    
    # Menghitung recency (jumlah hari sejak penggunaan terakhir) untuk day_data
    rfm_day["last_usage_date_day"] = pd.to_datetime(rfm_day["last_usage_date_day"])
    recent_date_day = day_data["dteday"].max()
    rfm_day["recency_day"] = rfm_day["last_usage_date_day"].apply(lambda x: (recent_date_day - x).days)
    
    # Menghitung frequency berdasarkan kategori pengguna untuk day_data
    rfm_day["frequency_day"] = day_data.groupby("user_category")["total_users"].count().reset_index(drop=True)
    
    # Menghapus kolom last_usage_date_day karena sudah tidak diperlukan lagi
    rfm_day.drop("last_usage_date_day", axis=1, inplace=True)

    # Menghitung RFM untuk hour_data
    rfm_hour = hour_data.groupby(by="user_category_hour", as_index=False).agg({
        "dteday": "max",  # Mengambil tanggal penggunaan terakhir
        "total_users": "sum",  # Total penggunaan sepeda
    })
    rfm_hour.columns = ["user_category_hour", "last_usage_date_hour", "monetary_hour"]
    
    # Menghitung recency (jumlah jam sejak penggunaan terakhir) untuk hour_data
    rfm_hour["last_usage_date_hour"] = pd.to_datetime(rfm_hour["last_usage_date_hour"])
    recent_date_hour = hour_data["dteday"].max()
    rfm_hour["recency_hour"] = rfm_hour["last_usage_date_hour"].apply(lambda x: (recent_date_hour - x).days)
    
    # Menghitung frequency berdasarkan kategori pengguna untuk hour_data
    rfm_hour["frequency_hour"] = hour_data.groupby("user_category_hour")["total_users"].count().reset_index(drop=True)
    
    # Menghapus kolom last_usage_date_hour karena sudah tidak diperlukan lagi
    rfm_hour.drop("last_usage_date_hour", axis=1, inplace=True)
    
    # Gabungkan kedua dataframe berdasarkan kategori pengguna
    combined_rfm_df = pd.merge(rfm_day, rfm_hour, left_on="user_category", right_on="user_category_hour", how="outer")
    
    # Menghitung Recency dan Frequency gabungan
    combined_rfm_df["recency"] = combined_rfm_df[["recency_day", "recency_hour"]].min(axis=1)
    combined_rfm_df["frequency"] = combined_rfm_df[["frequency_day", "frequency_hour"]].sum(axis=1)
    combined_rfm_df["monetary"] = combined_rfm_df[["monetary_day", "monetary_hour"]].sum(axis=1)
    
    # Menghapus kolom yang tidak perlu
    combined_rfm_df.drop(["recency_day", "recency_hour", "frequency_day", "frequency_hour", "monetary_day", "monetary_hour"], axis=1, inplace=True)
    
    return combined_rfm_df

# Load data
day_data = pd.read_csv("dashboard/day_data.csv")
hour_data = pd.read_csv("dashboard/hour_data.csv")

# Konversi kolom waktu
day_data['dteday'] = pd.to_datetime(day_data['dteday'])
hour_data['dteday'] = pd.to_datetime(hour_data['dteday'])

# Sidebar untuk rentang waktu
min_date = day_data['dteday'].min()
max_date = day_data['dteday'].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Konversi start_date dan end_date menjadi datetime64
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter dataset berdasarkan rentang waktu
filtered_day_data = day_data[(day_data['dteday'] >= start_date) & (day_data['dteday'] <= end_date)]
filtered_hour_data = hour_data[(hour_data['dteday'] >= start_date) & (hour_data['dteday'] <= end_date)]

# Judul dashboard
st.header('Dicoding: Proyek Analisis Data  :sparkles:')

# Menampilkan deskripsi analisis
st.write("""
    Pada dashboard ini, Anda dapat melihat hasil analisis data pengguna sepeda
    berdasarkan faktor cuaca, musim, dan waktu. Berikut adalah beberapa visualisasi
    dan informasi yang telah dianalisis.
""")

# Statistik Harian
st.markdown("### Statistik Harian")
daily_stats = daily_user_stats(filtered_day_data)

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=daily_stats, x="dteday", y="total_users", hue="user_category", marker="o", ax=ax)
    ax.set_title("Total Pengguna Harian per Kategori")
    st.pyplot(fig)

with col2:
    total_users = filtered_day_data['total_users'].sum()
    avg_temp = filtered_day_data['temp'].mean()
    st.metric("Total Pengguna", f"{total_users:,}")
    st.metric("Suhu Rata-rata", f"{avg_temp:.2f}°C")

# Distribusi Per Jam
st.markdown("### Distribusi Pengguna Per Jam")
hourly_stats = hourly_user_distribution(filtered_hour_data)

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(data=hourly_stats, x="hr", y="total_users", hue="user_category_hour", ax=ax)
ax.set_title("Distribusi Pengguna Per Jam")
st.pyplot(fig)

# Analisis Pengguna Jam Terakhir
st.markdown("### Analisis Pengguna Jam Terakhir")
fig, ax = plt.subplots(figsize=(16, 8))
sns.histplot(filtered_hour_data['hours_since_last_use'], kde=True, color="blue", ax=ax)
ax.set_title("Distribusi Jam Sejak Penggunaan Terakhir")
st.pyplot(fig)

st.markdown("-------------------------------------------------------------------------")

# Pertanyaan 1
st.markdown("### Pengaruh faktor cuaca, musim, dan waktu terhadap jumlah pengguna sepeda")

# Kalkulasi rata-rata pengguna berdasarkan musim
season_avg_df = calculate_season_avg_users(filtered_day_data)

# Kalkulasi rata-rata pengguna berdasarkan kondisi cuaca
weather_avg_df = calculate_weather_avg_users(filtered_day_data)

# Visualisasi rata-rata pengguna berdasarkan musim
st.markdown("##### Rata-rata Pengguna Berdasarkan Musim")
fig_season, ax_season = plt.subplots(figsize=(8, 6))
sns.barplot(
    data=season_avg_df,
    x="season",
    y="avg_users",
    palette="Blues",
    ax=ax_season
)
ax_season.set_title("Rata-rata Jumlah Pengguna Berdasarkan Musim", fontsize=14)
ax_season.set_xlabel("Musim", fontsize=12)
ax_season.set_ylabel("Rata-rata Pengguna Sepeda", fontsize=12)
st.pyplot(fig_season)

# Visualisasi rata-rata pengguna berdasarkan kondisi cuaca
st.markdown("##### Rata-rata Pengguna Berdasarkan Kondisi Cuaca")
fig_weather, ax_weather = plt.subplots(figsize=(8, 6))
sns.barplot(
    data=weather_avg_df,
    x="weather_condition",
    y="avg_users",
    palette="Oranges",
    ax=ax_weather
)
ax_weather.set_title("Rata-rata Jumlah Pengguna Berdasarkan Kondisi Cuaca", fontsize=14)
ax_weather.set_xlabel("Kondisi Cuaca", fontsize=12)
ax_weather.set_ylabel("Rata-rata Pengguna Sepeda", fontsize=12)
st.pyplot(fig_weather)

st.markdown("-------------------------------------------------------------------------")

# Pertanyaan 2
st.markdown("### Pola aktivitas pengguna sepeda berdasarkan waktu (jam) dan hari")

# DataFrame rata-rata pengguna per jam dan hari
hourly_weekday_avg = calculate_hourly_weekday_avg(filtered_hour_data)

# Visualisasi rata-rata pengguna berdasarkan jam
st.markdown("##### Rata-rata Pengguna Berdasarkan Jam")

# Rata-rata pengguna per jam
hourly_avg_users = hourly_weekday_avg.groupby('hr')['avg_users'].mean().reset_index()

# Membuat Line Plot untuk rata-rata pengguna per jam
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(x=hourly_avg_users['hr'], y=hourly_avg_users['avg_users'], marker='o', color='b')
ax.set_title("Rata-rata Pengguna Berdasarkan Jam", fontsize=14)
ax.set_xlabel('Jam', fontsize=12)
ax.set_ylabel('Rata-rata Pengguna Sepeda', fontsize=12)
ax.grid(True)
st.pyplot(fig)

# Visualisasi rata-rata pengguna berdasarkan hari
st.markdown("##### Rata-rata Pengguna Berdasarkan Hari")

# Rata-rata pengguna per hari
weekday_avg_users = hourly_weekday_avg.groupby('weekday')['avg_users'].mean().reset_index()

# Membuat Bar Plot untuk rata-rata pengguna per hari
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=weekday_avg_users['weekday'], y=weekday_avg_users['avg_users'], palette="Blues_d", ax=ax)
ax.set_title("Rata-rata Pengguna Berdasarkan Hari dalam Seminggu", fontsize=14)
ax.set_xlabel('Hari', fontsize=12)
ax.set_ylabel('Rata-rata Pengguna Sepeda', fontsize=12)
ax.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
st.pyplot(fig)

st.write("""
    - Pengguna sepeda lebih aktif pada musim panas dan cuaca cerah. Strategi seperti promosi khusus musim panas atau kampanye cuaca cerah dapat meningkatkan penggunaan sepeda.
- Aktivitas puncak pada pagi dan sore hari mengindikasikan kebutuhan alokasi sumber daya lebih besar pada jam sibuk, misalnya dengan memastikan sepeda dalam kondisi optimal.
- Tren berdasarkan hari dan jam dapat membantu perencanaan operasional seperti pengelolaan stasiun sepeda selama hari kerja atau waktu sibuk.
""")

st.markdown("-------------------------------------------------------------------------")

rfm_df_combined = create_combined_rfm_df(day_data, hour_data)

# Visualisasi RFM yang digabungkan
st.markdown("### Analisis RFM (Recency, Frequency, Monetary) Berdasarkan Hari dan Jam")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df_combined.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df_combined.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = rfm_df_combined.monetary.sum()
    st.metric("Total Users (Monetary)", value=f"{avg_monetary:,}")

# Visualizations for combined RFM
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9"]

# Plotting Recency
sns.barplot(y="recency", x="user_category", data=rfm_df_combined.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("User Category", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# Plotting Frequency
sns.barplot(y="frequency", x="user_category", data=rfm_df_combined.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("User Category", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

# Plotting Monetary (total usage)
sns.barplot(y="monetary", x="user_category", data=rfm_df_combined.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("User Category", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

# Menambahkan footer
st.write("""
    Dashboard ini dibuat untuk menyajikan hasil analisis data pengguna sepeda
    yang dapat membantu dalam memahami pola penggunaan sepeda berdasarkan faktor cuaca,
    musim, dan waktu.
""")

# Footer
st.caption("© 2024 Dashboard Proyek Analisis Data")
