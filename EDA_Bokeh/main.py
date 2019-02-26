import feather
import pandas as pd
import configparser
import os
import glob
import os
import gc
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import datetime as dt
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf

from scripts.Compare_Features import Compare_Features_tab
from scripts.Fluctuation_Analysis import Fluctuation_Analysis_tab

config = configparser.ConfigParser()
config.read('EDA_Bokeh/main_config.ini')

def read_monthly_data(config):
    """General Purpose Reading Function to used across multiple Scripts
    Curently only works with the Data in the Local directory
    """
    input_location        = config['INPUT']['input_location']
    file_name_cmo_monthly = config['INPUT']['file_name_cmo_monthly']
    apmc                  = config['INPUT']['apmc']
    commodity             = config['INPUT']['commodity']
    correct_spelling      = config['INPUT']['correct_spelling']
    spelling_dict         = config['INPUT']['spelling_dict']
    remove_outliers       = config['OUTLIER']['remove_outliers']

    if config['INPUT']['nthreads'] != '':
        nthreads  = int(config['INPUT']['nthreads'])
    else:
        nthreads  = 6

    os.chdir(input_location)

    print("Reading Dataframe monthly_data_cmo")
    monthly_data = pd.read_csv(input_location+file_name_cmo_monthly)

    monthly_data.Commodity = monthly_data.Commodity.apply(lambda x: x.lower())
    monthly_data.Commodity = monthly_data.Commodity.apply(lambda x: x.lstrip())

    if apmc!='':
        print('Filtering for the APMCs ',apmc)
        monthly_data = monthly_data[monthly_data.APMC.isin(apmc.split(','))]

    if commodity!='':
        print('Filtering for the Commoditys ',commodity)
        monthly_data = monthly_data[monthly_data.Commodity.isin(commodity.split(','))]

    if correct_spelling=='TRUE':
        print('Correcting commodity spelling of monthly_data')
        monthly_data.Commodity = monthly_data.Commodity.apply(lambda x: spelling_dict[x] if x in spelling_dict.keys() else x)


    if remove_outliers=='TRUE':
        print('Removing Outliers from the data')
        shape_initial = monthly_data.shape[0]
        print('Shape before removing outliers: ',monthly_data.shape)
        monthly_data = monthly_data[monthly_data.modal_price>0]

        monthly_data_filtered = pd.DataFrame()
        for commodity in monthly_data.Commodity.unique():
            temp = monthly_data[monthly_data.Commodity==commodity]
            Q1 = temp.quantile(0.25)['modal_price']
            Q3 = temp.quantile(0.75)['modal_price']
            IQR = Q3 - Q1
            temp_filtered = temp[temp.modal_price > (Q1 - 1.5 * IQR)]
            temp_filtered = temp_filtered[temp_filtered.modal_price < (Q3 + 1.5 * IQR)]
            monthly_data_filtered = pd.concat([monthly_data_filtered,temp_filtered])

        print('Shape after removing outliers : ',monthly_data_filtered.shape)
        print('Percentage of outliers removed : %d'%((shape_initial-monthly_data_filtered.shape[0])/shape_initial))
    else:
        monthly_data_filtered = monthly_data

    monthly_data_filtered.date = pd.to_datetime(monthly_data_filtered.date)
    monthly_data_filtered.sort_values(by='date',inplace=True)
    monthly_data_filtered.dropna(inplace=True)

    return monthly_data

def read_cmo_mandi(config):
    """General Purpose Reading Function to used across multiple Scripts
    Curently only works with the Data in the Local directory
    """
    input_location        = config['INPUT']['input_location']
    file_name_mandi       = config['INPUT']['file_name_mandi']
    correct_spelling      = config['INPUT']['correct_spelling']
    spelling_dict         = config['INPUT']['spelling_dict']

    if config['INPUT']['nthreads'] != '':
        nthreads  = int(config['INPUT']['nthreads'])
    else:
        nthreads  = 6

    os.chdir(input_location)

    print("Reading Dataframe cmo_mandi")
    cmo_mandi    = pd.read_csv(input_location+file_name_mandi)

    cmo_mandi.commodity    = cmo_mandi.commodity.apply(lambda x: x.lower())
    cmo_mandi.commodity    = cmo_mandi.commodity.apply(lambda x: x.lstrip())


    if correct_spelling=='TRUE':
        print('Correcting commodity spelling of cmo_mandi')
        cmo_mandi.commodity = cmo_mandi.commodity.apply(lambda x: spelling_dict[x] if x in spelling_dict.keys() else x)

    cmo_mandi.dropna(inplace=True)

    return cmo_mandi

