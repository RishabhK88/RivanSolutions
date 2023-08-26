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

f = {}
# Errors = []
def extract(url):
	print(url)
	try:
		features = {}
		try:
			response = requests.get('http://www.' + url)
		except:
			response = requests.get('https://www.' + url)

		# print(response.status_code)
		if response.status_code >= 400:
			csv_file = open('feat.csv', 'a+', newline="", encoding='utf-8')
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow([f"{url}", f"{response.status_code}"])
			csv_file.close()
			f[f"{url}"] = f"{response.status_code}"
		else:
			features["http/https status"] = (response.url).split(":")[0]
			soup = BeautifulSoup(response.text,'lxml')
			title = soup.find("title")
			features["Title"] = f"{title}"
			meta = soup.find_all("meta")
			features["Meta"] = f"{meta}"
			redirect = {}
			for resp in response.history:
				redirect[f"{resp.url}"] = f"{resp.status_code}"
			features["Redirect History"] = redirect
			# with open('result.json', 'a+') as fp:
			# 	json.dump(features, fp)
			csv_file = open('feat.csv', 'a+', newline="", encoding='utf-8')
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow([f"{url}", f"{features}"])
			csv_file.close()
			f[f"{url}"] = f"{features}"
	except Exception as e:
		# print(f"{url}: {e}")
		# Errors.append(f"{url}: {e}")
		csv_file = open('feat.csv', 'a+', newline="", encoding='utf-8')
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow([f"{url}", f"Not Working"])
		csv_file.close()
		f[f"{url}"] = f"Not Working"




l1 = []
# l2 = []


with open('data_extracion_domains_1.csv', 'r', encoding="utf-8") as read_obj:
	csv_reader = csv.reader(read_obj)
	header = next(csv_reader)
	if header != None:
		for i, row in enumerate(csv_reader):
			# extract(row[0])
			l1.append(row[0])
			# print(i)


# import ast
# result = {}
# print(l1)
# with open('feat.csv', 'r', encoding="utf-8") as read_obj1:
# 	csv_reader1 = csv.reader(read_obj1)
# 	for row in csv_reader1:
# 		# extract(row[0])
# 		# print(row[0])
# 		l2.append(row[0])
# 		# print(i)
# 		if isinstance(row[1], str) or row[1] != "Not Working":
# 			# print(row[1])
# 			# result[f"{row[0]}"] = str(json.loads(row[1]))
# 			# result[f"{row[0]}"] = (row[1])[1:-2]
# 			# print((row[1])[1:-2])
# 			# result[f"{row[0]}"] = ast.literal_eval(row[1])
# 		else:
# 			result[f"{row[0]}"] = f"{row[1]}"

# print(result)
l2 = ['asos.com', 'isodomos.com', 'hpe.com', 'sacbee.com', 'hmnow.com']

# print(l1)
# print(l2)
r = list(set(l1) - set(l2)) + list(set(l2) - set(l1))
# print(r)



with ThreadPoolExecutor() as executor:
    executor.map(extract, r[1:50])

# print(f)
# with open('result.json', 'r') as fp:
# 	x = json.load(fp)
# print(x)	

with open('result2.json', 'w+') as fp1:
	json.dump(f, fp1, indent=4)


# print(Errors)



