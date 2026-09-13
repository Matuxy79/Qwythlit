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


def model_catalog():
    """Text-output models with display names and context windows, in catalog order."""
    items = []
    seen = set()
    for item in request("/models").get("data", []):
        model_id = item.get("id")
        if not isinstance(model_id, str) or model_id in seen:
            continue
        if "text" not in item.get("architecture", {}).get("output_modalities", ["text"]):
            continue
        seen.add(model_id)
        items.append({
            "id": model_id,
            "name": item.get("name") or model_id,
            "context_length": item.get("context_length") or 0,
        })
    return items


def model_ids():
    return sorted(item["id"] for item in model_catalog())


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
