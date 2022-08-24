'''
This program takes the odds csv and combines it with the seasonal data
YOU SHOULD RUN THIS PROGRAM SECOND AFTER CsvStatsScraper.py
'''
import pandas as pd
import math

# turn off setting with copy warning
pd.set_option('mode.chained_assignment', None)


# every team and their abbreviations
teamsDict = {'ATL': 'AtlantaHawks', 'BRK': 'BrooklynNets', 'BOS': 'BostonCeltics',
             'CHA': 'CharlotteHornets', 'CHO': 'CharlotteHornets',
             'CHI': 'ChicagoBulls', 'CLE': 'ClevelandCavaliers',
             'DAL': 'DallasMavericks', 'DEN': 'DenverNuggets', 'DET': 'DetroitPistons',
             'GSW': 'GoldenStateWarriors', 'HOU': 'HoustonRockets', 'IND': 'IndianaPacers',
             'LAC': 'LosAngelesClippers', 'LAL': 'LosAngelesLakers', 'MEM' : 'MemphisGrizzlies',
             'MIA': 'MiamiHeat', 'MIL': 'MilwaukeeBucks', 'MIN': 'MinnesotaTimberwolves',
             'NJN': 'BrooklynNets', 'NOH': 'NewOrleansPelicans', 'NOP':'NewOrleansPelicans',
             'NYK': 'NewYorkKnicks', 'OKC': 'OklahomaCityThunder',
             'ORL': 'OrlandoMagic', 'PHI': 'Philadelphia76ers', 'PHO': 'PhoenixSuns',
             'POR': 'PortlandTrailBlazers', 'SAC': 'SacramentoKings', 'SAS': 'SanAntonioSpurs',
             'TOR': 'TorontoRaptors', 'UTA': 'UtahJazz', 'WAS': 'WashingtonWizards'}
# this function is called during add odds and cleans the odds df so its readable
def cleanOdds(odds):
    # cleaning up the dataset and making it readable
    del odds['Unnamed: 2']
    del odds['B\'s']

    odds.columns = ['Date', 'Teams', 'Score', 'HomeOdds', 'AwayOdds']
    del odds['Date']

    odds.dropna(inplace=True)
    odds.reset_index(drop=True, inplace=True)
    
    # just to clean the dataset
    for i in range(len(odds)):
        # get the teams playing
        teams = odds['Teams'].iloc[i]
        
        # clean the data so whitespace is removed
        teams = teams.replace(u'\xa0', u'')
        teams = teams.replace(' ', '')

        # string slicing to get home and away teams
        split = teams.find('-')
        homeTeam = teams[:split]
        awayTeam = teams[split+1:]
        # update the df with the cleaned string
        odds['Teams'].iloc[i] = homeTeam + '-' + awayTeam

        # cleaning the score data so it only contains the scores
        if odds['Score'].iloc[i][-2:] == "OT" or odds['Score'].iloc[i][-3:] == ":00":
            odds['Score'].iloc[i] = odds['Score'].iloc[i][:-3]
            
    return odds

# this function adds the odds to the seasonal data
def addOdds(y, odds, matches):
    odds = cleanOdds(odds)
        
    # sort matches by date
    matches.sort_values(['Date'],axis=0, inplace=True)
    matches = matches[::-1]
    matches.reset_index(drop=True, inplace=True)
    
    # get the teams odds and the opponents odds
    oddsArray = []
    opponentsOddsArray = []

    for m in range(len(matches)):
        # get the match info
        home = teamsDict[matches.loc[m, 'Team']]
        away = teamsDict[matches.loc[m, 'Opp']]
        homePoints = matches.loc[m, 'TM']
        awayPoints = matches.loc[m, 'OP']
        HoA = matches.loc[m, 'H/A']
        
        # in the matches dataset there is samples for both sides of the same game
        # this code ensures that we get the right odds for both sides of the sample
        
        # if its a home game
        if HoA == 'H':
            # match the teams playing and their scores
            game = odds.loc[(odds['Teams'] == home + '-' + away) &
                            (odds['Score'] == str(homePoints) + ':' + str(awayPoints))]
            if len(game) > 0:
                # append team and opponents odds
                oddsArray.append(game['HomeOdds'].values[0])
                opponentsOddsArray.append(game['AwayOdds'].values[0])
            else:
                oddsArray.append(math.nan)
                opponentsOddsArray.append(math.nan)
            
        # if its an away game
        elif HoA == 'A':
            # match the teams playing and their scores
            game = odds.loc[(odds['Teams'] == away + '-' + home) &
                            (odds['Score'] == str(awayPoints) + ':' + str(homePoints))]
            if len(game) > 0:
            # append team and opponents odds
                oddsArray.append(game['AwayOdds'].values[0])
                opponentsOddsArray.append(game['HomeOdds'].values[0])
            else:
                oddsArray.append(math.nan)
                opponentsOddsArray.append(math.nan)


    matches['TeamsOdds'] = oddsArray
    matches['OppOdds'] = opponentsOddsArray
    return matches
    
for y in range(2009, 2023):
    odds = pd.read_csv('C:\\AddYourFilePathHere' + str(y) + '.csv')    
    matches = pd.read_csv('C:\\AddYourFilePathHere'+str(y)+'_season.csv')
    matches  = addOdds(y, odds, matches)
    
    print('NaN values:',  matches['TeamsOdds'].isna().sum())
    matches.to_csv('C:\\AddYourFilePathHere' + str(y) + '_season_with_odds.csv', index=False)
    print(str(y) + ' Complete Adding Odds')
