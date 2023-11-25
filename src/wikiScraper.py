import requests
from bs4 import BeautifulSoup
from typing import NamedTuple


class PageElement(NamedTuple):
    tag: str
    text: str


def scrape_page(url):

    _PAGE_CONTENTS_LIST = []

    try:
        page = requests.get(url)
        page.raise_for_status()
    except requests.RequestException as e:
        print(f"Error related to request occurred: {e}")
    except Exception as e:
        print(f"Unexpected exception has occurred: {e}")

    try:
        # Get contents of the page using BeautifulSoup and then find in them div with class 'page'
        main_content = BeautifulSoup(page.content, 'html.parser').find('div', class_='page')
        for each in main_content.descendants:
            if each.name:
                element = PageElement(tag=each.name, text=each.get_text(strip=True))
                _PAGE_CONTENTS_LIST.append(element)
    except AttributeError as e:
        print(f"Error: {e}")

    return _PAGE_CONTENTS_LIST
