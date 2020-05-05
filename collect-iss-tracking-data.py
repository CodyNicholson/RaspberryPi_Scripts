import requests
import json
import random
from config import weather_api_key, host, port, database, user, password
import sqlalchemy as db
from sqlalchemy import create_engine

# Get ISS Position Data
iss_url = "http://api.open-notify.org/iss-now.json"
iss_data = requests.get(iss_url).json()
#print(json.dumps(iss_data, indent=4, sort_keys=True))
iss_lat = iss_data["iss_position"]["latitude"]
iss_lon = iss_data["iss_position"]["longitude"]
iss_timestamp = iss_data["timestamp"]

# Get Random Number From Timestamp
rand_num = round(random.random(), 1)
splice_num = -1
if(rand_num < 0.4):
    splice_num = -2
elif(0.4 >= rand_num < 0.7):
    splice_num = -3
lookup_num = str(iss_timestamp)[splice_num:]
num_url = f"http://numbersapi.com/{lookup_num}/math?json"
num_data = requests.get(num_url).json()
#print(json.dumps(num_data, indent=4, sort_keys=True))
num_description = num_data["text"]

# Weather Data
weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={iss_lat}&lon={iss_lon}&appid={weather_api_key}&units=imperial"
weather_data = requests.get(weather_url).json()
#print(json.dumps(weather_data, indent=4, sort_keys=True))
weather_description = weather_data["weather"][0]["description"]
weather_temp = weather_data["main"]["temp"]
try:
    country_alpha_code = weather_data["sys"]["country"]
except: 
    country_alpha_code = ""

# Country Data
if (country_alpha_code != ""):
    country_url = f"https://restcountries.eu/rest/v2/alpha/{country_alpha_code}"
    country_data = requests.get(country_url).json()
    #print(json.dumps(country_data, indent=4, sort_keys=True))
    country_name = country_data["name"]
    country_borders = country_data["borders"]
    country_flag_url = country_data["flag"]
    country_capital = country_data["capital"]
    print(json.dumps(country_data, indent=4, sort_keys=True))
else:
    country_name = ""
    country_borders = ""
    country_flag_url = ""
    country_capital = ""

# Write To Postgres
engine = create_engine(f"postgresql://{user}:{password}@{host}/{database}")
connection = engine.connect()
metadata = db.MetaData()

iss_data_table = db.Table('iss_data_table', metadata,
              db.Column('iss_timestamp', db.String(50)),
              db.Column('iss_lat', db.String(20), nullable=False),
              db.Column('iss_lon', db.String(20), nullable=False),
              db.Column('num_description', db.String(255), nullable=True),
              db.Column('weather_description', db.String(255), nullable=True),
              db.Column('weather_temp', db.String(10), nullable=True),
              db.Column('country_alpha_code', db.String(10), nullable=True),
              db.Column('country_name', db.String(50), nullable=True),
              db.Column('country_borders', db.String(255), nullable=True),
              db.Column('country_flag_url', db.String(255), nullable=True),
              db.Column('country_capital', db.String(50), nullable=True)
              )

metadata.create_all(engine)
query = db.insert(iss_data_table).values(iss_timestamp=iss_timestamp, iss_lat=iss_lat, iss_lon=iss_lon, num_description=num_description, weather_description=weather_description, weather_temp=weather_temp, country_alpha_code=country_alpha_code, country_name=country_name, country_borders=country_borders, country_flag_url=country_flag_url, country_capital=country_capital)
ResultProxy = connection.execute(query)
