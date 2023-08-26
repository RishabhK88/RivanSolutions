from os.path import exists
import json
import csv
import codecs
import re
import datetime
import math
import threading
import requests
from bs4 import BeautifulSoup
import mysql.connector as connector
from concurrent.futures import ThreadPoolExecutor
from os import listdir
from os.path import isfile, join

Errors = []


def next_page(pathway, search_url, image_url, category, Drugs, svg_filename, svg_url):
    mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')
    cursor = mydb.cursor()
    try:
        regex = re.compile(':|\.|/|\?|-|_|=')
        htmlfilename = re.sub(regex, '', image_url)+".html"
        if exists(f"./HTMLs/{htmlfilename}"):
            f=codecs.open(f"./HTMLs/{htmlfilename}", 'r')
            r = f.read()
            n_soup = BeautifulSoup(r,'lxml')
            temp_n = n_soup.find("div", attrs={"id": "tabs-description"}) \
            .find("div", attrs={"id": "des_content"})
            description = temp_n.find("div", attrs={"class": "sidebar_small_text"}).text.strip()
            smpd_category = temp_n.find_all("div", attrs={"class": "species"})[0].text
            created = temp_n.find_all("div", attrs={"class": "species"})[1] \
            .text.strip().split(" ")[1]
            last_updated = temp_n.find_all("div", attrs={"class": "species"})[2] \
            .text.strip().split(" ")[2]
            sub_category = temp_n.find("div", attrs={"id": "des_subject"}).text.strip()
            References = []
            temp_ref = n_soup.find_all("div", attrs={"class": "ref"})
            for k in range(0, len(temp_ref)):
                Reference = []
                t = temp_ref[k].find("div", attrs={"class": "ref-text"})
                if not (t.find("a") and "http://" in t.find("a")['href']):
                    r_text = t.text
                    Reference.append(r_text)
                    if temp_ref[k].find("a") and "Pubmed" in temp_ref[k].find("a").text:
                        r_link = {}
                        r_link[temp_ref[k].find('a').text.split(" ")[1]]=temp_ref[k].find('a')['href']
                        Reference.append(r_link)
                if not "http://" in Reference[0]:
                    References.append(Reference)
            References = str(References)
            Drugs = str(Drugs).replace("'", "\\'")
            pathway = str(pathway).replace("'", "\\'")
            Drugs = str(Drugs).replace('"', '\\"')
            pathway = str(pathway).replace('"', '\\"')
            description = str(description).replace("'", "\\'")
            References = str(References).replace("'", "\\'")
            description = str(description).replace('"', '\\"')
            References = str(References).replace('"', '\\"')

            query = "insert into Pathways_data(pathway, search_url, image_url, svg_url, svg_filename, category, \
                Drugs, description, smpd_category, created, last_updated, sub_category, References_text, Time_stamp) \
                values ('"+pathway+"', '"+search_url+"', '"+image_url+"', '"+svg_url+"', '"+svg_filename+"', '"+category+"', '"\
                +Drugs+"', '"+description+"', '"+smpd_category+"', '"+created+"', '"+last_updated+"', '"+sub_category+"', '"+\
                References+"', '"+str(datetime.datetime.now())+"')"
            # cursor.execute(query)
            # mydb.commit()
            # cursor.close()
            print(pathway)
        else:
            pass
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
search_url = []
image_url = []
category = []
Drugs = []
for y in c:
    pathway.append(y[0])
    search_url.append(y[1])
    image_url.append(y[2])
    category.append(y[5])
    Drugs.append(y[6])

svg_url = [x + "/download?type=full_vector_image" for x in image_url]
regex = re.compile(':|\.|/|\?|-|_|=')
svg_filename = []
for z in svg_url:
    svg_filename.append(re.sub(regex, '', z)+".svg")
with ThreadPoolExecutor() as executor:
    executor.map(next_page, pathway[30000:35000], search_url[30000:35000], image_url[30000:35000], category[30000:35000], Drugs[30000:35000], svg_filename[30000:35000], svg_url[30000:35000])


print(Errors)

