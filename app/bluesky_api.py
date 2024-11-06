import re
from atproto import Client
from atproto_client.models.app.bsky.embed.external import ViewExternal
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
    
    def get_timeline(self, fetch_function, **fetch_params):
        page = fetch_function(limit=PAGE_LIMIT, **fetch_params)
        skeets = page.feed
        
        while self.get_more(skeets, page):
            fetch_params['cursor'] = page.cursor
            page = fetch_function(limit=PAGE_LIMIT, **fetch_params)
            skeets.extend(page.feed)
        
        return skeets
    
    def get_embed(self, skeet):
        attributes = [
            'post',
            'post.embed',
            'post.embed.external',
        ]
        current = skeet
        for attr in attributes:
            current = getattr(current, attr.split('.')[-1], None)
            if isinstance(current, ViewExternal):
                return current
    
    def is_link_skeet(self, skeet):
        return bool(self.get_embed(skeet))
    
    def get_links(self, skeets):
        timeline_by_uri = {}
        for skeet in skeets:
            if self.is_link_skeet(skeet):
                embed = self.get_embed(skeet)
                if embed and embed.uri not in timeline_by_uri:
                    timeline_by_uri[embed.uri] = []
                timeline_by_uri[embed.uri].append(skeet)
        return timeline_by_uri
    
    def get_linked_timeline(self):
        return self.get_links(self.get_timeline(self.client.get_timeline))
    
    def get_feed_aggregation(self, feed_path):
        def fetch_feed_path(limit, cursor=None):
            params = {'feed': feed_path, 'limit': limit}
            if cursor:
                params['cursor'] = cursor
            return self.client.app.bsky.feed.get_feed(params=params)
        return self.get_links(self.get_timeline(fetch_feed_path))

def is_app_passwordy(s: str) -> bool:
    """
    Determines if a string matches the pattern with four 4-character segments separated by dashes.
    """
    if len(s) != 19:  # Check total length
        return False
    if s.count('-') != 3:  # Check the number of dashes
        return False
    # Check the pattern with a regular expression
    pattern = r'^[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$'
    return bool(re.match(pattern, s))

