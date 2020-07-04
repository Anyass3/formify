import os
from math import ceil
import json
import time
import random
import dill
from datetime import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
import google_auth_oauthlib

'''
doing some walkout with the google API
you will need a client_secrets or client_secrets_file
from the google API documentation
'''

# -*- coding: utf-8 -*-
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
try:
    with open('static/credentials.json', 'r') as json_token:
        refresh_token = json.load(json_token)['refresh_token']
except:
    pass
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
    flow.redirect_uri = 'http://127.0.0.1:5000/'

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
    resp=f'code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={flow.redirect_uri}&grant_type=authorization_code'
    p=f'''
    curl \\
    --request POST \\
    --data "{resp}" \\
    {base_token_url} > static/resp.json
    '''
    os.system(p)

def generate_token():
    '''
    #*this will generate a new access token everytime it is run from the refresh token
    the access token expires within an hour
    so a simple logic is implemented which will run this function everytime the program is executed
        this is done by saving the time it was run in a pickle file
        #*so everytime the program is run the time in the pickle file is checked against the current time
        if it is more than an hour this function is run again
        #*the checker is below the funtion
    '''
    resp=f'client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}&grant_type=refresh_token'
    p=f'''
    curl \\
    --request POST \\
    --data "{resp}" \\
    {base_token_url} > static/token.json
    '''
    os.system(p)
    with open('static/token.json') as json_token:
        try:
            token = json.load(json_token)['access_token']
        except:
            print("invalid_grant")
            return
    with open('static/credentials.json', 'r') as json_token:
        _credentials_ = json.load(json_token)
        _credentials_['token'] = token
        _credentials_['refresh_token'] = refresh_token
        _credentials_['token_uri'] = token_uri
        _credentials_['client_id'] = client_id
        _credentials_['client_secret'] = client_secret
        _credentials_['scopes'] = scopes
    with open('static/credentials.json', 'w') as json_token:
        json.dump(_credentials_, json_token)
    with open('static/time.pkl', 'wb') as t:
        dill.dump(datetime.utcnow(), t)
def _generate_token_():
    '''
    this is the checker for the generate_token function as described in it.
    '''
    with open('static/time.pkl', 'rb') as t:
        time_pkl = dill.load(t)
    if time_pkl:
        if (datetime.utcnow()-time_pkl).seconds/3600 >= 1:
            generate_token()

#_generate_token_()
try:
    with open('static/credentials.json') as json_token:
        _credentials = json.load(json_token)

    credentials = google.oauth2.credentials.Credentials(**_credentials)
    #print(credentials)
    sheets = build(api_service_name, api_version, credentials=credentials)
except:
    pass