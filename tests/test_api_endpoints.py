import os
# Force testing SQLite database before any imports
os.environ["DATABASE_URL"] = "sqlite:///./test_pathfinder_api.db"

import pytest
from fastapi.testclient import TestClient
from database.connection import engine, Base
from database.seed import seed_database
from api.main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_pathfinder_api.db"):
        try:
            os.remove("./test_pathfinder_api.db")
        except Exception:
            pass

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

def test_careers_endpoint():
    response = client.get("/api/careers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(c["name"] == "AI Engineer" for c in data)

def test_skills_endpoint():
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(s["name"] == "Python" for s in data)

def test_resources_endpoint():
    response = client.get("/api/resources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(r["resource_id"] == "ml_fundamentals_404" for r in data)

def test_auth_and_learner_flow():
    # 1. Register a new user
    user_email = "testlearner@hcltech.com"
    user_password = "supersecretpassword123"
    register_payload = {
        "email": user_email,
        "password": user_password,
        "name": "Test Learner"
    }
    register_resp = client.post("/api/auth/register", json=register_payload)
    assert register_resp.status_code == 201
    user_data = register_resp.json()
    assert user_data["email"] == user_email
    assert "id" in user_data

    # 2. Login
    login_payload = {
        "email": user_email,
        "password": user_password
    }
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}

    # 3. GET /api/auth/me
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == user_email

    # 4. Profile onboarding (POST /api/learners/profile)
    profile_payload = {
        "career_goal": "AI Engineer",
        "experience_level": "beginner",
        "learning_hours_per_week": 12.0,
        "interests": ["Machine Learning", "Neural Networks"],
        "current_skills": ["Python"]
    }
    profile_resp = client.post("/api/learners/profile", json=profile_payload, headers=headers)
    assert profile_resp.status_code == 200
    prof_data = profile_resp.json()
    assert prof_data["career_goal"] == "AI Engineer"
    assert prof_data["experience_level"] == "beginner"

    # 5. Profile fetch (GET /api/learners/profile)
    profile_resp_get = client.get("/api/learners/profile", headers=headers)
    assert profile_resp_get.status_code == 200
    assert profile_resp_get.json()["career_goal"] == "AI Engineer"

    # 6. Skill Gap Analysis (GET /api/skill-gap)
    gap_resp = client.get("/api/skill-gap", headers=headers)
    assert gap_resp.status_code == 200
    gap_data = gap_resp.json()
    assert "required_skills" in gap_data
    assert "priority_skills" in gap_data
    assert "Statistics" in gap_data["priority_skills"]

    # 7. Recommendations (GET /api/recommendations)
    rec_resp = client.get("/api/recommendations", headers=headers)
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert len(rec_data["recommendations"]) > 0
    assert rec_data["user_id"] == user_data["id"]

    # 8. Learning Path Roadmap (GET /api/learning-path)
    path_resp = client.get("/api/learning-path", headers=headers)
    assert path_resp.status_code == 200
    path_data = path_resp.json()
    assert "nodes" in path_data
    assert len(path_data["nodes"]) > 0
    
    first_node = path_data["nodes"][0]
    resource_id_to_complete = first_node["resource_id"]

    # 9. Complete Resource (POST /api/progress/complete)
    comp_payload = {
        "resource_id": resource_id_to_complete,
        "rating": 5.0
    }
    comp_resp = client.post("/api/progress/complete", json=comp_payload, headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert comp_data["status"] == "success"

    # 10. Submit Assessment (POST /api/progress/assessment)
    ass_payload = {
        "skill_name": "Python",
        "score": 0.85
    }
    ass_resp = client.post("/api/progress/assessment", json=ass_payload, headers=headers)
    assert ass_resp.status_code == 200
    ass_data = ass_resp.json()
    assert ass_data["status"] == "success"
    assert ass_data["new_proficiency"] >= 0.5

    # 11. Fetch report (GET /api/progress/report)
    report_resp = client.get("/api/progress/report", headers=headers)
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data["resources_completed"] == 1
    assert "metrics" in report_data
    assert report_data["metrics"]["mastery_percentage"] >= 0.0
