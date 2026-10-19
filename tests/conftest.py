import pytest
from app import create_app, db

@pytest.fixture()
def app(tmp_path):
    path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret",
                      "SQLALCHEMY_DATABASE_URI": f"sqlite:///{path.as_posix()}"})
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def logged_in_client(client):
    client.post("/login", data={"username": "admin", "password": "Admin123!"})
    return client
