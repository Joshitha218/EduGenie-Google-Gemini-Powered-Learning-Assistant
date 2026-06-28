import pytest
import os
import shutil
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_edugenie.db"
os.environ["SECRET_KEY"] = "test_secret_key_12345"

from backend.app.main import app
from backend.app.database import Base, get_db

# Create test database
TEST_DB_URL = "sqlite:///./test_edugenie.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Setup test tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown test database file
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_edugenie.db"):
        os.remove("./test_edugenie.db")

def test_auth_signup():
    response = client.post(
        "/api/auth/signup",
        json={"UserName": "TestStudent", "Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["UserName"] == "TestStudent"
    assert data["Email"] == "teststudent@example.com"
    assert "UserID" in data

def test_auth_signup_duplicate_email():
    # Attempt to sign up with duplicate email
    response = client.post(
        "/api/auth/signup",
        json={"UserName": "TestStudent2", "Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_auth_login():
    response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Check that HTTP-only cookie was set
    assert "access_token" in response.cookies

def test_auth_login_invalid_credentials():
    response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email" in response.json()["detail"]

def test_get_me_unauthorized():
    client.cookies.clear()
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_get_me_authorized():
    # Log in first to get tokens
    login_response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    token = login_response.json()["access_token"]
    
    # Request with authorization headers
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["Email"] == "teststudent@example.com"
    assert data["UserName"] == "TestStudent"

def test_modules_qa_simulated():
    # Request Q&A which should hit simulation fallback if no API key is specified
    login_response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/modules/qa",
        json={"Question": "What is reinforcement learning?"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "Answer" in data
    assert len(data["RelatedConcepts"]) > 0

def test_modules_explain_simulated():
    # Request Concept explanation which should use the fallback structure
    login_response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/modules/explain",
        json={"Topic": "Machine Learning"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "Definition" in data
    assert "Summary" in data
    assert len(data["Examples"]) > 0

def test_dashboard_stats():
    login_response = client.post(
        "/api/auth/login",
        json={"Email": "teststudent@example.com", "Password": "testpassword123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/history/dashboard/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert data["total_queries"] >= 2  # QA and Explain requests made earlier
    assert "qa" in data["queries_by_type"]
    assert "explain" in data["queries_by_type"]
