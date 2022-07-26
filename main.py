from flask import Blueprint,Flask,request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

import os.path
import json

load_dotenv(override=False)

bp = Blueprint('burritos', __name__,template_folder='templates')
PREFIX='/google-spreadsheet-api'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

@bp.route("/googleDoc/health")
def health():
    return 'success'

@bp.route("/googleDoc/spreadsheet")
def download_spreadsheet():
    key,gid,alt = pluck(request.args,'key','gid','alt')
    title_row = int(request.args.get('title_row',0))
    start_row = int(request.args.get('start_row',2))

    if not key or not gid:
        return "required key,gid as query string !!!"
    
    config = {
        'key': key,
        'gid': gid,
        'title_row':title_row,
        'start_row': start_row
    }

    data=parse_spreadsheet(config)

    if alt == 'json':
        data=convert_list_to_json(data)
    return {'data': data }


def parse_spreadsheet(config):
    key,gid,title_row,start_row = pluck(config,'key','gid','title_row','start_row')

    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet_metadata = service.spreadsheets().get(spreadsheetId=key).execute()
    sheets = sheet_metadata.get('sheets',[])
    current_sheet=list(filter(lambda x: x['properties']['sheetId'] == int(gid),sheets))
    if not current_sheet:
        return 'this sheet is not exist'
        
    range_name = current_sheet[0]['properties']['title']
    result =  service.spreadsheets().values().get(spreadsheetId=key,range=range_name).execute()
    values = result.get('values', [])
    values = [values[title_row]] + values[start_row:]
    max_row_length=len(max(values,key=len))
    values=list(map(lambda x: x + ([''] * (max_row_length - len(x))),values))
    values[0] = build_title(values[0])

    if not values:
        return 'No data found'
    
    return values

def convert_list_to_json(data):
    # title_row=0,start_row=1
    result=[]
    title_rows= data[0]
    for i in range(1,len(data)):
        line = dict()
        for j,cell in enumerate(data[i]):
            title_name=title_rows[j]
            strip_cell=cell.strip()
            if title_name and strip_cell:
                line[title_name]=line.get(title_name,[]) + [strip_cell]
        result.append(line)
    return result

def build_title(cells):
    title_row=[]
    for cell in cells:
        cell=cell.strip()
        if cell:
            title_row.append(cell)
        else:
            if title_row :
                title_row.append(title_row[-1])
    return title_row

# deconstruct dict to values
pluck = lambda dict,*args : (dict.get(arg,None) for arg in args)

app = Flask(__name__)
app.register_blueprint(bp, url_prefix=PREFIX)

if __name__ == '__main__':
    # app.debug = True
    app.run(
        host='0.0.0.0',
        port=5000
    )  