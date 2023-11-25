import requests, re
from bs4 import BeautifulSoup
from typing import NamedTuple


_EXCLUDED_CLASSES = ['animangafooter', 'global-footer', 'bottom-ads-container']
_EXCLUDED_ALTS = ['Advertisement', 'Navigation menu', 'Jump to search', 'Jump to navigation', 'Jump to main content',]


class PageElement(NamedTuple):
    html_tag: str
    contents: list
    link: str = None


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
        # Get contents of the page using BeautifulSoup and then find in them div which contains main content
        main_content = BeautifulSoup(page.content, 'html.parser').find(class_='mw-parser-output')

        for each in _EXCLUDED_CLASSES:
            for element in main_content.find_all(class_=each):
                element.decompose()

        for each in main_content.descendants:
            if each.name and each.name not in _EXCLUDED_ALTS and each.get_text(strip=True):
                element = PageElement(html_tag=each.name,
                                      contents=(lambda x: x.splitlines())(each.get_text(strip=False).strip()),
                                      link=each.get('href') if each.get('href') else None)
                _PAGE_CONTENTS_LIST.append(element)
        for each in _PAGE_CONTENTS_LIST:
            for element in each.contents:
                if element == '' or element.isspace():
                    each.text.remove(element)

    except AttributeError as e:
        print(f"Error: {e}")

    _PAGE_CONTENTS_LIST = convert_relative_links_to_absolute(url, _PAGE_CONTENTS_LIST)

    return _PAGE_CONTENTS_LIST


def convert_relative_links_to_absolute(url, page_contents):

    parsed = []

    url = (lambda x: x[:-6] if x.endswith('wiki/') else x)(url)

    for each in page_contents:
        if each.link and re.match(r'^(?!www\.|(?:http|ftp)s?://|[A-Za-z]:\\|//).*/', each.link):
            web_url = url + each.link
            element = PageElement(html_tag=each.html_tag, contents=each.contents, link=web_url)
            parsed.append(element)
        else:
            web_url = None
            element = PageElement(html_tag=each.html_tag, contents=each.contents, link=web_url)
            parsed.append(element)
    return parsed
