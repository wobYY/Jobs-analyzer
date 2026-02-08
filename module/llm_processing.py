import json
import logging

import httpx

LMSTUDIO_API_HOST = "http://127.0.0.1:1234"
HTTPX_CLIENT = httpx.Client(
    base_url=LMSTUDIO_API_HOST,
    headers={"Content-Type": "application/json"},
    timeout=3600,
)


def request_llm_response(
    model: str, prompt: str, message: str, **kwargs
) -> httpx.Response:
    try:
        request_body = {
            "model": model,
            "system_prompt": prompt,
            "input": message,
        }
        request_body.update(kwargs)

        return HTTPX_CLIENT.post(
            "/api/v1/chat",
            json=request_body,
        )
    except httpx.RequestError as exc:
        logging.error(f"An error occurred while requesting LLM response: {exc}")
        return httpx.Response(status_code=500, content=str(exc))
