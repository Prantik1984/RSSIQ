import feedparser
import json
import sys
from typing import List,Dict
class FeedOperator:
    """"
    Performs feed related operations
    """
    def get_feed_details(self, feed_url)->List[Dict[str, str]]:
        """"
        Downloads feed details
        """
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            print("Error reading RSS feed:", feed.bozo_exception)
            sys.exit(1)

        articles = []

        for entry in feed.entries:
            try:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                })
            except Exception as e:
                print("Error reading RSS feed:", e)

        return articles
