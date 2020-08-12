import numpy as np
import pandas as pd

JH_CSSE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
global_confirmed = f"{JH_CSSE}/time_series_covid19_confirmed_global.csv"
global_deaths =  f"{JH_CSSE}/time_series_covid19_deaths_global.csv"
global_recoveries = f"{JH_CSSE}/time_series_covid19_recovered_global.csv"
us_confirmed = f"{JH_CSSE}/time_series_covid19_confirmed_US.csv"
us_deaths = f"{JH_CSSE}/time_series_covid19_deaths_US.csv"

def test(string):
	return string

def clean_data(df_raw):
    dates = df_raw.columns[4:]
    df_cleaned = df_raw.melt(id_vars=['Province/State','Country/Region','Lat','Long'], 
                             value_vars=dates,
                             value_name='Cases', 
                             var_name='Date')
    df_cleaned = df_cleaned.set_index(['Country/Region','Province/State','Date'])
    df_cleaned["Cases"] = pd.to_numeric(df_cleaned["Cases"], downcast="float")
    return df_cleaned 

def country_data(df_cleaned, newname):    
    df_country = df_cleaned.groupby(['Country/Region','Date'])['Cases'].sum().reset_index()
    df_country = df_country.rename(columns={'Country/Region': 'country', 'Date': 'date'})
    df_country = df_country.set_index(['country','date'])
    df_country.index = df_country.index.set_levels([df_country.index.levels[0], pd.to_datetime(df_country.index.levels[1])])
    df_country = df_country.sort_values(['country','date'], ascending=True)
    df_country = df_country.rename(columns={'Cases': newname})
    return df_country

def daily_data(df_country, oldname, newname):
    df_countrydaily = df_country.groupby(level=0).diff().fillna(0)
    df_countrydaily = df_countrydaily.rename(columns={oldname:newname})
    return df_countrydaily


def calc_averages(df_cons):
	#df_cons['active'] =  np.round(
    #	df_cons['confirmed']-df_cons['deaths']-df_cons['recoveries'], 2).fillna(0)
	df_cons['roll_confirmed'] = np.round(
    	df_cons.groupby('country', level=0)['new_confirmed'].rolling(7).mean(), 3).fillna(0).values
	df_cons['roll_deaths'] = np.round(
    	df_cons.groupby('country', level=0)['new_deaths'].rolling(7).mean(), 3).fillna(0).values
	df_cons['pct_recoveries'] = np.round(
    	df_cons['recoveries']/(df_cons['recoveries']+df_cons['deaths']), 3).fillna(0)
	df_cons['deaths_ratio'] = np.round(
    	df_cons['deaths']/df_cons['confirmed'], 3).fillna(0)
	return df_cons


def doubling(indata):
    readings=indata.to_numpy()
    readingsLength=len(readings)
    double=np.zeros(readingsLength)
    double[:]=np.NaN
    for i in range(readingsLength - 1, -1, -1):
        target=readings[i]
        count=0
        for j in range(i, -1, -1):
            diffsofar=target-readings[j]
            exact=target / 2
            if diffsofar > exact:
                f=(exact - readings[j]) / (readings[j]-readings[j+1]) + count
                double[i]=f
                break
            else:
                count=count+1
    outdata=pd.Series(data= double, name = indata.name, index = indata.index)
    return outdata