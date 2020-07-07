import os
from math import ceil
import json
import time
from datetime import datetime
import random
import dill
import requests
from datetime import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
import google_auth_oauthlib
# import sqlite3
# conn = sqlite3.connect('/home/abdullah/Projects/islamic_webapp/site.db')
# c = conn.cursor()
# q='select id,f_name,l_name,email from users'
# rows = c.execute(q).fetchall()
# rows.insert(0, ("ID","First Name","Last Name","Email ID"))
# conn.close()

'''
doing some walkout with the google API
you will need a client_secrets or client_secrets_file
from the google API documentation
'''

import os

import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/spreadsheets"]


# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "sheets"
api_version = "v4"
client_secrets_file = "static/client_secret.json"
#api_key = os.environ.get('YOUTUBE_API_KEY')

#refresh_token = os.environ.get('REFRESH_TOKEN')

with open(client_secrets_file) as cs_file:
    client_secrets = json.load(cs_file)
    client_id=client_secrets['web']['client_id']
    client_secret=client_secrets['web']['client_secret']
    token_uri=client_secrets['web']['redirect_uris'][0]

base_token_url = 'https://accounts.google.com/o/oauth2/token'

def authorize():
    '''
    this function should be called once
    You will need curl to be able to do this
    '''
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file, scopes)
    flow.redirect_uri = 'http://127.0.0.1:5000/authorize'

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        login_hint='general14145@gmail.com',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    code=input(f'\nfollow link below to authorize:\n\n{authorization_url}\n\npaste the code here: ')
    
    '''
    Now after getting the authorization code from the user. 
    We need to ensure that our program is signed in permanently(ie. if the user doesn't revoke the authorization)
    To do that we need to exchange the authorization code for a token(ie. Access Token) and refresh token
        as the access token expires within an hour.
        therefore the Refresh token is the most important
    The below code will do the exchange and with save the response in 'static/resp.json'
    '''
    data={'code':f'{code}','client_id':f'{client_id}','client_secret':f'{client_secret}','redirect_uri':f'{flow.redirect_uri}','grant_type':'authorization_code'}
    resp=requests.post(base_token_url,data=data)
    json_resp=json.loads(resp.content)
    
    try:
        token = json_resp['refresh_token']
    except:
        print("Invalid authorization")
        return
    with open('static/resp.json','w') as f:
        json.dump(json_resp, f)
    return token

def get_refresh_token():
    try:
        with open('static/resp.json', 'r') as json_token:
            refresh_token = json.load(json_token)['refresh_token']
    except:
        print('There is no refresh token')
        print('running authorize() to get one')
        refresh_token=authorize()
    return refresh_token

def generate_token():
    '''
    #*this will generate a new access token everytime it is
 run from the refresh token
    the access token expires within an hour
    so a simple logic is implemented which will run this function everytime the program is executed
        this is done by saving the time it was run in a pickle file
        #*so everytime the program is run the time in the pickle file is checked against the current time
        if it is more than an hour this function is run again
        #*the checker is below the funtion
    '''
    refresh_token = get_refresh_token()
    data = {'client_id':f'{client_id}','client_secret':f'{client_secret}','refresh_token':f'{refresh_token}','grant_type':'refresh_token'}
    resp=requests.post(base_token_url,data=data)
    json_resp=json.loads(resp.content)
    
    try:
        token = json_resp['access_token']
    except:
        print("invalid_grant")
        return
    with open('static/token.json','w') as json_token:
        json.dump(json_resp, json_token)
    _credentials_={'token':token,'refresh_token':refresh_token,'token_uri':token_uri,'client_id':client_id,'client_secret':client_secret,'scopes':scopes}
    with open('static/credentials.json', 'w') as json_token:
        json.dump(_credentials_, json_token)
    with open('static/time.pkl', 'wb') as t:
        dill.dump(datetime.utcnow(), t)
    print('Generated a new access token')

