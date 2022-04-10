import pandas as pd
import numpy as np
import os

# turn off SettingWithCopyWarning
pd.set_option('mode.chained_assignment', None)

# CHANGE TO THE FILEPATH OF YOUR ORIGINAL DATA FILE
cd = '../Data'

# how many of their previous games should we lookback on?
lookback = 12

finalData = []
for y in range(2013, 2023):
    df = pd.read_csv(cd + str(y) + '_season_with_odds.csv')
    df.sort_values(['Date', 'Team'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    """
    df.drop(['TM','OP','ORtg', 'DRtg','Pace','FTr','3PAr', 'TS%','TRB%','AST%',
             'STL%','BLK%','eFG%','TOV%','ORB%','FT/FGA',
             'OeFG%','OTOV%','ODRB%','OFT/FGA'], axis=1, inplace=True)
             """
    # binary encode features
    df.replace({'H/A':{"H":0, "A":1}, 'W/L':{"W":0, "L":1}}, inplace=True)

    # FOR each team in the season
    for t in df['Team'].unique():
        currentTeam = df[df['Team'] == t]
        currentTeam.reset_index(drop=True, inplace=True)
        
        # FOR each game in the teams season
        for g in range(len(currentTeam)):

            # IF the amount of games theyve played that season exceeds N lookback start gaining data
            # add 10 because the first 10 matches in the season dont provide good data
            if g >= (lookback + 20):
                # get the up coming match
                nextMatch = currentTeam[currentTeam['G'] == g+1]
                
                # get the previous N lookback matches
                prevMatch = currentTeam.loc[currentTeam['Date'] < nextMatch['Date'].values[0]]
                prevMatch = prevMatch.tail(lookback)

                # get the opponents last N lookback games
                oppPrev = df[df['Team'] == nextMatch['Opp'].values[0]]         
                oppPrev = oppPrev.loc[oppPrev['Date'] < nextMatch['Date'].values[0]]
                oppPrev = oppPrev.tail(lookback)

                HoA = nextMatch['H/A']
                teamOdds = nextMatch['TeamsOdds']
                oppOdds = nextMatch['OppOdds']
                label = nextMatch['W/L']

                # drop columns we wont use anymore
                prevMatch.drop(['G','Date', 'Team', 'Opp'], axis=1,inplace=True)
                oppPrev.drop(['G','Date', 'Team', 'Opp'], axis=1, inplace=True)
                
                # convert to normal array because numpy arrays are slow to append to
                prevMatch = prevMatch.values.flatten().tolist()
                oppPrev = oppPrev.values.flatten().tolist()
                HoA = HoA.values.flatten().tolist()
                teamOdds = teamOdds.values.flatten().tolist()
                oppOdds = oppOdds.values.flatten().tolist()

                label = label.values.flatten().tolist()
                
                sample = prevMatch + oppPrev + HoA + teamOdds + oppOdds + label
                finalData.append(np.asarray(sample))
                
    print(y, '- complete')

# save the finalised data 
finalData = np.asarray(finalData)

# CHANGE FILEPATH TO THE LOCATION THAT YOU WANT YOUR FINALISED DATA TO BE 
np.save('./split_' + str(lookback) + ')', finalData)
