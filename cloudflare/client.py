import requests
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class ImageClient:
    def __init__(self) -> None:
        self.headers = {
            "Authorization": "Bearer JacL4qWbA_mTkfA8yiLkU_d_kPVcEiav7oRC8toz",
        }
        self.url = "https://api.cloudflare.com/client/v4/accounts/b2477739be77aa90496d6c0669820012/images/v1"

    def upload_image_from_url(self, url: str):
        files = {
            "url": (None, url),
            "metadata": (None),
            "requireSignedURLs": (None, "false"),
        }
        res = self.post_request(self.url, self.headers, files)
        if not res:
            return None
        return res.json()

    def upload_image(self, image_path: str) -> bool:
        files = {
            "file": open(image_path, "rb"),
        }
        res = self.post_request(self.url, self.headers, files)
        if not res:
            return False
        return True

    def post_request(self, url: str, headers: dict, files: dict) -> requests.Response:
        try:
            res = requests.post(url, headers=headers, files=files, timeout=(3.0, 10.0))
        except requests.exceptions.RequestException as e:
            logger.exception("failed to post", exc_info=e)
            raise RequestError
        else:
            logger.info("post success")
            return res


class RequestError(Exception):
    def __init__(self) -> None:
        pass
