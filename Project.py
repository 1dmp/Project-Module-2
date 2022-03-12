# libraries
import pandas as pd
import requests
from zipfile import ZipFile
from scipy.stats import ttest_rel
from scipy.stats import pearsonr
from scipy.stats import f_oneway

# read the .csv files
airlines = pd.read_csv('airlines.csv')
airports = pd.read_csv('airports.csv')
flights_interest = pd.read_csv('flights_interest.csv')

# display a concise summary of dataframes
airlines.info()
airports.info()
flights_interest.info()

# let's define the columns of dataframe that we are interested in
columns_interesting = ['MONTH', 'DAY_OF_WEEK',
                       'AIRLINE',
                       'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT',
                       'DEPARTURE_DELAY', 
                       'DISTANCE',
                       'ARRIVAL_DELAY']

# let's define a dataframe 'flights_interest' with the columns selected above
flights_interest = flights_interest[columns_interesting]

# let's create two new boolean variables based on 'departure_delay' ('dep_delay') and 
# 'arrival_delay' ('arr_delay')
flights_interest['arr_delay'] = (flights_interest.loc[:,'ARRIVAL_DELAY'] > 0).\
    astype('int', copy= False)
    
flights_interest['dep_delay'] = (flights_interest.loc[:,'DEPARTURE_DELAY'] > 0).\
    astype('int', copy= False)
    

# It was verified that some of the airports had not IATA codes (3 letters), but a five number
# codes. The address below was the source for the data that allowed to convert a 5-digit code
# into an IATA code

"""
https://www.transtats.bts.gov/
Data Finder, By Mode, Aviation
Aviation Support Tables
Master Coordinate
Download
"""

# let's store the list of airports with 5-digit codes in a dataframe, opening the .zip file
# that contains the .csv
with ZipFile('T_MASTER_CORD_20220309_171749.zip') as myzip:
    with myzip.open('T_MASTER_CORD.csv') as myfile:
        list_airports = pd.read_csv(myfile)
myzip.close()

# let's convert the 5-digit code with the information contained in 'T_MASTER_CORD.csv'
for i in flights_interest.loc[flights_interest['ORIGIN_AIRPORT'].str.len() > 3].index:
    flights_interest.loc[i,'ORIGIN_AIRPORT'] = \
    list_airports[list_airports['AIRPORT_ID'] == \
                  int(flights_interest.loc[i,'ORIGIN_AIRPORT'])].tail(1)['AIRPORT'].values[0]
        
for i in flights_interest.loc[flights_interest['DESTINATION_AIRPORT'].str.len() > 3].index:
    flights_interest.loc[i,'DESTINATION_AIRPORT'] = \
    list_airports[list_airports['AIRPORT_ID'] == \
                  int(flights_interest.loc[i,'DESTINATION_AIRPORT'])].tail(1)['AIRPORT'].\
        values[0]
        
# let's merge the information contained in 3 different dataframes (airlines, airports, 
# flights_interest) just in one dataframe (flights_airlines_airports)
flights_airlines = pd.merge(flights_interest, airlines,
                            left_on= 'AIRLINE', 
                            right_on= 'IATA_CODE')

flights_origin_airport = pd.merge(flights_airlines, airports, 
                                  left_on= 'ORIGIN_AIRPORT', 
                                  right_on= 'IATA_CODE')

flights_airlines_airports = pd.merge(flights_origin_airport, airports,
                            left_on= 'DESTINATION_AIRPORT',
                            right_on= 'IATA_CODE')

# let's drop the columns we are not interested in 'flights_airlines_airports'
flights_airlines_airports = flights_airlines_airports.drop(columns= ['AIRLINE_x',
                                                                     'ORIGIN_AIRPORT',
                                                                     'DESTINATION_AIRPORT',
                                                                     'IATA_CODE_x',
                                                                     'IATA_CODE_y',
                                                                     'COUNTRY_x',
                                                                     'IATA_CODE',
                                                                     'COUNTRY_y'])

# let's rename the names of columns in 'flights_airlines_airports'
flights_airlines_airports= \
    flights_airlines_airports.rename(columns= {'AIRLINE_y': 'AIRLINE',
                                               'AIRPORT_x': 'ORIGIN_AIRPORT',
                                               'CITY_x': 'CITY_ORIGIN_AIRPORT',
                                               'STATE_x': 'STATE_ORIGIN_AIRPORT',
                                               'LATITUDE_x': 'LATITUDE_ORIGIN_AIRPORT',
                                               'LONGITUDE_x': 'LONGITUDE_ORIGIN_AIRPORT',
                                               'AIRPORT_y': 'DESTINATION_AIRPORT',
                                               'CITY_y': 'CITY_DESTINATION_AIRPORT',
                                               'STATE_y': 'STATE_DESTINATION_AIRPORT',
                                               'LATITUDE_y': 'LATITUDE_DESTINATION_AIRPORT',
                                               'LONGITUDE_y': 'LONGITUDE_DESTINATION_AIRPORT'})
    
# let's put the dataframe 'flights_airlines_airports' into a .csv
flights_airlines_airports.to_csv('flights_tableau.csv')

# Let's test some hypothesis

### MONTH vs DELAYS ###

# Arrival delay
a = flights_airlines_airports.groupby('MONTH')['ARRIVAL_DELAY'].agg('mean').values

# Departure delay
b = flights_airlines_airports.groupby('MONTH')['DEPARTURE_DELAY'].agg('mean').values

print(ttest_rel(a,b))

### DAY OF WEEK vs DELAYS ###

# Arrival delay
a = flights_airlines_airports.groupby('DAY_OF_WEEK')['ARRIVAL_DELAY'].agg('mean').values

# Departure delay
b = flights_airlines_airports.groupby('DAY_OF_WEEK')['DEPARTURE_DELAY'].agg('mean').values

print(ttest_rel(a,b))

### AIRLINE vs DELAYS ###

# Arrival delay
a = flights_airlines_airports.groupby('AIRLINE')['ARRIVAL_DELAY'].agg('mean').values

# Departure delay
b = flights_airlines_airports.groupby('AIRLINE')['DEPARTURE_DELAY'].agg('mean').values

print(ttest_rel(a,b))

### DELAYS (ARRIVAL vs DEPARTURE) ###

print(pearsonr(flights_airlines_airports['ARRIVAL_DELAY'], 
         flights_airlines_airports['DEPARTURE_DELAY']))

# Now let's find the airports which are common between the columns 'ORIGIN_AIRPORT' and
# 'DESTINATION_AIRPORT'

common_airports = list(set(flights_airlines_airports['ORIGIN_AIRPORT']).\
                       intersection(set(flights_airlines_airports['DESTINATION_AIRPORT'])))
    
# for departures

departure_delays = []

for airport in common_airports:
        dd = []
        for row in range(len(flights_airlines_airports)):
            if flights_airlines_airports['ORIGIN_AIRPORT'][row] == airport:
                dd.append(flights_airlines_airports['DEPARTURE_DELAY'][row])
        departure_delays.append(dd)
        
print(f_oneway(*departure_delays))

# for arrivals

arrival_delays = []

for airport in common_airports:
        ad = []
        for row in range(len(flights_airlines_airports)):
            if flights_airlines_airports['DESTINATION_AIRPORT'][row] == airport:
                ad.append(flights_airlines_airports['ARRIVAL_DELAY'][row])
        arrival_delays.append(ad)
        
print(f_oneway(*arrival_delays))

###  DISTANCE vs ARRIVAL DELAY ###
print(pearsonr(flights_interest['ARRIVAL_DELAY'], flights_interest['DISTANCE']))