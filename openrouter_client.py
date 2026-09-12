"""OpenRouter requests with explicit, session-owned credentials."""
import json
import urllib.error
import urllib.request

BASE_URL = "https://openrouter.ai/api/v1"


def request(path, *, api_key="", payload=None):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        BASE_URL + path, headers=headers,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=60 if payload else 10) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"OpenRouter request failed (HTTP {exc.code}). Check your key, credits, and model access.") from None
    except (OSError, ValueError):
        raise RuntimeError("OpenRouter could not be reached or returned an invalid response. Please retry.") from None
    if not isinstance(result, dict) or result.get("error"):
        raise RuntimeError("OpenRouter could not complete this request. Check your account and selected model.")
    return result


def model_ids():
    return sorted({item["id"] for item in request("/models").get("data", [])
                   if isinstance(item.get("id"), str)
                   and "text" in item.get("architecture", {}).get("output_modalities", ["text"])})


def chat(messages, *, api_key, model, system=""):
    if not api_key or not model:
        raise RuntimeError("Set an OpenRouter API key and select a model first.")
    result = request("/chat/completions", api_key=api_key, payload={
        "model": model,
        "messages": ([{"role": "system", "content": system}] if system else []) + messages,
    })
    try:
        return result["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("OpenRouter returned no answer. Try another model.") from None
