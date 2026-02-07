import logging

import cloudscraper
import httpx
import requests
from fake_useragent import UserAgent

USER_AGENT = UserAgent().chrome
CLIENT = httpx.Client(headers={"User-Agent": USER_AGENT})
SCRAPER = cloudscraper.create_scraper(
    # Challenge handling
    interpreter="js2py",  # Best compatibility for v3 challenges
    delay=5,  # Extra time for complex challenges
    # Stealth mode
    enable_stealth=True,
    stealth_options={
        "min_delay": 2.0,
        "max_delay": 6.0,
        "human_like_delays": True,
        "randomize_headers": True,
        "browser_quirks": True,
    },
    # Browser emulation
    browser="firefox",
    # Debug mode
    debug=False,
)


def httpx_scrp(url, **kwargs) -> httpx.Response:
    logging.debug(f"Making GET request to {url} with User-Agent: {USER_AGENT}")

    # Setup headers with User-Agent
    if kwargs.get("headers"):
        logging.info("Custom headers provided, updating CLIENT headers.")
        CLIENT.headers.update(kwargs.get("headers", {}))

    # Do the request using httpx
    resp = CLIENT.get(url, **kwargs)

    return resp


def cloud_scrp(url: str, **kwargs) -> requests.Response:
    logging.debug(f"Making CloudScraper GET request to {url}")

    return SCRAPER.get(url, **kwargs)
