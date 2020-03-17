from vega_datasets import data
import streamlit as st
import altair as slt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import matplotlib.dates as mdates
from bokeh.plotting import figure

def main():
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration"])
    
    if page == "Homepage":
        df = load_data(flag='Report')
        st.header("COVID-19")
        st.write("Last Report")
        st.write(df)
        countries = list(set(df['Country/Region'].values.tolist()))
        filtro = st.selectbox('Select a Country',countries)
        st.write(df[df['Country/Region']==filtro])
    else:
        # Paths
        path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
        files = []
        # Dates
        start_date = date(2020,1,22) # First Report
        end_date = date.today() - timedelta(days=1)# Today
        delta = end_date - start_date # Days from the first report
        # Files
        for i in range(delta.days+1):
            dates = start_date + timedelta(days=i)
            files.append(dates.strftime('%m-%d-%Y'))
        # Bug 13/03/2020
        df2 = pd.DataFrame()
        for f in files:
            if f != '03-13-2020': # there is a bug in this report
                df_aux = pd.read_csv(path+f+'.csv')
                df_aux['Date'] = pd.to_datetime(f)
                df2 = pd.concat([df2,df_aux])
            else:
                df_aux = pd.read_csv(path+f+'.csv')
                df_aux.loc[df_aux['Country/Region']!='China',['Last Update']] = df_aux[df_aux['Country/Region'] != 'China']['Last Update'].str.replace('-11T','-13T')    
                df_aux['Date'] = pd.to_datetime(f)
                df2 = pd.concat([df2,df_aux]) 
                data = df2.groupby(['Country/Region','Date'])['Confirmed','Recovered','Deaths'].sum()
                st.header("COVID-19")
                st.write("Graph")
                st.write(data)
                countries = list(set(df2['Country/Region'].values.tolist()))
                filtro = st.selectbox('Select a Country',countries)
                st.line_chart(data=data.loc[countries,['Confirmed']], use_container_width=True)


@st.cache   
def load_data(flag):
    if flag == 'Report':
        path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/03-13-2020.csv'
        df = pd.read_csv(path)
        return df
    else:
        path = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
        df = pd.read_csv(path)
        return df

if __name__ == "__main__":
    main()