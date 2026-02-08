"""
Just a simple test that each scraper can request a page and that it gets a 200 response.
"""

import pytest

from module.scrapers import cloud_scrp, httpx_scrp


def test_cloud_scrp():
    url = "https://www.google.com"
    response = cloud_scrp(url)
    assert response.status_code == 200


def test_httpx_scrp():
    url = "https://www.google.com"
    response = httpx_scrp(url)
    assert response.status_code == 200