def deseasonalize(df,cmo_mandi):
    '''Fuction to de-seasonalize data'''

    df['APMC-Commodity'] = df.APMC.values + '-' + df.Commodity.values

    #Filtering the APMC-Commodity groups that have less than 24 data points
    df_grouped = df.groupby('APMC-Commodity').filter(lambda x: x['APMC-Commodity'].size>=24)

    print('Unique APMC-Commodity groups before subsetting : %d'%len(df['APMC-Commodity'].unique()))
    print('Unique APMC-Commodity groups after subsetting  : %d'%len(df_grouped['APMC-Commodity'].unique()))

    #Subetting the monthly_data_grouped dataframe for commodity values that are in cmo_mandi
    df_grouped = df_grouped[df_grouped.Commodity.isin(cmo_mandi.commodity.unique())]
    print('Number of APMC-Commodity pairs left after subsetting %d'%df_grouped['APMC-Commodity'].value_counts().size)

    monthly_data_deseason = pd.DataFrame()
    print("Detecting seasonality in the data for each APMC-Commodity pair")
    for apmc_commodity in df_grouped['APMC-Commodity'].unique():
        temp_deseasonal = pd.DataFrame()
        temp  = df_grouped[df_grouped['APMC-Commodity']==apmc_commodity] #Subsetting for apmc-commodity group
        temp.sort_values(by='date',inplace=True)
        temp2 = temp.set_index(keys='date')                                                 #setting date as index
        y     = (temp2['modal_price']).resample('20d').mean()
        y     = y.fillna(y.bfill())

        #Additively decomposing the timeseries
        decomposition_add = sm.tsa.seasonal_decompose(y, model='additive', freq=12,two_sided=False)
        #Multiplicatively decomposing the timeseries
        decomposition_mul = sm.tsa.seasonal_decompose(y, model='multiplicative', freq=12,two_sided=False)
        #Calculating acf of additive model
        acf_add = acf(decomposition_add.resid.dropna())
        #calculating acf of multiplicative model
        acf_mul = acf(decomposition_mul.resid.dropna())

        if sum(acf_add**2)>sum(acf_mul**2):
            #if sum of squared acf values of additive model is > than multiplicative then seasonality is multiplicative

            temp_deseasonal['date']               = decomposition_mul.trend.index
            temp_deseasonal['APMC_Commodity']     = temp2['APMC-Commodity'].unique()[0]
            temp_deseasonal['modal_price']        = decomposition_mul.observed.values
            temp_deseasonal['Seasonality_type']   = 'Multiplicative'
            temp_deseasonal['Seasonal_Component'] =  decomposition_mul.seasonal.values

            #Deseasonalizing the timeseries
            temp_deseasonal['modal_price_deseasonalized'] = temp_deseasonal['modal_price']/decomposition_mul.seasonal.values

        else:
            temp_deseasonal['date']               = decomposition_add.trend.index
            temp_deseasonal['APMC_Commodity']     = temp2['APMC-Commodity'].unique()[0]
            temp_deseasonal['modal_price']        = decomposition_add.observed.values
            temp_deseasonal['Seasonality_type']   = 'Additive'
            temp_deseasonal['Seasonal_Component'] =  decomposition_add.seasonal.values

            #Deseasonalizing the timeseries
            temp_deseasonal['modal_price_deseasonalized'] = temp_deseasonal['modal_price']-decomposition_add.seasonal.values

        monthly_data_deseason = pd.concat([temp_deseasonal, monthly_data_deseason])

    #Creating an Commodity column in monthly_data_deseason dataframe
    monthly_data_deseason['commodity'] = monthly_data_deseason['APMC_Commodity'].apply(lambda x:x.split('-')[1])
    monthly_data_deseason['APMC']      = monthly_data_deseason['APMC_Commodity'].apply(lambda x:x.split('-')[0])

    #Creating year column in monthly_data_deseason
    monthly_data_deseason['year'] = monthly_data_deseason.date.dt.year

    #Joining cmo mandi to monthly_data_deseason based on commodity and year
    final_df = monthly_data_deseason.merge(cmo_mandi,on=['commodity','year'],copy=False)

    #Calculating percentage fluctuation
    final_df['Percentage_fluc_des'] = round(((final_df.modal_price_deseasonalized - final_df.msprice)/final_df.msprice)*100,2)
    final_df['Percentage_fluc_raw'] = round(((final_df.modal_price_deseasonalized - final_df.msprice)/final_df.msprice)*100,2)


    return final_df





monthly_data               = read_monthly_data(config)
cmo_mandi                  = read_cmo_mandi(config)
monthly_data_deseasonalize = deseasonalize(monthly_data,cmo_mandi)

tab1 = Compare_Features_tab(monthly_data,cmo_mandi)
tab2 = Fluctuation_Analysis_tab(monthly_data_deseasonalize)

tabs = Tabs(tabs=[tab1,tab2])

curdoc().add_root(tabs)
curdoc().title = 'SocialCops Analysis'
