import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Data Total Penyewaan, Berdasarkan Registered Dan Casual Users
def create_daily_orders_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",         # Jumlah total penyewaan
        "registered": "sum",  # Total pengguna terdaftar
        "casual": "sum"       # Total pengguna kasual (opsional)
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt": "total_cnt",        # Total jumlah penyewaan
        "registered": "registered",  # Pengguna terdaftar
        "casual": "casual"         # Pengguna kasual
    }, inplace=True)
    return daily_orders_df

# Perbedaan Jumlah Penyewaan Berdasarkan Hari Kerja Dan Hari Libur
def create_weekday_vs_weekend_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['weekday'] = df['dteday'].dt.day_name()
    df['is_weekend'] = df['weekday'].isin(['Saturday', 'Sunday'])
    weekday_vs_weekend_df = df.groupby('is_weekend').agg({
        "cnt": "sum"
    }).reset_index()
    weekday_vs_weekend_df['is_weekend'] = weekday_vs_weekend_df['is_weekend'].map({
        False: "Weekday",
        True: "Weekend"
    })
    weekday_vs_weekend_df.rename(columns={
        "cnt": "total_cnt"
    }, inplace=True)
    return weekday_vs_weekend_df

# Perhitungan puncak penggunaan sepeda berdasarkan season
def create_peak_season_df(df):
    df['month'] = df['dteday'].dt.month
    peak_season_df = df.groupby('month').agg({
        "cnt": "sum"
    }).reset_index()
    peak_season_df.rename(columns={
        "cnt": "total_cnt"
    }, inplace=True)
    return peak_season_df

# perbedaan penyewaan sepeda dengan berdasarkan weathersit (cuaca)
def create_weather_df(df):
    weather_df = df.groupby('weathersit').agg({
        "cnt": "sum"
    }).reset_index()
    weather_df.rename(columns={
        "cnt": "total_cnt"
    }, inplace=True)
    return weather_df

# menampilkan data berdasarkan hari dan musim menggunakan grafik scatter
def create_scatter_df(df):
    scatter_df = df.groupby(['weekday', 'season']).agg({
        "cnt": "sum"
    }).reset_index()
    return scatter_df


# Load cleaned data
all_df = pd.read_csv("day.csv")
# Mengubah data mnth menjadi kategori example: 1 -> January
all_df['mnth'] = all_df['mnth'].map({1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'})

# Mengubah data weekday menjadi kategori example: 0 -> Sunday
all_df['weekday'] = all_df['weekday'].map({0:'Sunday', 1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday'})

# Mengubah data season menjadi kategori example: 1 -> Spring
all_df['season'] = all_df['season'].map({1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'})

# Mengubah data yr menjadi kategori example: 0 -> 2011
all_df['yr'] = all_df['yr'].map({0:2011, 1:2012})

# Mengubah data holiday menjadi kategori example: 0 -> No
all_df['holiday'] = all_df['holiday'].map({0:'No', 1:'Yes'})

# Mengubah data workingday menjadi kategori example: 0 -> No
all_df['workingday'] = all_df['workingday'].map({0:'No', 1:'Yes'})



datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/DewaTriWijaya/ImageAsset/refs/heads/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
weekday_vs_weekend_df = create_weekday_vs_weekend_df(main_df)

# plot number of daily sharing (2011)
st.header('Bike Sharing Collection Dashboard :sparkles:')
st.subheader('Daily Sharing')

col1, col2, col3 = st.columns(3)

with col1:
    total_user = daily_orders_df['total_cnt'].sum()
    st.metric("Total User", value=f"{total_user:,.0f}")  # Format angka dengan pemisah ribuan

with col2:
    total_registered = daily_orders_df['registered'].sum()
    st.metric("Total Registered", value=f"{total_registered:,.0f}")  # Format angka dengan pemisah ribuan

with col3:
    total_casual = daily_orders_df['casual'].sum()
    st.metric("Total Casual", value=f"{total_casual:,.0f}")  # Format angka dengan pemisah ribuan

# Plot total daily orders
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=daily_orders_df, x='dteday', y='total_cnt', ax=ax)
plt.title('Total Daily Orders')
plt.xlabel('Date')
plt.ylabel('Total Orders')
plt.xticks(rotation=45)
st.pyplot(fig)

# Plot total daily orders by user type
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=daily_orders_df, x='dteday', y='registered', label='Registered', ax=ax)
sns.lineplot(data=daily_orders_df, x='dteday', y='casual', label='Casual', ax=ax)
plt.title('Total Daily Orders by User Type')
plt.xlabel('Date')
plt.ylabel('Total Orders')
plt.xticks(rotation=45)
plt.legend()
st.pyplot(fig)

# bar plot weekday vs weekend
st.header('Weekday vs Weekend Orders')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=weekday_vs_weekend_df, x='is_weekend', y='total_cnt', ax=ax)
plt.title('Total Orders: Weekday vs Weekend')
plt.xlabel('Day Type')
plt.ylabel('Total Orders')
st.pyplot(fig)

# bar plot peak season
st.header('Peak Season Orders')
peak_season_df = create_peak_season_df(main_df)
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=peak_season_df, x='month', y='total_cnt', ax=ax)
plt.title('Total Orders: Peak Season')
plt.xlabel('Month')
plt.ylabel('Total Orders')
st.pyplot(fig)

# bar plot weather
st.header('Weather Orders')
weather_df = create_weather_df(main_df)
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=weather_df, x='weathersit', y='total_cnt', ax=ax)
plt.title('Total Orders: Weather')
plt.xlabel('Weather Situation')
plt.ylabel('Total Orders')
st.pyplot(fig)

# manampilkan data berdasarkan hari dan musim menggunakan grafik scatter
st.header('Scatter Plot')
scatter_df = create_scatter_df(main_df)
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(data=scatter_df, x='weekday', y='cnt', hue='season', ax=ax)
plt.title('Scatter Plot: Day vs Value by Season')
plt.xlabel('weekday')
plt.ylabel('Value')
plt.legend(title='Season')
st.pyplot(fig)


