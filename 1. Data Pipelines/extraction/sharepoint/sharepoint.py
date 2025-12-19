"""
Extrai arquivos Excel do SharePoint via Microsoft Graph e MSAL.
Lista os itens da pasta configurada e grava localmente para consumo posterior.

Author: Gustavo F. Lima
License: MIT
Created: 2025
"""

# ========================
# IMPORTS
# ========================
import os
import requests
from urllib.parse import quote
from msal import ConfidentialClientApplication

# ========================
# CONFIGURATION (ENV VARS)
# ========================
# NEVER hardcode secrets in the code
CLIENT_ID = os.getenv("SP_CLIENT_ID")
CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
TENANT_ID = os.getenv("SP_TENANT_ID")

SITE_HOST = os.getenv("SP_SITE_HOST")        # e.g. redeoba.sharepoint.com
SITE_NAME = os.getenv("SP_SITE_NAME")        # e.g. analytics

# Relative path inside the SharePoint document library
DRIVE_RELATIVE_FOLDER = os.getenv("SP_FOLDER_PATH")

# Local folder to save downloaded files
LOCAL_DOWNLOAD_PATH = os.getenv(
    "SP_LOCAL_PATH",
    "./data/sharepoint"
)

# File extensions to download
EXCEL_EXTS = (".xlsx", ".xls", ".xlsm")

# ========================
# VALIDATION
# ========================
required_envs = [
    CLIENT_ID,
    CLIENT_SECRET,
    TENANT_ID,
    SITE_HOST,
    SITE_NAME,
    DRIVE_RELATIVE_FOLDER
]

if not all(required_envs):
    raise EnvironmentError(
        "One or more required environment variables are missing. "
        "Check SP_CLIENT_ID, SP_CLIENT_SECRET, SP_TENANT_ID, "
        "SP_SITE_HOST, SP_SITE_NAME, SP_FOLDER_PATH."
    )

# ========================
# AUTHENTICATION (MSAL)
# ========================
def get_access_token() -> str:
    """
    Authenticate against Azure AD and return an access token
    for Microsoft Graph API.
    """
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    scopes = ["https://graph.microsoft.com/.default"]

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )

    token_result = app.acquire_token_for_client(scopes)

    if "access_token" not in token_result:
        raise RuntimeError(
            f"Failed to acquire token: "
            f"{token_result.get('error_description')}"
        )

    return token_result["access_token"]

# ========================
# GRAPH API HELPERS
# ========================
def graph_get(url: str, headers: dict, params=None) -> dict:
    """
    Perform a GET request to Microsoft Graph API.
    """
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=60
    )
    response.raise_for_status()
    return response.json()

def graph_download(url: str, headers: dict, destination: str):
    """
    Download a file from Microsoft Graph API using streaming.
    """
    with requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=300
    ) as response:
        response.raise_for_status()
        with open(destination, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

# ========================
# MAIN EXECUTION
# ========================
def main():
    """
    Main execution flow:
    1. Authenticate
    2. Resolve siteId
    3. Resolve driveId
    4. List files in target folder
    5. Download Excel files
    """

    # Ensure local directory exists
    os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)

    # Authenticate and prepare headers
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    # ------------------------
    # 1) Get siteId
    # ------------------------
    site_url = (
        f"https://graph.microsoft.com/v1.0/sites/"
        f"{SITE_HOST}:/sites/{SITE_NAME}"
    )
    site = graph_get(site_url, headers)
    site_id = site["id"]

    print(f"[INFO] siteId resolved")

    # ------------------------
    # 2) Get default driveId
    # ------------------------
    drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
    drive = graph_get(drive_url, headers)
    drive_id = drive["id"]

    print(f"[INFO] driveId resolved")

    # ------------------------
    # 3) List folder items
    # ------------------------
    encoded_path = quote(DRIVE_RELATIVE_FOLDER.strip("/"), safe="/")
    children_url = (
        f"https://graph.microsoft.com/v1.0/drives/"
        f"{drive_id}/root:/{encoded_path}:/children"
    )

    items = graph_get(children_url, headers).get("value", [])

    excel_items = [
        item for item in items
        if item.get("file")
        and item["name"].lower().endswith(EXCEL_EXTS)
    ]

    if not excel_items:
        print("[WARN] No Excel files found.")
        return

    # ------------------------
    # 4) Download files
    # ------------------------
    print(f"[INFO] Downloading {len(excel_items)} Excel file(s)...")

    for item in excel_items:
        file_name = item["name"]
        item_id = item["id"]
        download_url = (
            f"https://graph.microsoft.com/v1.0/drives/"
            f"{drive_id}/items/{item_id}/content"
        )
        destination = os.path.join(LOCAL_DOWNLOAD_PATH, file_name)

        print(f" - Downloading {file_name}")
        graph_download(download_url, headers, destination)

    print("✅ Download completed successfully.")

# ========================
# ENTRY POINT
# ========================
if __name__ == "__main__":
    main()
