# -*- coding: utf-8 -*-
"""
@author: gianc
"""
#Step 1: Turn on the YouTube Data API
# https://developers.google.com/youtube/v3/quickstart/go

import os
import json
import pandas as pd
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
import pickle
import algorand as algorand

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
# You need downloading the file YOUR_CLIENT_SECRET_FILE.json from your Google developer account page
client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
#your API KEY 
#https://developers.google.com/youtube/v3/quickstart/python
#Use this key in your application by passing it with the key=API_KEY parameter.
KEY = "YOUR KEY"

df_cols_sub = ['subtitle','iduser','idchannel','description']
rows_sub = []
def main():

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    youtube_subscribers = get_authenticated_service()
    youtube = build(api_service_name,api_version, developerKey=KEY)
    
    
    request_mysubscribers = youtube_subscribers.subscriptions().list(
        part="subscriberSnippet",
        maxResults=50,
        mySubscribers=True
    
    )
          
    response_mysubscribers = request_mysubscribers.execute()
    response_mysubscribers_json = json.dumps(response_mysubscribers)
    json_load_mysubscribers = json.loads(response_mysubscribers_json)
    with open('mysubscribers.json', "w") as outfile:
        json.dump(json_load_mysubscribers, outfile)

def get_authenticated_service():
    if os.path.exists("CREDENTIALS_PICKLE_FILE"):
        with open("CREDENTIALS_PICKLE_FILE", 'rb') as f:
            credentials = pickle.load(f)
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        with open("CREDENTIALS_PICKLE_FILE", 'wb') as f:
            pickle.dump(credentials, f)
    return googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


def save_mysubscribers():
    
    f = open('mysubscribers.json') 
    response_json = json.load(f)
    
    for item in response_json['items']:
        subtitle = item['subscriberSnippet']['title']
        description = item['subscriberSnippet']['description']
        iduser = item['id']
        idchannel = item['subscriberSnippet']['channelId']
        rows_sub.append({'subtitle': subtitle ,'iduser': iduser,'idchannel': idchannel, 'description': description })
    
    
    df = pd.DataFrame(rows_sub, columns = df_cols_sub)
    df.to_excel('mysubscribers.xlsx', index = False)


    
def retrieve_addresses():
    addresses = []
    subscribers = pd.read_excel('mysubscribers.xlsx')
    word = 'Wallet Algorand: '
    for address in zip(subscribers['description']):
        start_index = str(address).upper().find(word.upper())
        end_index = start_index + len(word) # if the start_index is not -1
        if start_index != -1:
            #search only algorand wallet address with 58 lenght charaters
            addresses.append(str(address)[end_index:(end_index+58)])  
    return addresses       
        
if __name__ == "__main__":
    main()
    save_mysubscribers()
    retrieve_addresses()
    addresses = retrieve_addresses()
    for address in addresses:
        try:
            status = algorand.send_token_to_subscribers(address)
        except Exception as e:
            print(e)        