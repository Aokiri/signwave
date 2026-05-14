from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)


def test_create_sign():
    r = client.post("/signs", json={"word": "hello", "hand": "right", "standard": "ASL"})
    assert r.status_code == 201
    assert r.json()["word"] == "hello"

def test_list_signs():
    r = client.get("/signs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_get_sign_not_found():
    r = client.get("/signs/99999")
    assert r.status_code == 404

def test_create_and_delete_sign():
    r = client.post("/signs", json={"word": "test_delete", "hand": "left"})
    sign_id = r.json()["id"]
    r = client.delete(f"/signs/{sign_id}")
    assert r.status_code == 204

def test_create_sample():
    sign = client.post("/signs", json={"word": "test_sample", "hand": "both"}).json()
    r = client.post("/samples", json={"sign_id": sign["id"], "emg_signal": "[0.1, 0.2, 0.3]"})
    assert r.status_code == 201

def test_stats_endpoint():
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_signs" in data
    assert "signs_per_hand" in data

def test_filter_signs_by_hand():
    client.post("/signs", json={"word": "filter_test", "hand": "right"})
    r = client.get("/signs", params={"hand": "right"})
    assert r.status_code == 200
    assert all(s["hand"] == "right" for s in r.json())
    
if __name__ == "__main__":
    instructions: str = "Usage: pytest tests/ -v"
    print(instructions)