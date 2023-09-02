#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:40:17 2017

@author: claudiahertzog
"""
import sys
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import numpy as np
import os
import pandas as pd
import argparse
import seaborn as sns 
import plotly.express as px

primarySpecies = list(np.sort(['CARP', 'TIL','TIL-r','CAT','LMB', 'HSB','HSB-FRESH']))

endDate = '2023-09-01'

#inputPath = '/Volumes/GoogleDrive/My Drive/KentSeaTech'
inputPath = '/Users/claudiahertzog/Documents/KentSeaTech'
summaryRevenue = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','weeklyRevenue_'+endDate+'.csv'),index_col=[0,1],parse_dates=True)
summaryHauler = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','weeklyVolumes_'+endDate+'.csv'),index_col=[0,1],parse_dates=True)
haulerTargets = pd.read_csv(os.path.join(inputPath,'FSRinputData','haulerTargets.csv'),index_col=0)

haulerTargets.replace(0,np.nan,inplace=True)

try:
    acDF = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','weeklyReceivables_'+endDate+'.csv'),index_col=0)
except FileNotFoundError:
    print('\nPlease download most recent recievables and sales from quickbooks\n')
    sys.exit()

summaryDirect = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','weeklyDirectRevenue_'+endDate+'.csv'),index_col=[0,1],parse_dates=True)
summaryDirect.dropna(subset=['SOLD $ AMT'],inplace=True)

summaryHauler['Total'] = summaryHauler.sum(axis=1)

summaryHauler = np.round(summaryHauler,0)

fileTimestamp = pd.to_datetime('today').strftime("%B %d, %Y")

targetThresh = summaryHauler.CARP.unstack()
targetThresh = targetThresh.loc[targetThresh.index >= pd.to_datetime('2017-11-17'),:]
    
    
def multiWeekTable(inputDF):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    
    nWeeks = 4
    
    df = inputDF.loc[inputDF.index.levels[0][-nWeeks:]].dropna(how='all',axis=1).copy()
    
    dfString = df.applymap('{:,g}'.format).copy()
    dfString[dfString == 'nan'] = ''
    
    columnSortOrder = df.columns.sort_values()[:-1].tolist()
    
    #speciesPlusTotal = df[primarySpecies].columns.tolist() + ['Total']
    speciesPlusTotal = df[columnSortOrder].columns.tolist() + ['Total']
    headerRow = [html.Td([]),html.Td([])]
    for eachSpecies in speciesPlusTotal:
        headerRow.append(html.Td([eachSpecies], style={"paddingLeft":"20px",'text-align': "right",'fontWeight': "bold"}))
    headerRow = [html.Tr(headerRow)]
    
    targetRow = [html.Td([],style={'text-align': "right",'fontStyle': "italic",'border-bottom': '1px solid'}),html.Td(['target lbs.'],style={'text-align': "right",'fontStyle': "italic",'border-bottom': '1px solid'})]
    #for eachSpecies in df[primarySpecies].columns:
    for eachSpecies in df[columnSortOrder].columns:
        try:
            appendVal = ["{:,g}".format(targetLbs[eachSpecies])]
        except:
            appendVal = [''] 
        appendText = html.Td(appendVal, style={'text-align': "right",'fontStyle': "italic",'border-bottom': '1px solid'})
        targetRow.append(appendText)
    targetRow.append(html.Td([],style={'text-align': "right",'fontStyle': "italic",'border-bottom': '1px solid'}))
    targetRow = [html.Tr(targetRow)]
    
    table = []
    for index in df.index.levels[0][-nWeeks:]:
        tempDF = dfString.loc[index,speciesPlusTotal].reset_index().copy()
        totalTemp = df.loc[index,speciesPlusTotal].sum().map('{:,g}'.format).replace('0','')
        
        for i,row in tempDF.iterrows():
            html_row = []
            if i == 0:
                html_row.append(html.Td([index.strftime('%m-%d-%Y')]))                
            else:
                html_row.append(html.Td([]))
            
            for j in range(len(row)):
                if i==tempDF.index[-1]:
                    html_row.append(html.Td([row[j]],style={'text-align': "right","paddingLeft":"20px",'border-bottom': '1px solid'}))
                else:
                    html_row.append(html.Td([row[j]],style={'text-align': "right","paddingLeft":"20px"}))
               
            table.append(html.Tr(html_row))
        
        totalRow = [html.Td([],style={'border-bottom': '1px solid'}),html.Td(['Total'],style={'text-align': "right",'border-bottom': '1px solid','fontWeight': "bold"})]
        for j in totalTemp:
            totalRow.append(html.Td([j],style={'text-align': "right",'border-top': '1px solid','border-bottom': '1px solid','fontWeight': "bold"}))
          
        table.append(html.Tr(totalRow))
        
    return headerRow+targetRow+table

def haulerTargetTable(df):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    #print('step3')  
    dfHeader = df.columns.tolist()
    secondHeader = ['Target' if  '' == eachCol else 'Actual' for eachCol in dfHeader]
    secondHeader[0] = ''
    
    headerRow = [html.Td([])]
    for eachSpecies in [eachS for eachS in dfHeader if eachS != '']:
        headerRow.append(html.Td([eachSpecies], colSpan=2, style={"paddingLeft":"20px",'text-align': "center",'fontWeight': "bold"}))
    
    header2 = [html.Td(col, style={"paddingLeft":"3px","paddingRight":"7px",'text-align': "right",'border-bottom': '1px solid'}) for col in secondHeader]
    
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            
            if i%2 == 0:
                  
                if index == df.shape[0] - 2:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'border-bottom': '1px solid','borderRight': 'thin darkgrey solid'}))
                elif index == df.shape[0] - 1:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'fontWeight': "bold",'borderRight': 'thin darkgrey solid'}))
                else:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid'}))
            else:
                if index == df.shape[0] - 2:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px",'text-align': "right",'border-bottom': '1px solid'}))
                elif index == df.shape[0] - 1:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px",'text-align': "right",'fontWeight': "bold"}))
                else:
                    html_row.append(html.Td([row[i]], style={"paddingLeft":"20px",'text-align': "right"}))
                
        table.append(html.Tr(html_row))
    return [html.Tr(headerRow)] + [html.Tr(header2)] + table

def receivablesTable(df):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    
    #colNames = ['Current', '1 - 7', '8 - 14', '15 - 21', '22 - 28', '29 - 30', '> 30','TOTAL']
    colNames = df.columns
    
    df.loc['Total']= df.sum()
    df = df.fillna(0).astype(int)
    
    dfString = df.applymap('{:,g}'.format).copy()
    dfString[dfString == 'nan'] = ''
    
    dfString.replace('0','',inplace=True)
    
    headerRow = [html.Td([], style={'border-bottom': '1px solid'})]
    for eachCol in colNames:
        headerRow.append(html.Td([eachCol], style={"paddingLeft":"20px",'text-align': "center",'fontWeight': "bold",'border-bottom': '1px solid'}))
    
    table = []
    for index, row in dfString.iterrows():
        if index == df.index[-2]:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid','border-bottom': '1px solid'})]
        elif index == df.index[-1]:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid','fontWeight': "bold"})]
        else:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid'})]
        
        for i in range(len(row)):
            if index == df.index[-2]:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'border-bottom': '1px solid'}))
            elif index == df.index[-1]:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'fontWeight': "bold"}))
            else:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right"}))
        table.append(html.Tr(html_row))
    
    return [html.Tr(headerRow)] + table

def revenueTable(df):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    
    intList = ['GROSS LBS','NET LBS','PAID']
    colNames = ['GROSS LBS', 'NET LBS', 'SIZE', 'TOTAL $', '$/LB']
    df[intList] = df[intList].astype(int)
    
    dfString = df.applymap('{:,g}'.format).copy()
    dfString[dfString == 'nan'] = ''
    dfString.SIZE = df.SIZE.map('{:.2f}'.format)  
    dfString.PPLB = df.PPLB.map('{:.2f}'.format)   
    
    headerRow = [html.Td([], style={'border-bottom': '1px solid'})]
    for eachCol in colNames:
        headerRow.append(html.Td([eachCol], style={"paddingLeft":"20px",'text-align': "center",'fontWeight': "bold",'border-bottom': '1px solid'}))
    
    table = []
    for index, row in dfString.iterrows():
        if index == df.index[-1]:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid','border-bottom': '1px solid'})]
        else:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid'})]
        
        for i in range(len(row)):
            if index == df.index[-1]:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'border-bottom': '1px solid'}))
            else:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right"}))
        table.append(html.Tr(html_row))
    
    totalTemp = df.sum().map('{:,g}'.format).replace('0','')
    totalTemp.SIZE = '{:.2f}'.format((df.SIZE * df['GROSS LBS']).sum()/df['GROSS LBS'].sum())
    totalTemp.PPLB = ''
    
    totalRow = [html.Td(['Total'],style={"paddingRight":"7px",'text-align': "right",'border-top': '1px solid','fontWeight': "bold",'borderRight': 'thin darkgrey solid'})]
    for j in totalTemp:
        totalRow.append(html.Td([j],style={"paddingRight":"7px",'text-align': "right",'border-top': '1px solid','fontWeight': "bold"}))  
    table.append(html.Tr(totalRow))

    return [html.Tr(headerRow)] + table

def revenueDirectTable(df):
    ''' Return a dash definitio of an HTML table for a Pandas dataframe '''
    
    df['MISSING $'] = -df['MISSING $']
    
    intList = ['HARVEST NET LBS','SOLD LBS','REVENUE P&L','MISSING QTY LBS','MISSING $']
    colNames = ['HARVEST LBS', 'SOLD LBS', 'MISSING LBS','REVENUE, NET', 'MISSING $ ','MISSING %','$/LB']
    colOrder = ['HARVEST NET LBS', 'SOLD LBS', 'MISSING QTY LBS', 'REVENUE P&L', 'MISSING $', 'MISSING %','PPLB']
    missingPercentTotal = df.sum()['MISSING $']/(-df.sum()['MISSING $']+ df.sum()['SOLD $ AMT'])
    df = df[colOrder]
    
    df[intList] = df[intList].astype(int)
    
    dfString = df.applymap('{:,g}'.format).copy()
    dfString[dfString == 'nan'] = ''
    dfString.PPLB = df.PPLB.map('${:.2f}'.format)   
    dfString['MISSING %'] = (-100*df['MISSING %']).map('{:.1f}%'.format)  
     
    headerRow = [html.Td([], style={'border-bottom': '1px solid'})]
    for eachCol in colNames:
        headerRow.append(html.Td([eachCol], style={"paddingLeft":"20px",'text-align': "center",'fontWeight': "bold",'border-bottom': '1px solid'}))
    
    table = []
    for index, row in dfString.iterrows():
        if index == df.index[-1]:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid','border-bottom': '1px solid'})]
        else:
            html_row = [html.Td([index], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'borderRight': 'thin darkgrey solid'})]
        
        for i in range(len(row)):
            if index == df.index[-1]:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right",'border-bottom': '1px solid'}))
            else:
                html_row.append(html.Td([row[i]], style={"paddingLeft":"20px","paddingRight":"7px",'text-align': "right"}))
        table.append(html.Tr(html_row))
    
    totalTemp = df.sum().map('{:,g}'.format).replace('0','')
    totalTemp.PPLB = '${:.2f}'.format(df.sum()['REVENUE P&L']/df.sum()['HARVEST NET LBS'])
    totalTemp['MISSING %'] = '{:.1f}%'.format(100*missingPercentTotal)
    
    totalRow = [html.Td(['Total'],style={"paddingRight":"7px",'text-align': "right",'border-top': '1px solid','fontWeight': "bold",'borderRight': 'thin darkgrey solid'})]
    for j in totalTemp:
        totalRow.append(html.Td([j],style={"paddingRight":"7px",'text-align': "right",'border-top': '1px solid','fontWeight': "bold"}))  
    table.append(html.Tr(totalRow))

    return [html.Tr(headerRow)] + table

def valid_date(s):
    try:
        return pd.to_datetime(s)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

colors = ['rgb(0,107,164)','rgb(255,128,14)','rgb(171,171,171)','rgb(89,89,89)',
          'rgb(95,158,209)', 'rgb(200,82,0)','rgb(137,137,137)','rgb(162,200,236)',
          'rgb(255,188,121)','rgb(207,207,207)','rgb(204,121,167)']
            

haulerColors = dict(zip(summaryHauler.index.levels[1], colors))
targetLbs = haulerTargets.sum()
    
formattedSummary = summaryHauler.loc[summaryHauler.index.levels[0][-1]][primarySpecies + ['Total']].copy()
#formattedSummary.dropna(how='all',axis=1,inplace=True)

noPickUps = [eachHauler for eachHauler in haulerTargets.index if eachHauler not in formattedSummary.index]

formattedSummary = pd.concat([formattedSummary,pd.DataFrame(index=noPickUps)])

newCol = pd.DataFrame(columns=[eachSpecies + ' target' for eachSpecies in formattedSummary.columns])
formattedSummary = formattedSummary.join(newCol,how='outer')

haulerTargets_copy = haulerTargets.copy()
haulerTargets_copy.columns = [eachSpecies + ' target' for eachSpecies in haulerTargets.columns]
haulerTargets_copy['Total target'] = haulerTargets_copy.sum(axis=1)
formattedSummary[haulerTargets_copy.columns] = haulerTargets_copy

speciesList = [eachSpecies[0] for eachSpecies in haulerTargets_copy.columns.sort_values().str.split(' ')]

formattedSummary = formattedSummary[speciesList + list(haulerTargets_copy.columns)]
#formattedSummary.dropna(how='all',axis=1,inplace=True)

formattedSummary = formattedSummary.append(pd.Series(formattedSummary.sum(),name='Total'))
formattedSummary.sort_index(axis=1,inplace=True)


formattedSummary.columns = ['' if 'target' in eachCol else eachCol for eachCol in formattedSummary.columns]
formattedSummary = formattedSummary.applymap('{:,g}'.format)
formattedSummary[formattedSummary == 'nan'] = ''

formattedSummary.reset_index(inplace=True)
formattedSummary.columns.values[0] = ''

weeklyRev = summaryRevenue.loc[summaryRevenue.index.levels[0][-1],:].copy()

rcvHtmlString = []
for eachType in acDF.customerType.unique():
    rcvHtmlString.append(html.H5(eachType))
    rcvHtmlString.append(html.Table(receivablesTable(acDF.loc[acDF.customerType == eachType,acDF.columns[:-1]])))
    rcvHtmlString.append(html.Br())
    
#stupid bug keeps the last index even if its not there
lastDate = summaryDirect.index.tolist()[-1][0]
weeklyDirectRev = summaryDirect.loc[lastDate,:].copy()

meanLiveSpec = [eachSpecies for eachSpecies in weeklyRev.index if eachSpecies != 'HSB-FRESH']
meanFreshSpec = [eachSpecies for eachSpecies in weeklyRev.index if eachSpecies == 'HSB-FRESH']

meanLive = (weeklyRev.loc[meanLiveSpec,'PPLB'] * weeklyRev.loc[meanLiveSpec,'GROSS LBS']).sum()/weeklyRev.loc[meanLiveSpec,'GROSS LBS'].sum()

if meanFreshSpec != []:
    try:
        meanFresh = '{:.2f}'.format((weeklyRev.loc[meanFreshSpec,'PPLB'] * weeklyRev.loc[meanFreshSpec,'GROSS LBS']).sum()/weeklyRev.loc[meanFreshSpec,'GROSS LBS'].sum())
    except:
        meanFresh = ' --'
else:
    meanFresh = ' --'

speciesColors = dict(zip(primarySpecies + ['BLUE','Total'], colors))

#haulerStats = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','haulerStats.csv'),index_col=[0,1])

nWeekCount = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','haulerCountScore.csv'),index_col=0)

avgOut = pd.read_csv(os.path.join(inputPath,'FSRinputData','output','salesResults','haulerVolScore.csv'),index_col=0)
haulerOrderTemp = ['KST','MTN SFD','LE FISH', 'FRESHCO', 'SEA TAK','CRAB HOUSE','NAUTILUS','GLOBAL NATURE', 'CRAB HOUSE','TAWA']
speciesOrder = ['LMB', 'TIL','CAT','CARP',  'HSB', 'HSB-FRESH']

haulerOrder = [eachHauler for eachHauler in haulerOrderTemp if eachHauler in haulerTargets.index]

figA = px.imshow(avgOut.loc[haulerOrder,speciesOrder],color_continuous_scale='Blues',zmin=0,zmax=1,aspect='auto',text_auto='.1f')
figA.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})

figB = px.imshow(nWeekCount.loc[haulerOrder,speciesOrder],color_continuous_scale='Blues',zmin=0,zmax=3,text_auto='i',aspect='auto')
figB.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})

#figC = px.imshow(haulerStats.LMB.unstack().dropna(how='all',axis=1).T,color_continuous_scale='Blues',width=800,height=300,zmin=0,zmax=1,text_auto='.1f')
#figC.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})


fig2 = px.line(summaryRevenue.PAID.unstack()[haulerTargets.columns].fillna(0).rolling(2).mean().replace(0,np.nan).tail(156),color_discrete_map=speciesColors)
fig2.update_layout(xaxis_title="",yaxis_title="Weekly Revenue ($)")
fig2.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})

fig3 = px.line(summaryDirect['REVENUE P&L'].unstack()[['CAT', 'LMB', 'TIL', 'HSB', 'CARP']].fillna(0).rolling(3).mean().replace(0,np.nan).tail(156),color_discrete_map=speciesColors)
fig3.update_layout(xaxis_title="",yaxis_title="Weekly Revenue ($)")
fig3.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})


app = dash.Dash(__name__)
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')
#"http://kentseatech.tuuli.co/files/2016/08/Kenttesch-logo-retina.png"
app.layout = html.Div([
    html.Div([
        html.H3('Kent SeaTech Sales Report - '+fileTimestamp,
                style={'display': 'inline',
                       'float': 'left',
                       'margin-left': '7px',
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }
                ),
        html.Img(src="http://kentseatech.com/wp-content/uploads/2016/08/Kenttesch-logo-retina.png",
                style={
                    'margin-top': '20px',
                    'height': '100px',
                    'float': 'right'
                },
        ),
    ],style={'width': '100%'}),
    html.Div([
            html.H4("Hauler Volumes - Actual vs Target "),
            html.Table(haulerTargetTable(formattedSummary))
       ], style={'padding-top': '60px','align': "center",'width': '110%'}),
    html.Div([
            html.H4("Direct Sales Revenue"),
            html.Table(revenueDirectTable(weeklyDirectRev)),html.Br()
        ], style={'padding-top': '0px','align': "center"}),
    html.Div([
            html.H4("Weekly Revenue by Species"),
            html.Table(revenueTable(weeklyRev)),html.Br(),
            html.H6("Weekly average $/lb (live sales): $" + '{:.2f}'.format(meanLive)),
            html.H6("Weekly average $/lb (fresh sales): $" + meanFresh),html.Br()
        ], style={'padding-top': '0px','align': "center"}),
    
    html.Div([
        html.H4("Hauler Scorecard"), 
        html.Div([
            html.Div([
                html.H5("3-week average volume (% of target)",style={ 'textAlign': 'center'}),
                dcc.Graph(id='g1', figure=figA)
            ], className="six columns"),
    
            html.Div([
                html.H5("Total number of pickups in 3 weeks",style={ 'textAlign': 'center'}), 
                dcc.Graph(id='g2', figure=figB)
            ], className="six columns"),
        ], className="row")
    ], style={'padding-top': '0px','align': "center"}),
    
    #html.Div([
    #        html.H4("Hauler Scorecard"),
    #        dcc.Graph(id='example-graphC', figure=figC)
    #    ], style={'padding-top': '0px','align': "center"}),
    
    html.Div([
            html.H4("Total Revenue by Species"),
            dcc.Graph(id='example-graph', figure=fig2)
        ], style={'padding-top': '0px','align': "center"}),
    
    html.Div([
            html.H4("Total Direct Revenue"),
            dcc.Graph(id='direct-graph',figure=fig3)
        ], style={'padding-top': '0px','align': "center"}),
    
    html.Div([
            html.H4("Receivables by Customer"),
            html.Div(rcvHtmlString),
            #html.Table(receivablesTable(acDF)),html.Br(),
            ], style={'padding-top': '0px','align': "center",'width': '110%'}),
    html.Div([
            html.H4("Four-Week Volume Totals"),
            html.Table(multiWeekTable(summaryHauler))
        ], style={'padding-top': '0px','align': "center"}),
    html.Div([
            html.H4("Select species to plot by week")
        ], style={'padding-top': '20px','align': "center"}),                
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s,'value': s} for s in primarySpecies],
        value=['LMB', 'HSB','HSB-FRESH','TIL','CAT','CARP'],
        multi=True
    ),
    html.Div(id='graphs')
], className="container")


@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []
    for i, ticker in enumerate(tickers):
        try:
            fig4 = px.bar(summaryHauler[ticker].unstack()[-20:].dropna(how='all',axis=1),
                          color_discrete_map=haulerColors,title="Automatic",width=900,height=400)
            fig4.update_layout(
                #title=ticker,
                xaxis_title="Week Ending",
                yaxis_title="Pounds Sold",
                legend_title="",
                title={
                    'text': ticker,
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'bottom'})
            fig4.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)'})
            fig4.update_layout(shapes=
                  [dict(type= 'line',
                        yref= 'y', y0= targetLbs[ticker], y1= targetLbs[ticker],
                        xref= 'x', x0=summaryHauler.index.levels[0][-20], x1=summaryHauler.index.levels[0][-1],
                        line=dict(color="darkgrey",
                                  width=2,
                                  dash="dash")
                        )])
            #fig4.add_trace(go.Scatter.line(
            #    x=[0, summaryHauler.index.levels[0][-1]],
            #    y=[targetLbs[ticker], targetLbs[ticker]]))

        except:
            graphs.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue
        graphs.append(dcc.Graph(
            id=ticker,
            figure=fig4))

    return graphs


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Work+Sans",
                "https://bootswatch.com/3/paper/bootstrap.css"]

# defaults to look locally so turn this off if I actually have the files locally)
app.css.config.serve_locally = False

for css in external_css:
    app.css.append_css({"external_url": css})
    
if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read latest sales report and create bar plots and csv summaries')   
    parser.add_argument('-e', "--endDate", help="The last date to include (should be a friday) - format YYYY-MM-DD ", 
                    required=True, type=valid_date)
    #parser.add_argument('-y', "--summaryYear", help="List of summary years to include, if different from the timestamp")
    #parser.add_argument('-m', "--missingFish", help="Flag to subtract missing fish from total", 
    #                action='store_true')
    
    #parser.add_argument('--foo', action='store_const', const=42)
    
    args = parser.parse_args()

    endDate = args.endDate
    
    
    #outputYears = args.summaryYear
    #includeMissing = args.missingFish
    #if outputYears:
    #    print(outputYears)
    #else:
    #    outputYears = timeIn.year
    print('Printing sales information as of ',endDate)  
    
    app.run_server(debug=True)
    
    
