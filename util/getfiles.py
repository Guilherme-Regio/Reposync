from bs4 import BeautifulSoup
from os import path, walk
from requests import get, exceptions
from time import sleep

def get_weblist(url):
    while True:
        try:
            response = get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")
            return [link.get("href") for link in links]
        except exceptions.RequestException as e:
            if "HTTPConnectionPool" in str(e) and "timed out" in str(e):
                print('Fila de acesso HTTP esgotada. Tentando novamente em 5 segundos...')
                sleep(5)
            else:
                print(f"Erro inesperado: {e}")
                return False


def filter_weblist(urlpath):
    web_list = get_weblist(urlpath)
    directories = [path.basename(item.rstrip('/')) for item in web_list if not item.startswith("?") and not item.endswith(".md5") and path.basename(item.rstrip('/')) != ".."]
    return directories


def get_locallist(path):
    local_dir = path
    local_list = set()
    for root, dirs, files in walk(local_dir):
        if root == local_dir: 
            for directory in dirs:
                local_list.add(directory)
            break
    return list(local_list)


def get_textfromweb(url):
    html = get(url)
    raw = html.content.decode('utf8')
    return str(raw)
