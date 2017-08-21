#!/usr/bin/python

import sys
import requests
from flask import Flask, g, jsonify, render_template
from peewee import *
from peewee import MySQLDatabase
app = Flask(__name__)
database = MySQLDatabase("weather", host="localhost", user="root", password="sat")

month_rev_map = {"JAN":0, "FEB":1, "MAR":2, "APR":3, "MAY":4, "JUN":5, "JUL":6, "AUG":7, "SEP":8, "OCT":9, "NOV":10, "DEC":11, "WIN":12, "SPR":13, "SUM":14, "AUT":15, "ANN":16}
countries = ["UK", "England", "Wales", "Scotland"]
metrics = {"Tmax":"temp_max", "Tmin":"temp_min", "Tmean":"temp_mean", "Sunshine":"sunshine", "Rainfall":"rainfall"}
@app.before_request
def before_request():
    g.db = database
    g.db.get_conn()


@app.after_request
def after_request(response):
    g.db.close()
    return response


#display api
@app.route('/monthwisedata/<string:year>', methods = ["GET"])
def monthwise(year):
    res = {v:{} for k, v in metrics.iteritems()}
    #res = {"metric":[{"country", [16 vals]}]}
    all_countries = {}
    q =   WeatherData.select().where(WeatherData.year == year)
    country_data =  q.execute() 
    country_data_formated = []
    for v in country_data:
        if v.country in res["temp_min"]:
            res["temp_min"][v.country][month_rev_map[v.month]]=v.temp_min
        else:
            l = [0]*17
            l[month_rev_map[v.month]]=v.temp_min
            res["temp_min"].update({v.country : l})
        
        if v.country in res["temp_max"]:
            res["temp_max"][v.country][month_rev_map[v.month]]=v.temp_max
        else:
            l = [0]*17
            l[month_rev_map[v.month]]=v.temp_max
            res["temp_max"].update({v.country : l})
        if v.country in res["temp_mean"]:
            res["temp_mean"][v.country][month_rev_map[v.month]]=v.temp_mean
        else:
            l = [0]*17
            l[month_rev_map[v.month]]=v.temp_mean
            res["temp_mean"].update({v.country : l})
        if v.country in res["sunshine"]:
            res["sunshine"][v.country][month_rev_map[v.month]]=v.sunshine
        else:
            l = [0]*17
            l[month_rev_map[v.month]]=v.sunshine
            res["sunshine"].update({v.country : l})
        if v.country in res["rainfall"]:
            res["rainfall"][v.country][month_rev_map[v.month]]=v.rainfall
        else:
            l = [0]*17
            l[month_rev_map[v.month]]=v.rainfall
            res["rainfall"].update({v.country : l})
    return jsonify(res)

@app.route('/getyears', methods = ["GET"])
def get_years():
    q =   WeatherData.select(WeatherData.year).distinct()
    years = q.execute()
    years =  [y.year for y in years]
    return jsonify({"years":years})


#store apis
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


''' this will store data into db with 100 rows each time'''
def store_data_in_table(metric, data_source):
        data = list(data_source.values())
        with database.atomic():
            for row in data:
                try:
                    WeatherData.insert(row).execute()
                except IntegrityError:
                    pass

@app.route('/storeAll', methods=['GET'])
def store():
    url_offset = "http://www.metoffice.gov.uk/pub/data/weather/uk/climate/datasets/"
    store_to_tables(url_offset, countries, metrics)
    return jsonify({"status":"success"})

#data model
class BaseModel(Model):
    class Meta:
        database = database

#  model specifies its fields (or columns)
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
#one time create table
def create_tables():
    database.connect()
    database.create_tables([WeatherData])

@app.route('/')
def hello_world():
    return render_template("index.html")

