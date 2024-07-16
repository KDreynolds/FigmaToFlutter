import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

class FigmaClient:
    BASE_URL = "https://api.figma.com/v1"

    def __init__(self):
        self.headers = {
            "X-Figma-Token": os.getenv("FIGMA_PERSONAL_ACCESS_TOKEN")
        }
        self.file_key = os.getenv("FIGMA_FILE_KEY")

    def get_file(self, file_key):
        url = f"{self.BASE_URL}/files/{file_key}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch file: {response.status_code}")

    def get_file_nodes(self, file_key, node_ids):
        url = f"{self.BASE_URL}/files/{file_key}/nodes"
        params = {"ids": ",".join(node_ids)}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch nodes: {response.status_code}")

    def get_image_urls(self, file_key, node_ids, format="png", scale=1):
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {
            "ids": ",".join(node_ids),
            "format": format,
            "scale": scale
        }
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch image URLs: {response.status_code}")

# Usage example
if __name__ == "__main__":
    client = FigmaClient()

    # Get file data
    file_data = client.get_file(client.file_key)
    print(json.dumps(file_data, indent=2))

    # Get specific nodes
    canvas_id = file_data["document"]["children"][0]["id"]
    nodes_data = client.get_file_nodes(client.file_key, [canvas_id])
    print(json.dumps(nodes_data, indent=2))

    # Get image URLs
    image_urls = client.get_image_urls(client.file_key, [canvas_id])
    print(json.dumps(image_urls, indent=2))