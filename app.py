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

def createleaderboard(finalDataFrame):
    Leaderboardlist=[]
    listplayerid = finalDataFrame['entry_1_entry'].unique()
    for player in listplayerid:
        for index, row in finalDataFrame.iterrows():
            if (row['entry_1_entry']==player):
                Leaderboardlist.append([row['id'],row['entry_1_entry'],row['entry_1_name'],row['entry_1_player_name'],row['entry_1_points'],row['entry_1_win'],row['entry_1_loss'],row['entry_1_draw'],row['entry_1_total'],row['event']])
            elif (row['entry_2_entry']==player):
                Leaderboardlist.append([row['id'],row['entry_2_entry'],row['entry_2_name'],row['entry_2_player_name'],row['entry_2_points'],row['entry_2_win'],row['entry_2_loss'],row['entry_2_draw'],row['entry_2_total'],row['event']])

    LeaderboardDf = pd.DataFrame(Leaderboardlist, columns=['matchid', 'PlayerID','TeamName', 'PlayerName','GWPoints','Win','Loss','Draw','H2Hpoints','GW'])
    return LeaderboardDf


def creatRankBoard(LeaderboardDf):

    Rankdf = LeaderboardDf.groupby(['PlayerID','TeamName','PlayerName'],as_index=False, sort=False).agg({'GWPoints': "sum", 'H2Hpoints': "sum",'Win': 'sum','Loss': 'sum','Draw': 'sum'})

    return Rankdf

def createH2Hweekly(LeaderboardDf):


    LeaderboardDf = LeaderboardDf[LeaderboardDf['GWPoints']!=0]


    TotalGw = LeaderboardDf['GW'].max()
    H2Hweeklylist=[]


    for GW in range(1,TotalGw):


        A = LeaderboardDf[LeaderboardDf['GW']==GW]


        H2Hweekly = A.set_index('PlayerName')['H2Hpoints'].to_json()
        week = {"GameWeek":'GameWeek:'+str(GW)}
        intrdta = json.loads(H2Hweekly)
        intrdta.update(week)

        H2Hweeklylist.append((intrdta))


    return H2Hweeklylist

def createGWweekly(LeaderboardDf):


    LeaderboardDf = LeaderboardDf[LeaderboardDf['GWPoints']!=0]


    TotalGw = LeaderboardDf['GW'].max()
    GWWeeklylist=[]


    for GW in range(1,TotalGw):


        A = LeaderboardDf[LeaderboardDf['GW']==GW]


        GWWeekly = A.set_index('PlayerName')['GWPoints'].to_json()
        week = {"GameWeek":'GameWeek:'+str(GW)}
        intrdta = json.loads(GWWeekly)
        intrdta.update(week)

        GWWeeklylist.append((intrdta))


    return GWWeeklylist



@app.route('/')
def root():
    return render_template('Home.html')

@app.route('/fetchleaguedata',methods=['POST'])
def LeagueDatafetch():
    leagueid = request.form['leagueid']
    finalDataFrame = GetAndAppendAllToOneJson(leagueid)

    LeaderboardDf = createleaderboard(finalDataFrame)

    RankDf = creatRankBoard(LeaderboardDf)

    return render_template('Dataview.html', column_names=RankDf.columns.values, row_data=list(RankDf.values.tolist()), zip=zip,leagueid=leagueid )


@app.route('/WeeklyReport',methods=['POST'])
def WeeklyReport():
    leagueid = request.form['hdfleagueid']
    finalDataFrame = GetAndAppendAllToOneJson(leagueid)
    LeaderboardDf = createleaderboard(finalDataFrame)
    playerlist = LeaderboardDf['PlayerName'].unique()
    H2Hweekly = createH2Hweekly(LeaderboardDf)
    GWWeekly = createGWweekly(LeaderboardDf)
    #return render_template('Dataview.html', column_names=H2Hweekly.columns.values, row_data=list(H2Hweekly.values.tolist()), zip=zip,leagueid=leagueid )
    return render_template('test.html',H2Hweekly=H2Hweekly, GWWeekly = GWWeekly ,playerlist=playerlist.tolist())
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True,threaded=True)

    app.debug = True
    app.run()
