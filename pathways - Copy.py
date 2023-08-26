import re
import datetime
import math
from bs4 import BeautifulSoup
import mysql.connector as connector
from concurrent.futures import ThreadPoolExecutor
import requests


def pagination():
    search_url_output = []
    r = requests.get("https://go.drugbank.com/pathways")
    soup = BeautifulSoup(r.text,'lxml')
    max_rec = int(soup.find("div", attrs={"class": "page_info"}).find_all("b")[1].text)
    max_page = math.ceil(max_rec/25)
    c_page=1
    for page_no in range(c_page,max_page+1):
        search_url = "https://go.drugbank.com/pathways?page="+str(page_no)
        search_url_output.append(search_url)
    return search_url_output

def page(search_url):
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
            query = "insert into Pathways_Table(pathway, search_url, image_url, category, Drugs) \
                values ('"+pathway+"', '"+search_url+"', '"+image_url+"', '"+category+"', '"+Drugs+"')"
            cursor.execute(query)
            mydb.commit()
            cursor.close()
            print(pathway,image_url,category,Drugs)
    except Exception as e:
        print("Page" + str(e))
        
def next_page(pathway, search_url, image_url, category, Drugs, svg_filename, svg_url):
    mydb = connector.connect(host='cdata.rivan.in',
                                 port='3306',
                                 user='rishab_rivan',
                                 password='Rishab@159',
                                 database='client_data_by_rivan')
    cursor = mydb.cursor()
    try:
        # print(category)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
        r = requests.get(image_url, headers=headers)
        n_soup = BeautifulSoup(r.text,'lxml')
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
        
        regex = re.compile(':|\.|/|\?|-|_|=')
        htmlfilename = re.sub(regex, '', image_url)+".html"
        References = str(References)
        Drugs = str(Drugs).replace("'", "\\'")
        pathway = str(pathway).replace("'", "\\'")
        Drugs = str(Drugs).replace('"', '\\"')
        pathway = str(pathway).replace('"', '\\"')
        description = str(description).replace("'", "\\'")
        References = str(References).replace("'", "\\'")
        description = str(description).replace('"', '\\"')
        References = str(References).replace('"', '\\"')
        with open(f"./HTMLs/{htmlfilename}", "w", encoding="utf-8") as f:
            f.write(r.text)
            f.close()

        query = "insert into Pathways_data(pathway, search_url, image_url, svg_url, svg_filename, category, \
            Drugs, description, smpd_category, created, last_updated, sub_category, References_text, Time_stamp) \
             values ('"+pathway+"', '"+search_url+"', '"+image_url+"', '"+svg_url+"', '"+svg_filename+"', '"+category+"', '"\
             +Drugs+"', '"+description+"', '"+smpd_category+"', '"+created+"', '"+last_updated+"', '"+sub_category+"', '"+\
             References+"', '"+str(datetime.datetime.now())+"')"
        cursor.execute(query)
        mydb.commit()
        cursor.close()
        print(pathway)
    except Exception as e:
        print(f"{pathway}: {e}")
        
        
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
        
        
if __name__ == "__main__":


    mydb = connector.connect(host = 'cdata.rivan.in',
                                     port = '3306',
                                     user = 'rishab_rivan',
                                     password = 'Rishab@159',
                                     database = 'client_data_by_rivan')
    list_of_search_urls = pagination()
    with ThreadPoolExecutor() as executor:
        executor.map(page, list_of_search_urls)

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
        executor.map(next_page, pathway, search_url, image_url, category, Drugs, svg_filename, svg_url)
        
    with ThreadPoolExecutor() as executor:
        executor.map(download_img, svg_filename, svg_url)

