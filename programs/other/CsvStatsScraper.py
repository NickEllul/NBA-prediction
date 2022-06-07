'''
This program scrapes the basketball-reference website
and creates seasonal data for it
YOU SHOULD RUN THIS FIRST
'''
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import os

# add url of the website and current working directory
url = 'https://www.basketball-reference.com/teams/'
cd = ""

# to scrape the basketball website for its data
def tableScraper(soup, team):
    # find the relevant table and scrape it from the site
    data = []
    table = soup.find('table')
    tableBody = table.find('tbody')

    rows = tableBody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols])

    # create the dataframe and its column names
    df = pd.DataFrame(data)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df.drop(columns=17)
    df = df.drop(columns=22)

    df.columns = ['G', 'Date', 'H/A', 'Opp', 'W/L','TM','OP','ORtg',
                  'DRtg','Pace','FTr','3PAr', 'TS%','TRB%','AST%',
                  'STL%','BLK%','eFG%','TOV%','ORB%','FT/FGA',
                  'OeFG%','OTOV%','ODRB%','OFT/FGA']

    # the websites table shows @ as away games
    for i in range(len(df)):
        if df['H/A'][i] == '@':
                df['H/A'][i] = 'A'
        else:
                df['H/A'][i] = 'H'
    df.insert(2, 'Team', team)

    return df

# generate the teams win loss ratio
def generateWinLoss(df):
    winLossRatio = []    
    # FOR the team in that season generate the W/L ratio
    for t in df['Team'].unique():
        
        # GET the current team were working with
        currentTeam = df[df['Team'] == t]
        currentTeam.reset_index(drop=True, inplace=True)

        # COUNT the wins and losses
        wins = 0
        losses = 0
        
        # the ratio should be one behind because the current match hasnt been played yet
        # so add 0 at the beggining for each team
        
        # FOR each match
        for m in range(len(currentTeam)):
            # CHECK if its a win or a loss and add it to the count
            if currentTeam['W/L'].loc[m] == 'W':
                wins += 1
            elif currentTeam['W/L'].loc[m] == 'L':
                losses += 1
            
            # Zero division error handling
            if losses == 0:
                winLossRatio.append(wins)
            else:
                winLossRatio.append((wins/losses))
        
                
    # Generate a new column for the W/L ratio 
    df['W/L_Ratio'] = winLossRatio
    return df

# Generate the opponents win loss ratio
def generateOppWL(df):
    oppWLratio = []
    # FOR the team in that season generate the W/L ratio
    for t in df['Team'].unique():
        
        # GET the current team were working with
        currentTeam = df[df['Team'] == t]
        currentTeam.reset_index(drop=True, inplace=True)
        
        # FOR each match
        for m in range(len(currentTeam)):
            
            # GET the opponent and the date
            opp = currentTeam.loc[m, 'Opp']
            date = currentTeam.loc[m, 'Date']

            oppWL = df.loc[(df['Team'] == opp) & (df['Date'] <= date)]
            # if they havent played a match yet just append 0
            if len(oppWL) == 0:
                oppWLratio.append(0)
            else:
                oppWLratio.append(oppWL['W/L_Ratio'].tail(1).values[0])

    df['Opp_W/L_ratio'] = oppWLratio
    return df            

for y in range(1990, 2023):
    # clear the data frame for each new year
    df = pd.DataFrame()

    # little bit hacky but we know that atlanta has had a team since
    # the beginning of the NBA
    teams = ['ATL']
    t = 0
    
    while t < len(teams):
        # scrape all teams in the leauge
        webpage = url + teams[t] + '/' + str(y) + '/gamelog-advanced/'
        html = requests.get(webpage).text
        soup = BeautifulSoup(html, 'lxml')

        # append the new teams df to the seasonal df
        df = pd.concat([df , tableScraper(soup, teams[t])])
        
        # crawler to get every team in the season
        for i in df['Opp'].unique():
            if i not in teams:
                teams.append(i)
        t += 1
        
    # generating the win loss ratio of the teams and their opponents
    # sorting the array by team and then date
    df.sort_values(by=['Team', 'Date'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # GET win loss for the teams and opponents
    df = generateWinLoss(df)
    df = generateOppWL(df)
    
    # save csv
    df.to_csv(cd + str(y) + '_season' + '.csv', index=False)
    print(str(y) + " - Complete")
