import datetime
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


# подгрузка и обновление excel
def update_excell():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(credentials_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    file_id = os.getenv("GOOGLE_SHEET_ID")
    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    request = drive_service.files().export_media(fileId=file_id, mimeType=mime_type)

    temp_path = "./schedule.xlsx"

    if os.path.exists(temp_path):
        os.remove(temp_path)
        print(f"Удалён старый файл: {temp_path}")

    with open(temp_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()


def download_and_update():
    current_date = datetime.datetime.now()
    try:
        update_excell()
        print(f"Расписание обновлено {current_date.strftime('%d %B %Y, %H:%M:%S')}")
    except Exception as e:
        print(e)
        print(f"!!!Расписание НЕ обновлено {current_date.strftime('%d %B %Y, %H:%M:%S')}")
