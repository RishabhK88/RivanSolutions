import requests
from bs4 import BeautifulSoup
import csv
import re
import datetime

headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
csv_file = open('Pathways.csv', 'a', newline="", encoding='utf-8')
csv_writer = csv.writer(csv_file)
# csv_writer.writerow(['Pathway', 'SearchURL', 'ImageURL', 'SVG_URL', 'SVG_FileName', 'Category', 'Drugs', 'Title', 'Description', 'SMPD_Category', 'Created', 'Last_Updated', 'Sub_Category', 'References', 'Timestamp'])
p=1
while p<101:
	payload = {'page': p}

	r = requests.get("https://go.drugbank.com/pathways", headers=headers, params = payload)
	soup = BeautifulSoup(r.text, 'lxml')
	table = soup.find("table", attrs={"class": "pathways-list"})
	body = table.find("tbody").find_all("tr")
	# print(body)


	for i in range(0, len(body[1:])+1):
		temp = body[i]
		Pathway = temp.find_all("td")[0].text
		ImageURL = temp.find_all("td")[1].find("a")["href"]
		Category = temp.find_all("td")[2].text
		temp_drugs = temp.find_all("td")[3].find_all('a')
		drugs_dict={}
		for j in range(0, len(temp_drugs)):
			drugs_dict[f"{temp_drugs[j].text}"]=f"https://go.drugbank.com{temp_drugs[j]['href']}"
		Drugs = drugs_dict
		temp_url = temp.find_all("td")[1].find("a")["href"]
		temp_r = requests.get(f"{temp_url}", headers=headers)
		temp_soup = BeautifulSoup(temp_r.text, 'lxml')
		Description = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find("div", attrs={"class": "sidebar_small_text"}).text.strip()
		Title = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find("h4", attrs={"id": "des_head"}).text
		SMPD_Category = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find_all("div", attrs={"class": "species"})[0].text
		Created = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find_all("div", attrs={"class": "species"})[1].text.strip().split(" ")[1]
		Last_Updated = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find_all("div", attrs={"class": "species"})[2].text.strip().split(" ")[2]
		Sub_Category = temp_soup.find("div", attrs={"id": "tabs-description"}).find("div", attrs={"id": "des_content"}).find("div", attrs={"id": "des_subject"}).text.strip()
		temp_SVG = temp_url + "/download?type=full_vector_image"
		IMG = requests.get(temp_SVG, headers=headers).content
		if IMG:
			IMG = requests.get(temp_SVG, headers=headers).content
		else:
			IMG=False
		temp_ref = temp_soup.find_all("div", attrs={"class": "ref"})
		ref_dict={}
		regex = re.compile(':|\.|/|\?|-|_|=')
		SVG_FileName = re.sub(regex, '', temp_SVG)+".svg"
		for k in range(0, len(temp_ref)):
			if temp_ref[k].find("a") and "Pubmed" in temp_ref[k].find("a").text:
				ref_dict[temp_ref[k].find('a').text.split(" ")[1]]=temp_ref[k].find('a')['href']
		References = ref_dict
		csv_writer.writerow([Pathway, r.url, ImageURL, temp_SVG, SVG_FileName, Category, Drugs, Title, Description, SMPD_Category, Created, Last_Updated, Sub_Category, References, datetime.datetime.now()])
		if IMG:
			with open(SVG_FileName, "wb") as f:
				f.write(IMG)
		else:
			pass
		print(f"Page:{p} and {i}. {Pathway} Scraped.")
	p+=1

csv_file.close()

