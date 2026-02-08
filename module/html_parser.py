import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from selectolax.parser import HTMLParser

from module.scrapers import cloud_scrp
from utils.encryption import decrypt_data


@dataclass
class JobData:
    url: str
    job_posting_company: str | None
    job_title: str | None
    job_description: str | None


def parser(url: str, response_text: str | None = None, **kwargs) -> JobData:
    # Find the correct parser
    parser_hosts = set(PARSER_CONFIG.keys())
    host_name: str | None = None
    url_host = urlparse(url.strip()).netloc
    for __parser_domain in parser_hosts:
        if __parser_domain in url_host:
            host_name: str = __parser_domain
            break

    if host_name is None:
        logging.warning(f"No parser found for URL: {url.strip()}")
        return JobData(
            url=url.strip(),
            job_posting_company=None,
            job_title=None,
            job_description=None,
        ).__dict__

    return PARSER_CONFIG.get(host_name)(
        url=url.strip(),
        response_text=response_text,
        **kwargs,
    )


def _parse_l(url: str, response_text: str | None = None) -> JobData:
    try:
        if not response_text:
            resp = cloud_scrp(url)

        html = HTMLParser(response_text or resp.text)

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


def _parse_i(url: str, response_text: str | None = None) -> JobData:
    try:
        if not response_text:
            resp = cloud_scrp(url)

        html = HTMLParser(response_text or resp.text)

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


PARSER_CONFIG: dict[str, callable] = {
    decrypt_data(
        b'Ne%C\x1b\x04\xfe\xf8\x8aBp\x19\xf3mYh\x05\xc5\xa9\x16H\xe0\x81\xdc\xa4\x19\xb5\xc6\x05\xd9\x85\x08z\x97\xbb\xe9\xf6?+\xcaC|\r,UVQU\xa6G/\x92\x8d\xdc\xdde\x1d\xeb\xd2p\x89\xdf\xb7\xccB\x8f\xc2\xad\xb5OLc\xccg\xe5f\x18\xc9\xeeL}g\xf7c\\Etl\x08b\x92\xa8\xc8\xc4\xb9\xb4O6d/\x8d\x19\x96\x98\xbc/\xfe\xcb\xf1\x92\x91\x8c\x11\xd5":\xe1\x91\x141\x0e@\xbb\x97\x91\xf8P5\x9dQ\\\xc9/s2\xbc1\xfa))\x93\x1c\xa2\x85\x1c\xfeL\x0b\x90\x9cde\x0e\x97\x92e\xb53\x08\x8bH\xd2+\x1b~\x12\x99\x1f\xe4%\xe1`\x88!\xdb\x87\x99\xcbF\xe8\x9aeb8.CJ\x98\xd4Ro+\\;=3\x1a\xbb%\x86\xa41y#\x90\xa1\t)\x8a\xf7w\x871Asg|\xaeGm\x1e\xe2\xf5\x84\xb1\xae>\xa6\x16\x9a*\xa6\xd9\xa5N\xaeX|\x85\x83z\xcf!kn\x00N\x01\x1a\xea\x98x\r\x15\x93\xca'
    ): _parse_l,
    decrypt_data(
        b'x0\x9c\xe2<\xf6\xfe\xc7\x06\x89\xc2\xec\x8c\x8a\x1eblr\xe1\xaf\xcf\xea3\xebWHwY-g\xfc\x80l3\x83M\x899\xddO\x13^\xa4PO\xc4x\xd7\x0e\xd2"\xc4I\xb2\x98[V\x0c\x93\x17\xdc\xed\xa9\xec"\xfb\xb9\xc4\xfc-\x82\xf7!\xba\xadZ\xc4\xdbV`\xa1\xe8*1W m\xc0\xd9k\xb0\xde\xbcz<\xda\xb9#T\x13;\xd0O\x91\xd9\xe9\x1c_\xc9\xfbm{Q\xd7wTU\x03!\xff\xe2aZ(\xda\x91]\x06\xa29\xa4\xef\x17\xec\xbd%\xd8\xfc\x92Z\xd1\x15\xe4\x9b\x979\xae\xd0s8\x84\xce\xfc\x91d\x87\xb7z~\xe3\x915\xdb\xe4\x8bo\x1db28H\xbe\x9a03\xca\xba\xd0\xc5\xe3\xfb\xba\xe8\x14\'\x92\xa2d\xa0O5\xfc\xd3\x99\t\xc1\xa0LNVt,\x9e^\xd5-\xed\x02\x99.\xea{h\x146\x85A\xeb\x1d\x19\x00\xaa\x00I\xc8\xe0\'\x00!\xbcj\x8d\xa33%"\x16\x91\xa9\xfam-\xfe\xc5\xbd\xb9\x9f\x10\x98\xd1r%"\xabo\xe3'
    ): _parse_i,
}
