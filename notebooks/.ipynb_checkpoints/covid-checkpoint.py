from vega_datasets import data
import streamlit as st
import altair as slt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import matplotlib.dates as mdates
from bokeh.plotting import figure
plt.style.use('ggplot')
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import ScalarFormatter

# Renaming Countries
def rename(dataframe,dictionary):
    for key, value in dict_countries.items():
        for val in value:
            dataframe['Country'] = dataframe['Country'].str.replace(val,key)
            
# Plot Cumulative Number of Deaths
def cum_death(top_country_list,log_scale=True,size=(12,6)):
    x = list(range(21))
    y = [10*(1+0.33)**num for num in x]
    jet= plt.get_cmap('jet')
    colors = iter(jet(np.linspace(0,1,10)))
    fig, ax = plt.subplots(figsize=size)
    for c in top_country_list:
        my_color = next(colors)
        ax.plot(data.loc[c].query('Deaths>=10')['Deaths'].values,label=c,marker=".",color=my_color)
        ax.text(len(data.loc[c].query('Deaths>=10')['Deaths'].values.tolist()),data.loc[c].query('Deaths>=10')['Deaths'].values.tolist()[-1],c,color=my_color,weight="bold",family="monospace")
    if log_scale == True:
        ax.set_yscale('log')
    ax.set_yticks([20, 50, 100, 200, 500, 1000,2000,3000])
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    plt.plot(x,y,'--',color='black',alpha=0.5)
    plt.text(len(x),y[-1],'33% Daily Increase',color='grey',weight="bold",family="monospace")
    plt.title('Cumulative Number of Deaths, by number of days since 10th death');

dict_countries = {'United States':['US'],
                  'United Kingdom':['UK','Jersey','Guernsey'],
                  'China':['Mainland China'],
                  'Macao':['Macau'],
                  'Korea, Republic of':['South Korea','Korea, South'],
                  'Korea, North':['North Korea'],
                  'Russian Federation':['Russia'],
                  'Iran, Islamic Republic of':['Iran'],
                  'Macedonia':['North Macedonia'],
                  'Moldova, Republic of':['Moldova'],
                  'Cote d\'Ivoire':['Ivory Coast'],
                  'Holy See (Vatican City State)':['Holy See'],
                  'Congo, The Democratic Republic of the':['Congo (Kinshasa)','Republic of the Congo'],
                  'Congo':['Congo (Brazzaville)'],
                  'Brunei Darussalam':['Brunei'],
                  'Czech Republic':['Czechia'],
                  'Palestinian Territory':['occupied Palestinian territory'],
                  'Swaziland':['Eswatini'],
                  'Netherlands':['Curacao'],
                  'Serbia':['Kosovo'],
                  'Tanzania, United Republic of':['Tanzania'],
                  'Bahamas':['The Bahamas'],
                 
                 }

# Data
path = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports/'
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
df = pd.DataFrame()
for f in files:
    if f != '03-13-2020': # there is a bug in this report
        df_aux = pd.read_csv(path+f+'.csv')
        df_aux['Date'] = pd.to_datetime(f)
        df = pd.concat([df,df_aux])
    else:
        df_aux = pd.read_csv(path+f+'.csv')
        df_aux.loc[df_aux['Country/Region']!='China',['Last Update']] = df_aux[df_aux['Country/Region'] != 'China']['Last Update'].str.replace('-11T','-13T')    
        df_aux['Date'] = pd.to_datetime(f)
        df = pd.concat([df,df_aux])
# Renaming
df.rename(columns={'Country/Region':'Country'},inplace=True)
df.rename(columns={'Province/State':'Province'},inplace=True)
rename(df,dict_countries)
# Provinces
df.loc[df['Province']=='Hong Kong',['Country']] = 'Hong Kong'
df.loc[df['Province']=='Macau',['Country']] = 'Macao'
df.loc[df['Province']=='Taiwan',['Country']] = 'Taiwan'
df.loc[df['Country'].str.startswith('Tai'),['Country']] = 'Taiwan'
data = df.groupby(['Country','Date'])['Confirmed','Recovered','Deaths'].sum()
# Data from Last Report by Country
data_last_report = data.loc[data.index.get_level_values(1) == datetime.strptime(files[-1],'%m-%d-%Y')]
# TOP Country List by Confirmed Cases
top_list = data_last_report.sort_values(by='Confirmed',ascending=False)['Confirmed'][:10].index.get_level_values(0).tolist()
coord = pd.read_csv('https://raw.githubusercontent.com/albertyw/avenews/master/old/data/average-latitude-longitude-countries.csv')
maps = pd.merge(data_last_report,coord,on=['Country'])
maps.rename(columns={'Latitude':'lat'},inplace=True)
maps.rename(columns={'Longitude':'lon'},inplace=True)
mapa = maps[['Confirmed','lat','lon']]

