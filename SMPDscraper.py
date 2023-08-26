from os.path import exists
import re
import requests
from bs4 import BeautifulSoup
import mysql.connector as connector
from concurrent.futures import ThreadPoolExecutor
Errors = []


def next_page(pathway, image_url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        r = requests.get(image_url, headers=headers)
        n_soup = BeautifulSoup(r.text,'lxml')
        side_bar = n_soup.find('div',{'id':'sidebar_container'})
        regex = re.compile(':|\.|/|\?|-|_|=')
        htmlfilename = re.sub(regex, '', image_url)+".html"
        if not exists(f"./HTMLs/{htmlfilename}"):
            with open(f"./HTMLs/{htmlfilename}", "w", encoding="utf-8") as f:
                f.write(f"{side_bar}")
                f.close()
            print(pathway)
    except Exception as e:
        print(f"{pathway}: {e}")
        Errors.append(f"{pathway}: {e}")

mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')

query = "select * from Pathways_Table"
cursor = mydb.cursor()
cursor.execute(query)
c = cursor.fetchall()
cursor.close()
mydb.commit()
pathway = []
image_url = []
for y in c:
    pathway.append(y[0])
    image_url.append(y[2])

with ThreadPoolExecutor() as executor:
    executor.map(next_page, pathway[30000:35000], image_url[30000:35000])


print(Errors)

