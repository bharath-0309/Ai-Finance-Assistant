import unittest
from app import create_app, db
from app.models import User
from app.services import chatbot_reply

class FinanceAssistantTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["WTF_CSRF_ENABLED"] = False

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.client.post("/api/register", json={
            "name": "Test Student",
            "email": "student@example.com",
            "password": "secret123"
        })
        self.assertEqual(response.status_code, 201)

    def test_password_is_hashed(self):
        with self.app.app_context():
            user = User(name="Test", email="hash@example.com")
            user.set_password("secret123")
            self.assertNotEqual(user.password_hash, "secret123")
            self.assertTrue(user.check_password("secret123"))

    def test_chatbot(self):
        answer = chatbot_reply("How does the budget work?")
        self.assertIn("budget", answer.lower())

if __name__ == "__main__":
    unittest.main()
