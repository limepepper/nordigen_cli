import urllib
from urllib.parse import urlparse


def next_page_by_url(response, previous_page_url):
    if response["next"]:
        parsed = urlparse(response["next"])
        query = urllib.parse.parse_qs(parsed.query)
        if "offset" in query:
            try:
                _ = int(query["offset"][0])
                return response["next"]
            except ValueError:
                pass
    return None
