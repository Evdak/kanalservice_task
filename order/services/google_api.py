from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials

import os.path
import os

from datetime import datetime

import json


# Файл, полученный в Google Developer Console
CREDENTIALS_FILE_SHEETS = 'creds_sheets.json'
# ID Google Sheets документа
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
# ID Google Drive документа
SPREADSHEET_FILE_ID = os.environ.get("SPREADSHEET_FILE_ID")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/drive.metadata.readonly']


def get_file_data():
    creds = get_creds()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        values = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="A:D",
            majorDimension='ROWS'
        ).execute()

        return values

    except HttpError as error:
        print(f'An error occurred: {error}')


def get_last_modified_time() -> datetime:

    creds = get_creds()

    try:
        service = build('drive', 'v3', credentials=creds)

        result = service.files().get(
            fileId=SPREADSHEET_FILE_ID,
            fields="modifiedTime"
        ).execute()

        return (datetime.strptime(
            result['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ'))

    except HttpError as error:
        print(f'An error occurred: {error}')


def get_creds():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(
            'token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds
