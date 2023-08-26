from os.path import exists
import json
import csv
import re
import datetime
import math
import threading
import requests
from bs4 import BeautifulSoup
import mysql.connector as connector
from concurrent.futures import ThreadPoolExecutor

Errors = []

mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')

def download_img(svg_filename, svg_url):
    try:
        headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        r = requests.get(svg_url, headers=headers)
        IMG = r.content
        if IMG:
            with open(f"./Images/{svg_filename}", "wb") as f:
                f.write(IMG)
                print(svg_url)
            f.close()
        else:
            pass
    except Exception as e:
        print(f"{svg_url}: {e}")
        Errors.append(f"{svg_url}: {e}")


query = "select image_url from Pathways_Table"
cursor = mydb.cursor()
cursor.execute(query)
c = cursor.fetchall()
cursor.close()
mydb.commit()

urls = []
for y in c:
    urls.append(y[0])

svg_url = [x + "/download?type=full_vector_image" for x in urls]
regex = re.compile(':|\.|/|\?|-|_|=')
svg_filename = []
for y in svg_url:
    svg_filename.append(re.sub(regex, '', y)+".svg")
# print(len(svg_url))
# print(len(svg_filename))


with ThreadPoolExecutor() as executor:
    executor.map(download_img, svg_filename, svg_url)


print(Errors)


