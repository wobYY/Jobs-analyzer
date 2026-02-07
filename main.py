import pathlib
import random
import time
import urllib.parse as urlparse

import pandas as pd
import pendulum
from icecream import ic

from module.html_parser import PARSER_CONFIG
from utils.logging import get_logger

log = get_logger()

ic.configureOutput(includeContext=True)


# Check if /tmp exists
tmp_dir = pathlib.Path(__file__).parent / "tmp"
if not tmp_dir.exists():
    log.error(
        "/tmp directory does not exist, creating it. Add the csv file with the URLs in the /tmp directory."
    )
    tmp_dir.mkdir(parents=True, exist_ok=True)
    raise RuntimeError(
        "/tmp directory created. Please add the csv file with the URLs in the /tmp directory and run the script again."
    )


def process_urls(**kwargs) -> None:
    # Check if there's any csv file in /tmp
    csv_files = list(tmp_dir.glob("*.csv"))
    if not csv_files:
        log.error(
            "No csv file found in /tmp directory. Please add the csv file with the URLs in the /tmp directory and run the script again."
        )
        raise RuntimeError(
            "No csv file found in /tmp directory. Please add the csv file with the URLs in the /tmp directory and run the script again."
        )
    ic(csv_files)
    for csv_file in csv_files:
        log.info(f"Processing file: {csv_file}")
        # Here you would add the logic to process the URLs in the csv file
        # For example, you could read the csv file and extract the URLs, then perform some operations on them
        # This is just a placeholder for your actual processing logic
        with open(csv_file, "r") as f:
            urls: list[str] = f.readlines()

            if len(urls) == 0:
                log.warning(f"No URLs found in file: {csv_file}")
                continue

            data = []
            parser_hosts = set(PARSER_CONFIG.keys())
            for url in urls:
                # Add your URL processing logic here
                host_name: str | None = None

                url_host = urlparse.urlparse(url.strip()).netloc
                for __parser_domain in parser_hosts:
                    if __parser_domain in url_host:
                        host_name: str = __parser_domain
                        break

                if host_name is None:
                    log.warning(f"No parser found for URL: {url.strip()}")
                    continue

                data.append(
                    PARSER_CONFIG.get(host_name)(
                        url=url.strip(),
                        **kwargs,
                    )
                )

                sleep_time = random.randint(3, 20)
                log.debug(f"Sleeping for {sleep_time} seconds to avoid rate limiting.")
                time.sleep(sleep_time)

            # Create a pandas DataFrame from the data list and save it to a new csv file
            df = pd.DataFrame(
                data,
                columns=[
                    "url",
                    "job_posting_company",
                    "job_title",
                    "job_description",
                ],
            )

            output_dir = tmp_dir / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = (
                output_dir / f"{pendulum.now().to_datetime_string()}_processed.parquet"
            )
            df.to_parquet(output_file, index=False)
            log.info(f"Processed data saved to: {output_file}")


if __name__ == "__main__":
    process_urls()
