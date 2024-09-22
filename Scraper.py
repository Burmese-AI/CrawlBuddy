import requests
import re
import json
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

# User agents for future modifications for dynamic websites
# user_agents = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
#     "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
# ]


def getChildrenData(url, children, data):
    """
    This function extracts data from all potential tags with data
    """
    # specify parents to skip
    parents = ["nav", "header", "footer", "button", "noscript", "figcaption", "code"]
    for child in children:
        # skip tags with specified parents
        if parents and child.find_parent(parents):
            continue

        """
        content is
        NOT tag
        NOT descendent of 'figure' tag
        NOT descendent of empty anchor tag
        HAS at least one alphabet
        HAS at least three words
        """
        content = {}
        if (
            not isinstance(child, Tag)
            and not child.find_parent("figure")
            and not child.find_parent("a", href="#")
            and re.search(r"[a-zA-Z]", child.get_text(strip=True))
            and re.search(r" ", child.get_text(strip=True))
            and len(child.get_text(strip=True).split()) >= 3
        ):
            content["tag"] = child.parent.name if child.parent else ""
            content["text"] = child.get_text(strip=True).replace("\n", "")

            if child.parent and child.parent.name == "a":
                continue

        if len(content.keys()) > 0:
            data.append(content)

def getLinks(url, children, links):
    
    # same as getChildrenData but this function processess tags

    parents = ["nav", "header", "footer", "button", "noscript", "figcaption"]
    for child in children:
        # skip tags with specified parents
        if parents and child.find_parent(parents):
            continue

        if (
            not isinstance(child, Tag)
            and not child.find_parent("figure")
            and not child.find_parent("a", href="#")
            and re.search(r"[a-zA-Z]", child.get_text(strip=True))
            and re.search(r" ", child.get_text(strip=True))
            and child.parent and child.parent.name == "a"
        ):
            
            links.append(urljoin(url, child.parent.get("href")))

    
def metaData(soup):
    """
    This function extracts data from <meta> tags
    """

    # Extract Title
    title = soup.title.string.replace("\n", "") if soup.title else ""

    # Extract Description
    desc = soup.find("meta", {"name": "description"})
    description = desc.attrs["content"].replace("\n", "").strip() if desc else ""

    # Extract author
    author_meta = soup.find("meta", {"name": "author"})
    author = (
        author_meta.attrs["content"].replace("\n", "").strip() if author_meta else ""
    )

    # Extract publish date (assuming it's in a 'name' or 'property' meta tag)
    publish_date_meta = (
        soup.find("meta", {"name": "publish_date"})
        or soup.find("meta", {"name": "publish_time"})
        or soup.find("meta", {"property": "publish_date"})
        or soup.find("meta", {"property": "article:published_time"})
    )
    publish_date = (
        publish_date_meta.attrs["content"].replace("\n", "").strip()
        if publish_date_meta
        else ""
    )

    # Extract robots
    robots_meta = soup.find("meta", {"name": "robots"})
    robots = (
        robots_meta.attrs["content"].replace("\n", " ").strip() if robots_meta else ""
    )

    return {
        "title": title,
        "description": description,
        "author": author,
        "published_date_time": publish_date,
        "robots": robots,
    }


def scrape(url):
    html = requests.get(url)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")

    if not soup:
        None

    main = soup.find("main")
    meta = metaData(soup)
    data = []
    links = []
    if main:
        # scrape <main> tag if it exists
        getChildrenData(url, main.descendants, data)
        getLinks(url, soup.body.descendants, links)
    else:
        # scrape <body> tag if no <main> tags
        getChildrenData(url, soup.body.descendants, data)
        getLinks(url, soup.body.descendants, links)

    return {"meta_data": meta, "contents": data, "links": links}


def toJson(data):
    # turn data to json file
    return json.dumps(data, indent=4)
