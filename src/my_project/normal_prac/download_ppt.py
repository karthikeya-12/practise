import os
import requests
from dotenv import load_dotenv
import time
load_dotenv()


def download_ppt(res_dict: dict):
    # logger.info("Inside the download ppt function")
    try:
        if not isinstance(res_dict, dict):
            # logger.warning("Given parameter named res_dict is not a dict")
            return "Given parameter named res_dict is not a dict"

        generation_id = res_dict.get("generationId")
        if not generation_id:
            raise ValueError("generationId not found in response dictionary")

        # logger.info(f"generationId: {generation_id}")
        url = f"https://public-api.gamma.app/v0.2/generations/{generation_id}"
        # logger.info(url)

        headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("GAMMA_API_KEY")
        }

        export_url = None
        max_retries = 20  # wait up to ~100s
        for attempt in range(max_retries):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            res = response.json()
            # logger.info(f"Attempt {attempt+1}: {res}")

            export_url = res.get("exportUrl")
            if export_url:
                # logger.info(f"Got exportUrl: {export_url}")
                break

            sleep_time = min(2 ** attempt, 30)  # exponential backoff, max 30s
            # logger.info(f"Still pending. Sleeping {sleep_time}s before retry...")
            time.sleep(sleep_time)

        if not export_url:
            raise TimeoutError("exportUrl not available after multiple retries")

        ppt_response = requests.get(export_url, stream=True)
        ppt_response.raise_for_status()

        # Download the file locally
        filename = f"Presentation_{generation_id}.pptx"
        with open(filename, 'wb') as f:
            for chunk in ppt_response.iter_content(chunk_size=8192):
                f.write(chunk)

        # logger.info(f"Successfully downloaded PPT as {filename}")
        return filename

    except Exception as e:
        # logger.error(f"{e.__class__.__name__}: {str(e)}")
        raise e


res = download_ppt({'generationId': 'f6dGItNyBdZKwMcmO3P2l'})
print(res)
