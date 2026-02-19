import os
import requests
import subprocess


def get_github_access_token():
    hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
    repl_identity = os.environ.get("REPL_IDENTITY")
    web_repl_renewal = os.environ.get("WEB_REPL_RENEWAL")

    if repl_identity:
        x_replit_token = f"repl {repl_identity}"
    elif web_repl_renewal:
        x_replit_token = f"depl {web_repl_renewal}"
    else:
        return None

    if not hostname:
        return None

    try:
        resp = requests.get(
            f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github",
            headers={
                "Accept": "application/json",
                "X_REPLIT_TOKEN": x_replit_token
            },
            timeout=10
        )
        data = resp.json()
        item = data.get("items", [None])[0]
        if not item:
            return None
        settings = item.get("settings", {})
        token = settings.get("access_token") or settings.get("oauth", {}).get("credentials", {}).get("access_token")
        return token
    except Exception:
        return None


def github_api(endpoint, token):
    resp = requests.get(
        f"https://api.github.com{endpoint}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json()
    return None


def get_local_git_info():
    info = {}
    try:
        info["branch"] = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        info["branch"] = "N/A"

    try:
        log_output = subprocess.check_output(
            ["git", "log", "--oneline", "-10"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        info["recent_commits"] = log_output.split("\n") if log_output else []
    except Exception:
        info["recent_commits"] = []

    try:
        status = subprocess.check_output(
            ["git", "status", "--short"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        info["status"] = status.split("\n") if status else []
    except Exception:
        info["status"] = []

    try:
        info["remote"] = subprocess.check_output(
            ["git", "remote", "-v"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        info["remote"] = ""

    return info
