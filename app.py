import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template

import requests
import pandas as pd
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='static/uploads'


#Function to generate url endpoint for api
def GetEndpoints(leagueid):
    apis = []
    baseEndpoint = "https://fantasy.premierleague.com/api/leagues-h2h-matches/league/"
    finalbaseEndpoint = baseEndpoint + leagueid + '/'
    for i in range(1, 8):
        if i == 1 :
          #print(baseEndpoint)
          apis.append(finalbaseEndpoint)
        else:
            apiEndpoint = finalbaseEndpoint + "?page=" + str(i)
            #print(apiEndpoint)
            apis.append(apiEndpoint)
    return apis

#Get all response jsons and append to one whole json
def GetAndAppendAllToOneJson(leagueid):
    combinedJson = []
    apis = GetEndpoints(leagueid)
    for api in apis:
        response = GetAPIResponse(api)
        resultsjson = response['results']
        combinedJson = combinedJson + resultsjson
    finaldataframe = pd.DataFrame(combinedJson)
    return finaldataframe


#Function to get responses from API
def GetAPIResponse(APIEndpointURL):
    response = requests.get(APIEndpointURL).json()
    return response

#Convert API response to JSON
def ConvertToJson(data):
    response = data.json()

#######Everything above this line reads teh apis and appends them alotogether#######
#######Below is an example of me writing to pandas df using just 1 API URL. This works but i dont know how o write the appended apis to pandas.
#Create Dataframe

#try this out

#print(finalDataFrame)


@app.route('/')
def root():
    return render_template('Home.html')

@app.route('/fetchleaguedata',methods=['POST'])
def LeagueDatafetch():
    leagueid = request.form['leagueid']
    finalDataFrame = GetAndAppendAllToOneJson(leagueid)

    return render_template('Dataview.html', column_names=finalDataFrame.columns.values, row_data=list(finalDataFrame.values.tolist()), zip=zip )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True,threaded=True)

    app.debug = True
    app.run()
