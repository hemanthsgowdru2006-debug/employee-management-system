def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_admin_can_view_dashboard(logged_in_client):
    response = logged_in_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_admin_can_add_employee(logged_in_client):
    response = logged_in_client.post("/employees/new", data={
        "name": "Test Employee", "email": "test.employee@example.com",
        "phone": "9876543210", "designation": "Developer", "salary": "45000",
        "joining_date": "2026-01-15", "department_id": ""
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Employee" in response.data

def test_invalid_login(client):
    response = client.post("/login", data={"username": "admin", "password": "wrong"},
                           follow_redirects=True)
    assert b"Invalid username or password" in response.data