def _generate_token_():
    '''
    this is the checker for the generate_token function as described in it.
    '''
    try:
        with open('static/time.pkl', 'rb') as t:
            time_pkl = dill.load(t)
    except:
        with open('static/time.pkl', 'wb') as t:
            dill.dump(datetime.utcnow(), t)
            generate_token()
    else:
        if (datetime.utcnow()-time_pkl).seconds/3600 >= 1:
            generate_token()
#_generate_token_()
def set_sheet_id(sheet_id):
    with open('static/sheet_id.json','w') as f:
        json.dump({'sheet_id':sheet_id},f)

def get_sheet_id():
    try:
        with open('static/sheet_id.json') as f:
            sheet_id=json.load(f)['sheet_id']
    except:
        sheet_id = None
        print('NO sheet sheet_id was set or no sheet was created')
        print('try running create sheet or set a sheet sheet_id by running get_sheet_id()')
    else:
        return sheet_id

def get_sheets():
    with open('static/credentials.json') as json_token:
        _credentials = json.load(json_token)
    credentials = google.oauth2.credentials.Credentials(**_credentials)
    # print(credentials)
    try:
        sheets = build(api_service_name, api_version, credentials=credentials)
    except:
        print("Please check your network connection")
    else:
        return sheets
    print("Error")

def create_sheet(title=None):
    sheets = get_sheets()
    if not title:
        title=f'G-API -- {datetime.utcnow().strftime("%Y/%B/%A  %I:%M:%S %p")}'
    data={'properties':{'title': title}}
    res=sheets.spreadsheets().create(body=data).execute()
    sheet_id = res['spreadsheetId']
    set_sheet_id(sheet_id)
    print(f'Created {res["properties"]["title"]} with ID: {sheet_id}')
    return sheet_id

if not get_sheet_id():
    i=input('Do you want to create a new sheet - input any-key(for yes) or n(for no): ')
    if i!='n':
        t=input('Please input a sheet title: ')
        create_sheet(t)
    else:
        si=input('Please input a sheet id: ')
        set_sheet_id(si)

def update_sheet(data_list,range="A1",value_type='RAW',sheet_id=None):
    sheets = get_sheets()
    if type(data_list) == list or type(data_list) == tuple:
        if type(data_list[0]) == list or type(data_list[0]) == tuple:
            data={'values': [tuple(row) for row in data_list]}
        else:
            data={'values': [tuple(data_list)]}
    else:
        print('Error')
        return None
    if not sheet_id:
        sheet_id = get_sheet_id()
    res=sheets.spreadsheets().values().update(spreadsheetId=sheet_id,range=range,valueInputOption=value_type,body=data).execute()
    print(f'Updated ID: {sheet_id} as {value_type}')
    return res

def batch_update_sheet(data=None,sheet_id=None):
    sheets = get_sheets()
    if not data:
        with open('static/batch_update.json') as bu:
            data = json.load(bu)
    if not sheet_id:
        sheet_id = get_sheet_id()
    res=sheets.spreadsheets().batchUpdate(spreadsheetId=sheet_id,body=data).execute()

def append_sheet(data_list,sheet_id=None,range="A1",value_type='RAW'):
    sheets = get_sheets()
    if type(data_list) == list or type(data_list) == tuple:
        if type(data_list[0]) == list or type(data_list[0]) == tuple:
            data={'values': [tuple(row) for row in data_list]}
        else:
            data={'values': [tuple(data_list)]}
    else:
        print('Error')
        return None
    if not sheet_id:
        sheet_id = get_sheet_id()
    res=sheets.spreadsheets().values().append(spreadsheetId=sheet_id,range=range,valueInputOption=value_type,body=data).execute()
    print(f'Appended ID: {sheet_id} as {value_type}')
    return res

def print_sheet(range='A1',sheet_id=None):
    sheets = get_sheets()
    if not sheet_id:
        sheet_id = get_sheet_id()
    sheet = sheets.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,range=range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    return values