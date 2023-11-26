# THIS FILE IS USED FOR TESTING PURPOSES ONLY

import api.scraper.wikiScraper as wikiScraper
from pprint import PrettyPrinter

if __name__ == '__main__':
    pp = PrettyPrinter(indent=4)
    root = wikiScraper.scrape_page_tree('https://azur-lane.fandom.com')
    pp.pprint(root)
    #print(wikiScraper.get_page_title('https://azur-lane.fandom.com'))

