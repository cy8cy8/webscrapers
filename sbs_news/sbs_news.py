# 1. sudo dnf install libxml2-devel libxslt-devel (helper programs written in C to handle web data e.g. HTML, XML)
# 2. sudo dnf install gcc gcc-c++
# 3. pip install newspaper4k newspaper4k[nlp] lxml_html_clean feedparser
# RSS feed example: https://www.sbs.com.au/news/article/feeds/nbv1rs3kw

import feedparser, newspaper, pydoc

class Sbs_News():
    def __init__(self):
        self.rss_urls = [
            "https://www.sbs.com.au/news/feed", 
            "https://www.sbs.com.au/news/topic/latest/feed", 
            "https://www.sbs.com.au/news/topic/australia/feed",
            "https://www.sbs.com.au/news/topic/world/feed"
        ]

    def _get_all_feed_from_sbs(self) -> tuple[list[str], list[str]]:
        """
        Combines top stories from all SBS RSS feeds, removes duplicates, 
        and returns unique story links and titles.
        """
        # Use a dict to map unique links to their titles in one pass
        unique_stories: dict[str, str] = {
            entry.link: entry.title
            for url in self.rss_urls
            for entry in feedparser.parse(url).entries
        }
        story_links = list(unique_stories.keys())
        story_titles = list(unique_stories.values())
        print(f"{len(story_links)} unique articles found")
        return story_links, story_titles

    def _retrive_and_display_all_headlines_from_feed(self) -> None:
        links, titles = self._get_all_feed_from_sbs()
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        return links

    def read_a_news_article(self) -> None:
        links = self._retrive_and_display_all_headlines_from_feed()
        while True:
            try: 
                choice = input("Choose a story to read or [q]uit: ")
                if choice == "q": break
                choice = int(choice)
                if not (1 <= choice <= len(links)): continue
            except ValueError:
                continue
            article = newspaper.article(links[choice-1]).text
            pydoc.pager(article)