import json
import pathlib
import random
import time
from typing import Any

import pandas as pd
import pendulum
from rich.progress import track

from module.html_parser import parser
from module.llm_processing import request_llm_response
from utils.logging import get_logger

log = get_logger()

# Define the system prompt for the LLM to extract information from the job description
LLM_PROMPT = """The provided message contain the job post information. I want you to, based on the provided job description, extract certain information. The information required and the column name are as follows:
- Is knowing Python required? Mark it as true or false (column name: python_required)
- Is the previous experience required? Mark it as a float based on the amount of years of experience required, if not required, mark it as an empty string (column_name: experience_required)
- Other required programming languages. Extract other programming languages (e.g. C++, Java, etc.) that are REQUIRED as python lists (leave out the, nice to know languages). (column name: other_programming_languages)
- Other required technologies. Extract the technologies that are required (e.g. Databricks, dbt, Spark, etc.) that are REQUIRED as python lists (leave out the nice to know technologies). (column name: required_technologies)
- Nice to know technologies and programming languages. Extract the nice to know technologies and programming languages as python lists. Prefix each one of the technologies with "Tech: " and programming languages with "Lang: " (column name: nice_to_know)

Do not add any comments or any unnecessary text. Just provide the output in a JSON format with the column names as keys and the extracted information as values. If you cannot find any information for a certain key, just mark it as an empty string or an empty list depending on the expected output type. The output should be a valid JSON that can be parsed by Python's json.loads() function."""


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


def scrape_data() -> pd.DataFrame:
    """
    This function scrapes the data from the URLs provided in the csv file in the /tmp directory. It then saves the scraped data to a new parquet file in the /tmp/output directory. The parquet file contains the following columns: url, job_posting_company, job_title, job_description.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped data.

    Raises:
        RuntimeError: If no csv file is found in the /tmp directory.
    """
    # Check if there's any csv file in /tmp
    csv_files = list(tmp_dir.glob("*.csv"))
    if not csv_files:
        log.error(
            "No csv file found in /tmp directory. Please add the csv file with the URLs in the /tmp directory and run the script again."
        )
        raise RuntimeError(
            "No csv file found in /tmp directory. Please add the csv file with the URLs in the /tmp directory and run the script again."
        )

    for csv_file in csv_files:
        log.info(f"Processing file: {csv_file}")
        # Here you would add the logic to process the URLs in the csv file
        # For example, you could read the csv file and extract the URLs, then perform some operations on them
        # This is just a placeholder for your actual processing logic
        with open(csv_file, "r") as f:
            urls: list[str] = f.readlines()

            # Make sure that the urls are not empty strings and that there
            # are URLs
            urls = [url.strip() for url in urls if url.strip() != ""]
            if len(urls) == 0:
                log.warning(f"No URLs found in file: {csv_file}")
                continue

            data = []
            for url in track(urls, description=f"Processing URLs from {csv_file}..."):
                data.append(parser(url=url.strip()))

                sleep_time = random.randint(3, 20)
                log.debug(
                    f"Sleeping for {sleep_time} seconds to avoid getting blocked."
                )
                time.sleep(sleep_time)

            # Create a pandas DataFrame from the data list and save it to a new parquet file
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
                output_dir / f"{pendulum.now().to_datetime_string()}_raw.parquet"
            )
            df.to_parquet(output_file, index=False)
            log.info(f"Processed data saved to: {output_file}")

            return df.copy()


def process_job_descriptions(
    path_to_df: str | pathlib.Path | None = None,
    df: pd.DataFrame | None = None,
    filename: str | pathlib.Path | None = None,
) -> pd.DataFrame:
    if path_to_df is None and not isinstance(df, pd.DataFrame):
        raise ValueError("Either path_to_df or df must be provided.")

    if isinstance(df, pd.DataFrame) and filename is None:
        filename = (
            tmp_dir
            / "output"
            / f"{pendulum.now().to_datetime_string()}_processed.parquet"
        )

    if isinstance(path_to_df, (str, pathlib.Path)):
        df = pd.read_parquet(path_to_df)

    # Process each job description in the DataFrame using the LLM
    extracted_data_dict = []
    for index, row in track(
        df.iterrows(), total=len(df), description="Processing job descriptions..."
    ):
        job_description = row["job_description"]
        response = request_llm_response(
            model="openai/gpt-oss-120b",
            prompt=LLM_PROMPT,
            message=job_description,
            reasoning="high",
        )

        if int(response.status_code) == 200:
            try:
                llm_output: dict[str, Any] = response.json()
                extracted_info: dict[str, Any]
                for output in llm_output.get("output", []):
                    if str(output.get("type")).lower() != "message":
                        continue

                    extracted_info = json.loads(output.get("content", "{}"))
                    extracted_data_dict.append({"url": row["url"], **extracted_info})

            except (json.JSONDecodeError, KeyError) as e:
                log.error(f"Error parsing LLM response for index {index}: {e}")
                continue
        else:
            log.error(
                f"LLM request failed for index {index} with status code {response.status_code}"
            )

    # Store the processed data in a new parquet file
    final_df = df.merge(pd.DataFrame(extracted_data_dict), on="url", how="left")
    __parquet_df = df.merge(
        pd.DataFrame(extracted_data_dict, dtype=str), on="url", how="left"
    )
    __parquet_df.to_parquet(filename, index=False)
    log.info(f"Processed data saved to: {filename}")

    return final_df.copy()


if __name__ == "__main__":
    df = scrape_data()

    process_job_descriptions(df=df)
