#!/usr/bin/python

import sys
import requests
from flask import Flask, g, jsonify
from peewee import *
from peewee import MySQLDatabase
app = Flask(__name__)
database = MySQLDatabase("weather", host="localhost", user="root", password="root")

countries = ["UK", "England", "Wales", "Scotland"]
metrics = {"Tmax":"temp_max", "Tmin":"temp_min", "Tmean":"temp_mean", "Sunshine":"sunshine", "Rainfall":"rainfall"}
@app.before_request
def before_request():
    g.db = database
    g.db.get_conn()


@app.after_request
def after_request(response):
    g.db.close()
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


#display api
@app.route('/monthwisedata/<string:year>', methods = ["GET"])
def monthwise(year):
    res = {}
    #res = {"metric":[{"country", [16 vals]}]}
    metrics = ["Tmax"]
    for metric in metrics.keys():
        all_countries = {}
        for country in countries:
            q =   WeatherData.select().where((WeatherData.year == year) & (WeatherData.country == country))
            print q
            country_data =  q.execute() 
            country_data_formated = []
            for v in country_data:
                print v.month, v.year, v.country
                country_data_formated.append({v.month:v.value})
            print country_data_formated
            all_countries.update({country: country_data_formated})
        res.update({metric:all_countries})
            #res[metric].append({country:values}) 
    return jsonify(res)

#@app.route('/min_temp')
#def min_temp():
#
#
#@app.route('/sunshine')
#
#@app.route('/rainfall')

#store api

'''fetch data from apis for all countries defined in "countries" list and store them in a dict "data_source"'''
def store_to_tables(url_offset, countries, metrics):
    month_map = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC", 13:"WIN", 14:"SPR", 15:"SUM", 16:"AUT", 17:"ANN"}
    data_source = {}
    for metric in metrics.keys():
        for country in countries:
            url = url_offset + metric +"/ranked/"+country+ ".txt"
            print url
            metric_data = requests.get(url, stream=True)
            count = 0
            for l in metric_data.iter_lines():
                count += 1
                if count < 9:
                    continue
                line_data = l.split()
                #print "line", line_data
                for k,v in enumerate(line_data):
                    if k%2 == 0:
                        month = month_map[k/2+1]
                        val = v
                    else:
                        year = v
                        unique_set = (month,year,country)
                        if(data_source.get(unique_set) == None):
                            data_source[unique_set] = {"month":month, metrics[metric]:val, "year":year, "country":country}
                        else :
                            data_source[unique_set][metrics[metric]] = val
        store_data_in_table(metric, data_source)
    print 1
            #print metric, "data:", metric_data.text


''' this will store data into db with 100 rows each time'''
def store_data_in_table(metric, data_source):
        data = list(data_source.values())
        with database.atomic():
            for idx in range(0, len(data), 100):
                WeatherData.insert_many(data[idx:idx + 100]).execute()


@app.route('/storeAll', methods=['GET'])
def store():
    url_offset = "http://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/"

    store_to_tables(url_offset, countries, metrics)
    #countries = get_countries()
    return jsonify({})

#model

class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns)

'''Model to Store data '''
class WeatherData(BaseModel):
    month = CharField()
    year = CharField()
    temp_min = DecimalField(default=0)
    temp_max = DecimalField(default=0)
    temp_mean = DecimalField(default=0)
    sunshine = DecimalField(default=0)
    rainfall = DecimalField(default=0)
    country = CharField()

    class Meta:
        indexes = (
            (("month","year","country"), True),
        )




def create_tables():
    database.connect()
    database.create_tables([WeatherData])

#def store_single_table(table, data):
#    return True 
@app.route('/')
def hello_world():
    return 'Hello, World!'

#app.run(port = 8888, debug=Truesseu)
