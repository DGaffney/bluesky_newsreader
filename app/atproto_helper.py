from atproto import Client
from atproto_client.models.app.bsky.embed.external import External
import db
TIMELINE_MIN = 1000
PAGE_LIMIT = 100
class BlueskyAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client()
        self.client.login(self.username, self.password)
    
    def get_more(self, skeets, page):
        return page.cursor and len(skeets) < TIMELINE_MIN
    
    def get_timeline(self):
        page = self.client.get_timeline(limit=PAGE_LIMIT)
        skeets = page.feed
        while self.get_more(skeets, page):
            page = self.client.get_timeline(limit=PAGE_LIMIT)
            for skeet in page.feed:
                skeets.append(skeet)
        return skeets
    
    def get_embed(self, skeet):
        attributes = [
            'post',
            'post.embed',
            'post.embed.record',
            'post.embed.record.value',
            'post.embed.record.value.embed',
            'post.embed.record.value.embed.external'
        ]
        current = skeet
        for attr in attributes:
            current = getattr(current, attr.split('.')[-1], None)
            if isinstance(current, External):
                return current
    
    def is_link_skeet(self, skeet):
        return bool(self.get_embed(skeet))
    
    def get_links(self, skeets):
        timeline_by_uri = {}
        for skeet in skeets:
            if self.is_link_skeet(skeet):
                if not timeline_by_uri.get(self.get_embed(skeet).uri):
                    timeline_by_uri[self.get_embed(skeet).uri] = []
                timeline_by_uri[self.get_embed(skeet).uri].append(skeet)
        return timeline_by_uri
    
    def get_news_feed(self):
        return self.get_links(self.get_timeline())
