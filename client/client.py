import requests

class SignLanguageClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _url(self, path):
        return f"{self.base_url}{path}"

# Signs #

def get_signs(self, standard=None, hand=None):
    params: dict = {}
    if standard:
        params["standard"] = standard
    if hand:
        params["hand"] = hand
    r = requests.get(self._url("/signs"), params=params)
    r.raise_for_status()
    return r.json()

def get_sign(self, sign_id):
    r = requests.get(self._url(f"/signs/{sign_id}"))
    r.raise_for_status()
    return r.json()

def create_sign(self, word, hand, standard="ASL", description=None):
    payload = {"word": word, "hand": hand, "standard": standard, "description": description}
    r = requests.post(self._url("/signs"), json=payload)
    r.raise_for_status()
    return r.json()

def update_sign(self, sign_id, word, hand, standard="ASL", description=None):
    payload = {"word": word, "hand": hand, "standard": standard, "description": description}
    r = requests.put(self._url(f"/signs/{sign_id}"), json=payload)
    r.raise_for_status()
    return r.json()

def delete_sign(self, sign_id):
        r = requests.delete(self._url(f"/signs/{sign_id}"))
        r.raise_for_status()
        

# Samples #

def get_samples(self, sign_id):
        r = requests.get(self._url(f"/signs/{sign_id}/samples"))
        r.raise_for_status()
        return r.json()

def create_sample(self, sign_id, emg_signal=None, image_url=None):
    payload = {"sign_id": sign_id, "emg_signal": emg_signal, "image_url": image_url}
    r = requests.post(self._url("/samples"), json=payload)
    r.raise_for_status()
    return r.json()


# Stats and Describe #

def get_stats(self):
    r = requests.get(self._url("/stats"))
    r.raise_for_status()
    return r.json()

def describe_sign(self, sign_id):
    r = requests.get(self._url(f"/signs/{sign_id}/describe"))
    r.raise_for_status()
    return r.json()