from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = '1UsEcOQWeKXW_6dzItRQapKPxfo9ryaHOHEJIb6vYr9A'
RANGE_NAME = 'apple'

SERVICE_ACCOUNT_FILE='credential.json'


def main():
    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets',[])
        current_sheet=list(filter(lambda x: x.get('properties').get('sheetId') == 0,sheets))

        if not current_sheet:
            print('this sheetId is not exist')
            return
            
        RANGE_NAME = current_sheet[0].get('properties').get('title')
        result =  service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        print(values)
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()