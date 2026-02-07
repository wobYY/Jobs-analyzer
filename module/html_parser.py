import logging
from dataclasses import dataclass

from selectolax.parser import HTMLParser

from .scrapers import cloud_scrp


@dataclass
class JobData:
    url: str
    job_title: str | None
    job_description: str | None


def parse_l(url: str) -> JobData:
    try:
        resp = cloud_scrp(url)
        html = HTMLParser(resp.text)
        job_posting_company = html.css_first(
            'a[data-tracking-control-name="public_jobs_topcard-org-name"]'
        )
        job_title = html.css_first('h1[class*="top-card-layout__title"]')
        job_description = html.css_first(
            'div[class*="description__text description__text--rich"] section div[class*="show-more-less-html__markup"]'
        )
        return {
            "url": url.strip(),
            "job_posting_company": job_posting_company.text(strip=True)
            if job_posting_company is not None
            else None,
            "job_title": job_title.text(strip=True) if job_title is not None else None,
            "job_description": job_description.text(strip=True, separator="\n")
            if job_description
            else None,
        }
    except Exception as e:
        logging.error(f"Error parsing: {e}")
        return {}


def parse_i(url: str) -> JobData:
    try:
        resp = cloud_scrp(url)
        html = HTMLParser(resp.text)
        job_posting_company = html.css_first('span[class*="css-qcqa6h"] a')
        job_title = html.css_first(
            'div[class*="jobsearch-JobInfoHeader-title-container"]'
        )
        job_description = html.css_first("div#jobDescriptionText")
        return {
            "url": url.strip(),
            "job_posting_company": job_posting_company.text(strip=True).split(".css-")[
                0
            ],
            "job_title": job_title.text(strip=True) if job_title is not None else None,
            "job_description": job_description.text(strip=True, separator="\n")
            if job_description
            else None,
        }
    except Exception as e:
        logging.error(f"Error parsing: {e}")
        return {}


PARSER_CONFIG: dict[str, callable] = {}
