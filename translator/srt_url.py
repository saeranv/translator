import os
import requests
from bs4 import BeautifulSoup

SUB_SEARCH_URL = ("https://www.opensubtitles.org/en/search2"
                  "/sublanguageid-eng/moviename-")


def get_query_html(site_url:str, query:str) -> bytes:
    """Returns subtitles search html from given url and query string"""

    query_ = query.replace(" ", "+").strip()
    url =  f"{site_url}{query_}"
    resp = requests.get(url)

    return resp.content


def parse_sub_urls(content:bytes) -> dict[str,str]:
    """Returns the subtitle file url from the html"""


    soup = BeautifulSoup(content, "html.parser")
    table = soup.find_all("a", {"table id": "search_results"})
    # TODO: parse table to get sub title and url
    # TODO: if this fails, use https://jamesturk.github.io/scrapeghost/
    #sub_urls = [link["href"] for link in links
    #        if "english" in link.text.lower()]
    sub_urls = table
    return sub_urls


if __name__ == "__main__":
    content = get_query_html(SUB_SEARCH_URL, "Interstellar")
    sub_urls = parse_sub_urls(content)
    print(sub_urls)
