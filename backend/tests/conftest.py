import os, tempfile, pytest
_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"
os.environ["JWT_SECRET"] = "test-secret-not-for-production-use-0123456789"
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

def _h(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": "Campus@123"})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}

@pytest.fixture(scope="session")
def admin(client): return _h(client, "admin@ddugu.demo")
@pytest.fixture(scope="session")
def faculty(client): return _h(client, "faculty@ddugu.demo")
@pytest.fixture(scope="session")
def student(client): return _h(client, "student@ddugu.demo")
