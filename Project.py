# libraries
import pandas as pd
import requests

# read the .csv files
airlines = pd.read_csv('airlines.csv')
airports = pd.read_csv('airports.csv')
flights = pd.read_csv('flights_interest.csv')

# display a concise summary of dataframes
airlines.info()
airports.info()
flights.info()

# select a sample of 100 rows from all data available 
# defining a seed for analysis purposes
flights_interest = flights.sample(n= 100, random_state= 7)

# let's check some rows of sample
flights_interest