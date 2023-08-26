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

class DrugBank:
    def __init__(self):
        self.con = connector.connect(host = 'cdata.rivan.in',
                                     port = '3306',
                                     user = 'rishab_rivan',
                                     password = 'Rishab@159',
                                     database = 'client_data_by_rivan')
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
        try:
            soup = self.request_soup("https://go.drugbank.com/pathways", "Soup")
            max_rec = int(soup.find("div", attrs={"class": "page_info"}).find_all("b")[1].text)
            max_page = math.ceil(max_rec/25)
            c_page = self.last_page("page.txt", True)
            c_rec = self.last_page("Rec.txt", True)
            return max_page, c_page, c_rec
        except Exception as e:
            print("Find" + str(e))

    def pagination(self, k):
        try:
            max_page, c_page, c_rec = self.find_page_and_rec()
            c_page = self.last_page("page.txt", True)
            c_rec = self.last_page("Rec.txt", True)
            payload = {'page': c_page}
            soup = self.request_soup("https://go.drugbank.com/pathways", "Soup", payload)
            search_url = self.request_soup("https://go.drugbank.com/pathways", "URL", payload)
            table = soup.find("table", attrs={"class": "pathways-list"})
            body = table.find("tbody").find_all("tr")
            # print(len(body))
            for i in range(c_rec, len(body)):
                # print(i)
                if i+1 != len(body):
                    self.last_page("Rec.txt", False, i)
                else:
                    self.last_page("Rec.txt", False, 0)
                pathway = self.page(i, body, search_url)
                print(f"page:{c_page} and {i}. {pathway} Scraped.")
                # self.last_page(False, c_page, i)
            self.last_page("page.txt", False, c_page+1)
        except Exception as e:
            print("Pagionation" + str(e))                


    def page(self, i, body, search_url):
        try:
            temp = body[i].find_all("td")
            pathway = temp[0].text
            image_url = temp[1].find("a")["href"]
            category = temp[2].text
            temp_drugs = temp[3].find_all('a')
            Drugs={}
            for j in range(0, len(temp_drugs)):
                Drugs[f"{temp_drugs[j].text}"]=f"https://go.drugbank.com{temp_drugs[j]['href']}"
            n_url = temp[1].find("a")["href"]
            description, smpd_category, created, last_updated, sub_category, svg_url, \
            svg_filename, References = self.next_page(n_url)
            csv_file = open('Pathways.csv', 'a+', newline="", encoding='utf-8')
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([pathway, search_url, image_url, svg_url, svg_filename,
                            category, Drugs, description, smpd_category, created, last_updated,
                            sub_category, References, datetime.datetime.now()])
            csv_file.close()
            Drugs = str(Drugs).replace("'", "\\'")
            References = str(References).replace("'", "\\'")
            query = "insert into Pathways_csv(pathway, search_url, image_url, svg_url, svg_filename, category, \
            Drugs, description, smpd_category, created, last_updated, sub_category, References_text, Time_stamp) \
             values ('"+pathway+"', '"+search_url+"', '"+image_url+"', '"+svg_url+"', '"+svg_filename+"', '"+category+"', '"\
             +Drugs+"', '"+description+"', '"+smpd_category+"', '"+created+"', '"+last_updated+"', '"+sub_category+"', '"+\
             References+"', '"+str(datetime.datetime.now())+"')"
            # c = self.con.cursor()
            # print(query)
            # c.execute(query)
            # self.con.commit() 
            return pathway
        except Exception as e:
            print("Page" + str(e))  


    def next_page(self, n_url):
        try:
            n_soup = self.request_soup(n_url, "Soup")
            temp_n = n_soup.find("div", attrs={"id": "tabs-description"}) \
            .find("div", attrs={"id": "des_content"})
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
            IMG = self.request_soup(svg_url, "IMG")
            self.download_img(svg_filename, IMG)
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
            return description, smpd_category, created, last_updated, sub_category, \
            svg_url, svg_filename, References
        except Exception as e:
            print("NextPage" + str(e))


    def download_img(self, svg_filename, IMG):
        if IMG:
            with open(f"./Images/{svg_filename}", "wb") as f:
                f.write(IMG)
            f.close()
        else:
            pass

    def multi_thread(self) :
        pager = [j for j in range(1, 10)]
        with ThreadPoolExecutor() as executor :
            executor.map(self.pagination, pager)
        # self.csv_file.close()


def main():
    scrape = DrugBank()
    # scrape.Pagination()
    max_page, c_page, c_rec = scrape.find_page_and_rec()
    if c_page < max_page:
        scrape.multi_thread()

if __name__ == "__main__":
    main()
