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

mydb = connector.connect(host='cdata.rivan.in',
                         port='3306',
                         user='rishab_rivan',
                         password='Rishab@159',
                         database='client_data_by_rivan')
class DrugBank:
    def __init__(self):
        mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')
        cursor = mydb.cursor()

        if not exists("Pathways.csv"):
            csv_file = open('Pathways.csv', 'w+', newline="", encoding='utf-8')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["pathway", "search_url", "image_url", "svg_url", "svg_filename",
                        "category", "Drugs", "description", "smpd_category", "created", "last_updated",
                        "sub_category", "References", "Timestamp"])
            csv_file.close()

    def request_soup(self, URL, c, payload=False):
        headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        r = requests.get(f"{URL}", headers=headers, params=payload)
        if c == "Soup":
            return BeautifulSoup(r.text, 'lxml')
        elif c == "URL":
            return r.url
        elif c=="IMG":
            if r.content:
                return r.content
            else:
                return False
        else:
            pass

    def last_page(self, f, r, w=0):
        if r:
            with open(f, "r", encoding='utf-8') as f:
                return int(f.read())
        else:
            with open(f, "w+", encoding='utf-8') as f:
                f.write(f"{w}")

        f.close()

    def find_page_and_rec(self):
        soup = self.request_soup("https://go.drugbank.com/pathways", "Soup")
        max_rec = int(soup.find("div", attrs={"class": "page_info"}).find_all("b")[1].text)
        max_page = math.ceil(max_rec/25)
        c_page = self.last_page("page.txt", True)
        c_rec = self.last_page("Rec.txt", True)
        return max_page, c_page, c_rec

    def pagination(self):
        print("ent")
        search_url_output = []
        max_page, c_page, c_rec = self.find_page_and_rec()
        for page_no in range(c_page,max_page+1):
            # print("yes")
            search_url = "https://go.drugbank.com/pathways?page="+str(page_no)
            self.last_page("page.txt", False, page_no + 1)
            search_url_output.append(search_url)
            # print(search_url)
        return search_url_output

    def page(self, search_url):
        mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')
        cursor = mydb.cursor()

        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
            r = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(r.text,'lxml')
            table = soup.find("table", attrs={"class": "pathways-list"})
            body = table.find("tbody").find_all("tr")
            for i in range(0, len(body)):
                temp = body[i].find_all("td")
                pathway = temp[0].text
                image_url = temp[1].find("a")["href"]
                category = temp[2].text
                temp_drugs = temp[3].find_all('a')
                Drugs={}
                for j in range(0, len(temp_drugs)):
                    Drugs[f"{temp_drugs[j].text}"]=f"https://go.drugbank.com{temp_drugs[j]['href']}"
                n_url = temp[1].find("a")["href"]
                Drugs = str(Drugs).replace("'", "\\'")
                pathway = str(pathway).replace("'", "\\'")
                Drugs = str(Drugs).replace('"', '\\"')
                pathway = str(pathway).replace('"', '\\"')
                query = "insert into Pathways_Table(pathway, search_url, image_url, category, Drugs) " \
                        "values ('"+pathway+"', '"+search_url+"', '"+image_url+"', '"+category+"', '"+Drugs+"')"
                cursor.execute(query)
                mydb.commit()
            cursor.close()
        except Exception as e:
            print("Page" + str(e))

    def next_page(self, n_url):
        mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')
        cursor = mydb.cursor()
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
            r = requests.get(n_url, headers=headers)
            n_soup = BeautifulSoup(r.text,'lxml')
            temp_n = n_soup.find("div", attrs={"id": "tabs-description"}) \
            .find("div", attrs={"id": "des_content"})
            title = temp_n.find("h4", attrs={"id": "des_head"}).text
            description = temp_n.find("div", attrs={"class": "sidebar_small_text"}).text.strip()
            smpd_category = temp_n.find_all("div", attrs={"class": "species"})[0].text
            created = temp_n.find_all("div", attrs={"class": "species"})[1] \
            .text.strip().split(" ")[1]
            last_updated = temp_n.find_all("div", attrs={"class": "species"})[2] \
            .text.strip().split(" ")[2]
            sub_category = temp_n.find("div", attrs={"id": "des_subject"}).text.strip()
            svg_url = n_url + "/download?type=full_vector_image"
            regex = re.compile(':|\.|/|\?|-|_|=')
            svg_filename = re.sub(regex, '', svg_url)+".svg"
            # IMG = self.request_soup(svg_url, "IMG")
            # self.download_img(svg_filename, IMG)
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
            description = str(description).replace("'", "\\'")
            References = str(References).replace("'", "\\'")
            description = str(description).replace('"', '\\"')
            References = str(References).replace('"', '\\"')
            References = """%s""".format(References)
            query = "insert into Pathways_csv(pathway, description, smpd_category, created, last_updated, sub_category, \
                 svg_url, References_text, Time_stamp, svg_filename) values ('"+title+"', '"+description+"', '"+smpd_category+"', '"\
                 +created+"', '"+last_updated+"', '"+sub_category+"', '"+svg_url+"', '"+References+"\
                 ', '"+str(datetime.datetime.now())+"', '"+svg_filename+"')"
            # cursor = mydb.cursor()
            cursor.execute(query)
            mydb.commit()
            cursor.close()
            print(svg_filename)
        except Exception as e:
            print("NextPage" + str(e))

    def download_img(self, svg_filename, svg_url):
        IMG = self.request_soup(svg_url, "IMG")
        if IMG:
            with open(f"./Images/{svg_filename}", "wb") as f:
                f.write(IMG)
            f.close()
        else:
            pass

if __name__ == "__main__":

    scrape = DrugBank()
    # list_of_search_urls = scrape.pagination()
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape.page, list_of_search_urls)

    query = "select image_url from Pathways_Table"
    cursor = mydb.cursor()
    cursor.execute(query)
    c = cursor.fetchall()
    cursor.close()
    mydb.commit()
    img_urls = []
    # print(img_urls)
    for x in c:
        img_urls.append(x[0])
    # print(img_urls)
    with ThreadPoolExecutor() as executor:
        executor.map(scrape.next_page, img_urls)

    # query = "select svg_filename, svg_url from Pathways_Table"
    # cursor = mydb.cursor()
    # cursor.execute(query)
    # mydb.commit()
    # cursor.close()
    # filenames = []
    # urls = []
    # for y in c:
    #     filenames.append(y[0])
    #     urls.append(y[1])
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape.download_img, filenames, urls)

    mydb.close()