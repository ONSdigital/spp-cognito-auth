import re


def fix_url(url: str) -> str:
    if not re.match("(?:http|https)://", url):
        url = "https://{}".format(url)
    return url
