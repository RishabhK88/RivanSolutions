
from torrequest import TorRequest
from bs4 import BeautifulSoup

with TorRequest(proxy_port=9050, ctrl_port=9051, password="Rishabh") as tr:
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    response = tr.get('https://www.barnesandnoble.com/h/books/browse', headers = headers)
    print(response.text)  # not your IP address
    html = BeautifulSoup(response.text, 'lxml')
    with open(f"ReqHTML.html", "w+", encoding="utf-8") as f:
        f.write(f"{html}")
        f.close()
  

    tr.reset_identity()

    response = tr.get('http://ipecho.net/plain')
    print(response.text)  # another IP address, not yours