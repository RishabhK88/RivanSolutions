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
import codecs
import urllib
def apc_get_html(url):
  html = BeautifulSoup(requests.get(url,
                           headers={'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}).content, 'html.parser')
  # print()
  return html

url = 'https://www.1mg.com/drugs/azithral-500-tablet-325616'

html = apc_get_html(url)
x = html.find('div', id='drug_header').find('div', class_='slick-track')
print(x.find("script"))