def main():
    page = st.sidebar.selectbox("Choose a page", ["Report by Country", "Dashboard","Map"])
    
    if page == "Report by Country":
        url = 'https://www.charlescountymd.gov/Home/ShowPublishedImage/4496/637195158875230000'
        st.image(url,use_column_width=True)
        st.title("COVID-19")
        countries = list(set(df['Country'].values.tolist()))
        filtro = st.selectbox('Select a Country',countries)
        st.subheader(filtro+' Dataframe')
        st.write(data.loc[filtro])
        st.subheader(filtro+' Plot')
        st.line_chart(data.loc[filtro,['Confirmed','Recovered','Deaths']])
    elif page == 'Dashboard':
        url = 'https://www.charlescountymd.gov/Home/ShowPublishedImage/4496/637195158875230000'
        st.image(url,use_column_width=True)
        st.title("COVID-19")
        
        fig = plt.figure(figsize=(36,20),constrained_layout=True)
        gs = GridSpec(4, 3, figure=fig)
        ax1 = fig.add_subplot(gs[:2, :])
        ax2 = fig.add_subplot(gs[2, :1])
        ax3 = fig.add_subplot(gs[2, 1:2])
        ax4 = fig.add_subplot(gs[2, -1])
        ax5 = fig.add_subplot(gs[3, :1])
        ax6 = fig.add_subplot(gs[3, 1:2])
        ax7 = fig.add_subplot(gs[3, -1])
        # Colors
        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,10)))
        clist = [(0, "red"), (0.125, "red"), (0.25, "orange"), (0.5, "green"), 
                 (0.7, "green"), (0.75, "blue"), (1, "blue")]
        rvb = mcolors.LinearSegmentedColormap.from_list("", clist)
        N1 = 10
        N2 = 9
        x1 = np.arange(N1).astype(float)
        x2 = np.arange(N2).astype(float)
        y1 = np.random.uniform(0, 5, size=(N1,))
        y2 = np.random.uniform(0, 5, size=(N2,))
        # Axis 1
        for country in top_list:
            ax1.plot(data.loc[country,['Confirmed']],label=country[:15],color=next(colors),alpha=0.5)
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax1.xaxis.set_minor_locator(mdates.DayLocator())
        ax1.legend(loc='upper left', bbox_to_anchor=(0.0, 1, 0.20, 0),mode="expand",ncol=2)
        ax1.set_title('COVID-19')
        # Axis 2, 5
        ax2.bar(data_last_report.sort_values(by='Confirmed',ascending=False)['Confirmed'][:10].index.get_level_values(0),data_last_report.sort_values(by='Confirmed',ascending=False)['Confirmed'][:10].values,color=rvb(x1/N1))
        ax2.tick_params(labelrotation=45,labelsize=8)
        ax2.title.set_text('TOP Confirmed')
        ax5.bar(data_last_report.sort_values(by='Confirmed',ascending=False)['Confirmed'][1:10].index.get_level_values(0),data_last_report.sort_values(by='Confirmed',ascending=False)['Confirmed'][1:10].values,color=rvb(x2/N2))
        ax5.tick_params(labelrotation=45,labelsize=8)
        ax5.title.set_text('TOP Confirmed w/o China')
        # Axis 3, 6
        ax3.bar(data_last_report.sort_values(by='Recovered',ascending=False)['Recovered'][:10].index.get_level_values(0),data_last_report.sort_values(by='Recovered',ascending=False)['Recovered'][:10].values,color=rvb(x1/N1))
        ax3.tick_params(labelrotation=45,labelsize=8)
        ax3.title.set_text('TOP Recovered')
        ax6.bar(data_last_report.sort_values(by='Recovered',ascending=False)['Recovered'][1:10].index.get_level_values(0),data_last_report.sort_values(by='Recovered',ascending=False)['Recovered'][1:10].values,color=rvb(x2/N2))
        ax6.tick_params(labelrotation=45,labelsize=8)
        ax6.title.set_text('TOP Recovered w/o China')
        # Axis 4, 7
        ax4.bar(data_last_report.sort_values(by='Deaths',ascending=False)['Deaths'][:10].index.get_level_values(0),data_last_report.sort_values(by='Deaths',ascending=False)['Deaths'][:10].values,color=rvb(x1/N1))
        ax4.tick_params(labelrotation=45,labelsize=8)
        ax4.title.set_text('TOP Deaths')
        ax7.bar(data_last_report.sort_values(by='Deaths',ascending=False)['Deaths'][1:10].index.get_level_values(0),data_last_report.sort_values(by='Deaths',ascending=False)['Deaths'][1:10].values,color=rvb(x2/N2))
        ax7.tick_params(labelrotation=45,labelsize=8)
        ax7.title.set_text('TOP Deaths w/o China')
        
        st.pyplot()
        
        cum_death(top_list,log_scale=True,size=(16,8))
        st.pyplot()
    else:
        url = 'https://www.charlescountymd.gov/Home/ShowPublishedImage/4496/637195158875230000'
        st.image(url,use_column_width=True)
        st.title("COVID-19")
        st.map(mapa)

if __name__ == "__main__":
    main()