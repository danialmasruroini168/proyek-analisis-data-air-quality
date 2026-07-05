# Proyek Analisis Data: Air Quality Dataset

Dashboard interaktif untuk menganalisis kualitas udara Beijing (PRSA) 2013–2017.

## Setup Environment - Anaconda

```
conda create --name proyek-airquality python=3.9
conda activate proyek-airquality
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek-airquality
cd proyek-airquality
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```
streamlit run dashboard/dashboard.py
```
