import json
import urllib.request
from urllib.error import HTTPError
from urllib.parse import quote
import pandas as pd
import plotly.graph_objs as go
from django.shortcuts import render

from .models import City


def index(request):
    # cities = City.objects.all()
    if request.method == 'POST':
        city = request.POST['city']
        city2 = request.POST['city2']
        end_date = request.POST['end_date']
        start_date = request.POST['start_date']



        city = city.split()
        city = '%20'.join(city)



        city2 = city2.split()
        city2 = '%20'.join(city2)


        try:
            source = urllib.request.urlopen('https://geocoding-api.open-meteo.com/v1/search?name=' + city).read()
        except UnicodeEncodeError:
            city = quote(city)
            source = urllib.request.urlopen('https://geocoding-api.open-meteo.com/v1/search?name=' + city + '&language=ru').read()
        try:
            source3 = urllib.request.urlopen('https://geocoding-api.open-meteo.com/v1/search?name=' + city2).read()
        except UnicodeEncodeError:
            city2 = quote(city2)
            source3 = urllib.request.urlopen('https://geocoding-api.open-meteo.com/v1/search?name=' + city2 + '&language=ru').read()

        list_of_data = json.loads(source)
        list_of_data3 = json.loads(source3)

        try:
            source2 = urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?latitude='+str(list_of_data['results'][0]['latitude'])+'&longitude='+str(list_of_data['results'][0]['longitude'])+'&start_date='+start_date+'&end_date='+end_date+'&hourly=temperature_2m').read()
        except KeyError:
            return render(request, "weatherapp/index.html", {'error': "Выберите 2 существующих города"})
        except HTTPError as err:
            if err.code == 400:
                return render(request, "weatherapp/index.html", {'error': "Выберите корректные даты"})
            else:
                raise
            source2 = urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?latitude=' + str(list_of_data['results'][0]['latitude']) + '&longitude=' + str(list_of_data['results'][0]['longitude']) + '&start_date=' + start_date + '&end_date=' + start_date + '&hourly=temperature_2m').read()
        list_of_data2 = json.loads(source2)

        try:
            source4 = urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?latitude='+str(list_of_data3['results'][0]['latitude'])+'&longitude='+str(list_of_data3['results'][0]['longitude'])+'&start_date='+start_date+'&end_date='+end_date+'&hourly=temperature_2m').read()
        except KeyError as kerr:
            return render(request, "weatherapp/index.html", {'error': "Выберите 2 существующих города"})
        except HTTPError as err:
            if err.code == 400:
                return render(request, "weatherapp/index.html", {'error': "Выберите корректные даты"})
            else:
                raise
            source4 = urllib.request.urlopen('https://archive-api.open-meteo.com/v1/archive?latitude=' + str(list_of_data3['results'][0]['latitude']) + '&longitude=' + str(list_of_data3['results'][0]['longitude']) + '&start_date=' + start_date + '&end_date=' + start_date + '&hourly=temperature_2m').read()
        list_of_data4 = json.loads(source4)

        data = {
                "period": str(list_of_data2['hourly']),
                "time": str(list_of_data2['hourly']['time'][::]).replace("', '", " ").replace("'", ""),
                "temperature": str(list_of_data2['hourly']['temperature_2m'][::]),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "name": str(list_of_data['results'][0]['name']),
                "country": str(list_of_data['results'][0]['country']),
                "lat": str(list_of_data['results'][0]['latitude']),
                "lon": str(list_of_data['results'][0]['longitude']),

                "period2": str(list_of_data4['hourly']),
                "time2": str(list_of_data4['hourly']['time'][::]).replace("', '", " ").replace("'", ""),
                "temperature2": str(list_of_data4['hourly']['temperature_2m'][::]),
                "start_date2": str(start_date),
                "end_date2": str(end_date),
                "name2": str(list_of_data3['results'][0]['name']),
                "country2": str(list_of_data3['results'][0]['country']),
                "lat2": str(list_of_data3['results'][0]['latitude']),
                "lon2": str(list_of_data3['results'][0]['longitude']),
        }

        df = pd.DataFrame(data=data, index=[0])
        temp = df['temperature'][0].replace("', '", ", ").replace("[", "").replace("]", "").replace("None", "nan").replace("'", "").replace(",", "")
        temp2 = df['temperature2'][0].replace("', '", ", ").replace("[", "").replace("]", "").replace("None", "nan").replace("'", "").replace(",", "")
        dt = df['time'][0].replace("'", "").replace("[", "").replace("]", "")
        d = dt.split()
        t = str(temp).split()
        result = list(map(float, t))
        t2 = str(temp2).split()
        result2 = list(map(float, t2))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d, y=result,
                                 mode='lines',
                                 name=df['name'][0]))
        fig.add_trace(go.Scatter(x=d, y=result2,
                                 mode='lines',
                                 name=df['name2'][0]))
        fig.update_layout(
            yaxis_title='Temperature, °C',
            xaxis_title='Date',
            title='Temperature comparison'
        )

        fig.write_html("weatherapp/templates/weatherapp/graph.html")

    else:
        data = {}

    return render(request, "weatherapp/index.html", data)


def graph(request):
    return render(request, "weatherapp/graph.html")






