import requests

class Uploader:
    def to_splunk(self, blob: bytes, url: str, token: str):
        headers = {
            "Authorization": f"Splunk {token}",
            "Content-Type": "application/octet-stream"
        }
        r = requests.post(url, headers=headers, data=blob)
        return r.status_code, r.text

    def to_elk(self, blob: bytes, url: str):
        headers = {"Content-Type": "application/octet-stream"}
        r = requests.post(url, headers=headers, data=blob)
        return r.status_code, r.text

