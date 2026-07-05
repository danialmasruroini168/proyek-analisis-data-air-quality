import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import glob
import os

sns.set_theme(style='whitegrid')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data', 'PRSA_Data_20130301-20170228')

@st.cache_data
def load_data():
    all_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    dfs = []
    for f in all_files:
        df = pd.read_csv(f)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    weather = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    for col in pollutants + weather:
        df[col] = df.groupby('station')[col].transform(lambda x: x.fillna(x.median()))
    df['wd'] = df.groupby('station')['wd'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else 'NNE'))

    monthly = df.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
    monthly['date'] = pd.to_datetime(monthly[['year', 'month']].assign(day=1))
    station_avg = df.groupby('station')['PM2.5'].mean().sort_values().reset_index()
    station_avg.columns = ['station', 'avg_pm25']
    hourly = df.groupby('hour')['PM2.5'].mean().reset_index()
    return df, monthly, station_avg, hourly

df, monthly, station_avg, hourly = load_data()

st.set_page_config(page_title='Air Quality Dashboard', layout='wide')
st.title('🌫️ Air Quality Dashboard')
st.markdown('Analisis kualitas udara Beijing (PRSA) 2013–2017')

st.sidebar.header('Filter')

stations = sorted(df['station'].unique())
selected_stations = st.sidebar.multiselect('Stasiun', stations, default=stations[:4])

years = sorted(df['year'].unique())
selected_years = st.sidebar.multiselect('Tahun', years, default=years)

filtered = df[df['station'].isin(selected_stations) & df['year'].isin(selected_years)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_pm25 = filtered['PM2.5'].mean()
    st.metric('Rata-rata PM2.5', f'{avg_pm25:.1f} µg/m³')
with col2:
    avg_pm10 = filtered['PM10'].mean()
    st.metric('Rata-rata PM10', f'{avg_pm10:.1f} µg/m³')
with col3:
    max_pm25 = filtered['PM2.5'].max()
    st.metric('Max PM2.5', f'{max_pm25:.0f} µg/m³')
with col4:
    good_pct = (filtered['PM2.5'] <= 35).mean() * 100
    st.metric('Kualitas Baik', f'{good_pct:.1f}%')

st.subheader('Rata-rata PM2.5 Bulanan')
fig, ax = plt.subplots(figsize=(14, 5))
monthly_filtered = filtered.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
monthly_filtered['date'] = pd.to_datetime(monthly_filtered[['year', 'month']].assign(day=1))
ax.plot(monthly_filtered['date'], monthly_filtered['PM2.5'], marker='o', color='#C73E1D', linewidth=1.5)
ax.axhline(35, color='#2E86AB', linestyle='--', label='WHO guideline (35)')
ax.set_xlabel('Tahun')
ax.set_ylabel('PM2.5 (µg/m³)')
ax.legend()
st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    st.subheader('PM2.5 per Stasiun')
    station_filt = filtered.groupby('station')['PM2.5'].mean().sort_values().reset_index()
    station_filt.columns = ['station', 'avg_pm25']
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#6A994E'] * 3 + ['#F18F01'] * (len(station_filt) - 6) + ['#C73E1D'] * 3
    colors = colors[:len(station_filt)]
    sns.barplot(x='avg_pm25', y='station', data=station_filt, palette=colors, ax=ax)
    ax.set_xlabel('PM2.5 (µg/m³)')
    st.pyplot(fig)

with col2:
    st.subheader('Pola Jam-jaman PM2.5')
    hourly_filt = filtered.groupby('hour')['PM2.5'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly_filt['hour'], hourly_filt['PM2.5'], marker='o', color='#2E86AB', linewidth=2)
    ax.axvline(8, color='#F18F01', linestyle='--', alpha=0.5)
    ax.axvline(18, color='#C73E1D', linestyle='--', alpha=0.5)
    ax.set_xlabel('Jam')
    ax.set_ylabel('PM2.5 (µg/m³)')
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)

st.subheader('Distribusi PM2.5 per Arah Angin')
wind_filt = filtered.groupby('wd')['PM2.5'].mean().sort_values().reset_index()
wind_filt.columns = ['wd', 'avg_pm25']
fig, ax = plt.subplots(figsize=(12, 4))
sns.barplot(x='avg_pm25', y='wd', data=wind_filt, palette='RdYlBu_r', ax=ax)
ax.set_xlabel('PM2.5 (µg/m³)')
st.pyplot(fig)

st.caption('Sumber: Beijing PM2.5 Air Quality Dataset (PRSA)')
