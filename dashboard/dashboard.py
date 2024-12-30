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
        "cnt": "sum",        
        "registered": "sum",  
        "casual": "sum"       
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "cnt": "total_cnt",        
        "registered": "registered",  
        "casual": "casual"         
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
    df['mnth'] = pd.to_datetime(df['dteday']).dt.month
    
    peak_season_df = df.groupby('mnth').agg({
        "cnt": "sum"
    }).reset_index()
    
    peak_season_df.rename(columns={
        "cnt": "total_cnt"
    }, inplace=True)
    
    peak_season_df['mnth'] = peak_season_df['mnth'].map({
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    })
    
    return peak_season_df

# perbedaan penyewaan sepeda dengan berdasarkan weathersit (cuaca)
def create_weather_df(df):
    weather_df = df.groupby('weathersit').agg({
        "cnt": "sum"
    }).reset_index()
    weather_df.rename(columns={
        "cnt": "total_cnt"
    }, inplace=True)

    # Change Weathersit manjadi kategorikal
    weather_df["weathersit"] = weather_df["weathersit"].map({
        1: 'Clear', 2:'Mist', 3:'Light Rain', 4:'Heavy Rains'
    })

    return weather_df

# menampilkan data berdasarkan hari dan musim menggunakan grafik 
def create_scatter_df(df):
    scatter_df = df.groupby(['weekday', 'season']).agg({
        "cnt": "sum"
    }).unstack().fillna(0)

    scatter_df.columns = scatter_df.columns.droplevel(0)
    scatter_df.reset_index(inplace=True)
    
    return scatter_df


# Load cleaned data
all_df = pd.read_csv("dashboard/modified_day.csv")

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
peak_season_df = create_peak_season_df(main_df)
weather_df = create_weather_df(main_df)
scatter_df = create_scatter_df(main_df)

# plot number of daily sharing (2011)
st.header('Bike Sharing Collection Dashboard :sparkles:')
st.subheader('Daily Sharing')

col1, col2, col3 = st.columns(3)

with col1:
    total_user = daily_orders_df['total_cnt'].sum()
    st.metric("Total User", value=f"{total_user:,.0f}")  

with col2:
    total_registered = daily_orders_df['registered'].sum()
    st.metric("Total Registered", value=f"{total_registered:,.0f}")  

with col3:
    total_casual = daily_orders_df['casual'].sum()
    st.metric("Total Casual", value=f"{total_casual:,.0f}")  

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
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=peak_season_df, x='mnth', y='total_cnt', ax=ax)
plt.title('Total Orders: Peak Season')
plt.xlabel('mnth')
plt.ylabel('Total Orders')
st.pyplot(fig)

# bar plot weather
st.header('Weather Orders')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=weather_df, x='weathersit', y='total_cnt', ax=ax)
plt.title('Total Orders: Weather')
plt.xlabel('Weather Situation')
plt.ylabel('Total Orders')
st.pyplot(fig)

# manampilkan data berdasarkan hari dan musim menggunakan grafik scatter
st.header('Stacked Bar Chart: Hari dan Musim')
fig, ax = plt.subplots(figsize=(12, 6))
scatter_df.set_index('weekday').plot(kind='bar', stacked=True, ax=ax)
plt.title('Data Berdasarkan Hari dan Musim')
plt.xlabel('Hari')
plt.ylabel('Jumlah')
plt.legend(title='Musim')
st.pyplot(fig)


