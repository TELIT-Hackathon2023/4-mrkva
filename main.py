import scraper.wikiScraper as wikiScraper
from pprint import PrettyPrinter

if __name__ == '__main__':
    pp = PrettyPrinter(indent=4)
    pp.pprint(wikiScraper.scrape_page('https://fringe.fandom.com/wiki/FringeWiki'))

