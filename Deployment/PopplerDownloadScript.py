import os
from google_drive_downloader import GoogleDriveDownloader as gdd

if(not os.path.isdir('C:\poppler-0.68.0')):
    gdd.download_file_from_google_drive(file_id='1aslGtTKrj6iW6sJ2cOnwpG1T_Up8EYxF',
                                    dest_path='C:\poppler.zip',
                                    unzip=True)
