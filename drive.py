from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def init_auth(folder_url):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    load_files(folder_url, drive)


def load_files(folder_url, drive):
    splits = folder_url.split("/")
    folder_id = splits[-1]
    # List files from drive
    file_list = drive.ListFile({'q':f"'{folder_id}' in parents and trashed = false"}).GetList()
    for file in file_list:
        if file['mimeType'] == "application/pdf":
            file.GetContentFile(f"resume_files/{file['title']}") # downloads the file            