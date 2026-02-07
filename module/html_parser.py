import logging

from selectolax.parser import HTMLParser

from .httpx_requests import cloud_scrp


def parse_l(url: str) -> dict:
    try:
        resp = cloud_scrp(url)
        html = HTMLParser(resp.text)
        job_title = html.css_first('h1[class*="top-card-layout__title"]')
        job_description = html.css_first(
            'div[class*="description__text description__text--rich"] section div[class*="show-more-less-html__markup"]'
        )
        return {
            "job_title": job_title.text(strip=True) if job_title is not None else None,
            "job_description": job_description.text(strip=True, separator="\n")
            if job_description
            else None,
        }
    except Exception as e:
        logging.error(f"Error parsing: {e}")
        return {}


def parse_i(url: str) -> dict:
    try:
        resp = cloud_scrp(url)
        html = HTMLParser(resp.text)
        job_title = html.css_first(
            'div[class*="jobsearch-JobInfoHeader-title-container"]'
        )
        job_description = html.css_first("div#jobDescriptionText")
        return {
            "job_title": job_title.text(strip=True) if job_title is not None else None,
            "job_description": job_description.text(strip=True, separator="\n")
            if job_description
            else None,
        }
    except Exception as e:
        logging.error(f"Error parsing: {e}")
        return {}
