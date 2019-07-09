import requests
import re
import urllib.parse
from multiprocessing import Pool
import sys
from bs4 import BeautifulSoup as soup

def download_file(url):
    session = requests.Session()
    base_url = re.search('http.+.com', url).group()
    response = session.get(url)
    page_soup = soup(response.content, "lxml")
    scripts = page_soup.find_all("script", {"type": "text/javascript"})

    for script in scripts:
        if "getElementById('dlbutton')" in script.text:
            url_raw = re.search('= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);', script.text).group('url')
            math = re.search('= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);', script.text).group('math')
            dl_url = url_raw.replace(math, '"'+str(eval(math))+'"')
            break

    dl_url = base_url + eval(dl_url)
    print("Downloading", dl_url)
    local_filename = urllib.parse.unquote(dl_url.split('/')[-1])
    with requests.get(dl_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            counter = 0
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: 
                    f.write(chunk)

def main():
    if len(sys.argv) < 2:
        sys.exit("Specify textfile or url")
    
    media = sys.argv[1]
    if '.txt' in media:
        with open('urls.txt') as f_in:
            lines = list(line for line in (l.strip() for l in f_in) if line)
        agents = 5
        chunksize = 3
        with Pool(processes = agents)as pool:
            pool.map(download_file, lines, chunksize)
    else:
        download_file(media)

main()