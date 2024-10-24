import requests
import os

def download_blob(blob_url, download_path):
    """Download a blob file from the passed URL to a local directory."""
    try:
        response = requests.get(blob_url)
        if response.status_code == 200:
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {blob_url} to {download_path}")
        else:
            raise Exception(f"Failed to download file from {blob_url}. Status code: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error downloading file: {str(e)}")
