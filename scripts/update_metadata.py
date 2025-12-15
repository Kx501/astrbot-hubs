# scripts/update_metadata.py
import json
import os
import sys
import yaml
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

GITHUB_TOKEN = os.getenv("HUB_TOKEN") or os.getenv("GITHUB_TOKEN")

def load_yaml_content(yaml_content):
    try:
        return yaml.safe_load(yaml_content)
    except Exception:
        return yaml_content if isinstance(yaml_content, dict) else {}

def parse_owner_repo(repo_url: str):
    parts = repo_url.rstrip("/").split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return "", ""

def fetch_repo_info(owner, repo):
    if not (owner and repo):
        return {}
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=5)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return {}

def detect_logo(owner, repo, branch):
    if not (owner and repo):
        return ""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/logo.png"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        r = requests.head(url, headers=headers, timeout=5)
        if r.ok:
            return url
    except Exception:
        pass
    return ""

def convert_to_official_format(plugin_data):
    repo_url = plugin_data.get("repo", "").rstrip("/")
    owner, repo = parse_owner_repo(repo_url)

    # 字典 key 用仓库名，退回 name 或 unknown
    plugin_id = repo or plugin_data.get("name", "unknown_plugin")

    tags = plugin_data.get("tags") or []

    info = fetch_repo_info(owner, repo)
    stars = info.get("stargazers_count") or 0
    updated_at = info.get("pushed_at") or info.get("updated_at")
    if not updated_at:
        updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    branch = info.get("default_branch") or "main"

    logo = detect_logo(owner, repo, branch)

    formatted = {
        "display_name": plugin_data.get("name", ""),
        "desc": plugin_data.get("desc", ""),
        "author": plugin_data.get("author", ""),
        "repo": repo_url,
        "tags": tags,
        "social_link": f"https://github.com/{owner}" if owner else "",
        "stars": stars,
        "version": plugin_data.get("version", ""),
        "updated_at": updated_at,
        "logo": logo,
    }
    return plugin_id, formatted

def update_plugin_metadata(plugin_yaml):
    plugin_data = load_yaml_content(plugin_yaml)

    plugins_file = Path("plugins.json")
    if plugins_file.exists():
        with plugins_file.open("r", encoding="utf-8") as f:
            all_plugins = json.load(f)
    else:
        all_plugins = {}

    plugin_id, formatted_data = convert_to_official_format(plugin_data)
    all_plugins[plugin_id] = formatted_data

    with plugins_file.open("w", encoding="utf-8") as f:
        json.dump(all_plugins, f, ensure_ascii=False, indent=2)

    return plugin_id, formatted_data

if __name__ == "__main__":
    plugin_yaml = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PLUGIN_YAML", "{}")
    plugin_id, updated_data = update_plugin_metadata(plugin_yaml)
    print(f"Updated plugin: {plugin_id}")
    print(json.dumps({plugin_id: updated_data}, ensure_ascii=False, indent=2))
