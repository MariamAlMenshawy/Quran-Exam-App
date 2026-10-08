from rest_framework.test import APITestCase
from globals.test_objects import create_user
from .models import User
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Create your tests here.

class TestLogin(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('login')

    def test_login_valid(self):
        data = {
            "email":"test@gmail.com",
            "password":"test12345"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,200)
        self.assertIn("access",res.data)
        self.assertIn("refresh",res.data)

    def test_login_email_not_exist(self):
        data = {
            "email":"notexist@gmail.com",
            "password":"test12345"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,401)

    def test_login_wrong_password(self):
        data = {
            "email":"test@gmail.com",
            "password":"wrongpassword"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,401)        

    def test_login_empty_password(self):
        data = {
            "email":"test@gmail.com",
            "password":""
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)


class TestTokenRefresh(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('token_refresh')
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)

    def test_refresh_valid(self):
        data = {
            "refresh":self.refresh_token
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,200)
        self.assertIn("access",res.data)

    def test_refresh_invalid(self):
        data = {
            "refresh":".."
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,401)

    def test_refresh_empty(self):
        data = {
            "refresh":""
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)        

    def test_refresh_missing(self):
        data = {}
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)        


class TestRegister(APITestCase):
    def setUp(self):
        self.endpoint = reverse('register')

    def test_register_valid(self):
        data = {
            "full_name":"new user",
            "email":"newuser@gmail.com",
            "password":"newuser12345",
            "confirm_password":"newuser12345"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,201)
        self.assertTrue(User.objects.filter(email="newuser@gmail.com").exists())
        self.assertIn("access",res.data)
        self.assertIn("refresh",res.data)

    def test_register_invalid(self):
        data = {
            "full_name":"new user",
            "email":"newuser@gmail.com",
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)

    def test_register_not_match_password(self):
        data = {
            "full_name":"new user",
            "email":"newuser@gmail.com",
            "password":"newuser12345",
            "confirm_password":"12345"        
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)

    def test_register_existing_email(self):
        self.user = create_user()
        data = {
            "full_name":"test test",
            "email":"test@gmail.com",
            "password":"test12345",
            "confirm_password":"test12345"        
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)


class TestForgetPassword(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('forget_password')

    def test_valid_email(self):
        data = {
            "email":"test@gmail.com"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,200)
        self.assertIn("message",res.data)
        self.assertIn("token",res.data)

    def test_not_exist_email(self):
        data = {
            "email":"notexist@gmail.com"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)
        self.assertIn("email",res.data)

    def test_invalid_email(self):
        data = {
            "email":"test"        
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)

    def test_empty_email(self):
        data = {
            "email":""        
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)


class TestResetPassword(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('reset_password')
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.token = f"{uid}-{token}"

    def test_valid_data(self):
        data = {
            "token": self.token,
            "new_password": "test12345",
            "confirm_password": "test12345"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,200)
        self.assertIn("message",res.data)

    def test_not_match_password(self):
        data = {
            "token": self.token,
            "new_password": "test12345",
            "confirm_password": "12345"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)
        self.assertIn("confirm_password",res.data)

    def test_invalid_token(self):
        data = {
            "token": "...",
            "new_password": "test12345",
            "confirm_password": "test12345"              
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)
        self.assertIn("token",res.data)

    def test_empty_password(self):
        data = {
            "token": self.token,
            "new_password": "",
            "confirm_password": ""              
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)


class TestGetProfile(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('get_profile')

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["full_name"], self.user.full_name)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["total_points"], self.user.total_points)
          
    def test_profile_unauthenticated(self):
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code,401)


class TestUpdateProfile(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('update_profile')

    def test_update_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "full_name": "Edit Name",
            "email": "editemail@gmail.com"
        }
        res = self.client.put(self.endpoint, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["full_name"], "Edit Name")
        self.assertEqual(res.data["email"], "editemail@gmail.com")
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Edit Name")
        self.assertEqual(self.user.email, "editemail@gmail.com")

    def test_update_profile_unauthenticated(self):
        data = {
            "full_name": "Edit Name",
            "email": "editemail@gmail.com"
        }
        res = self.client.put(self.endpoint, data)
        self.assertEqual(res.status_code, 401)


class TestChangePassword(APITestCase):
    def setUp(self):
        self.user = create_user(password="test12345")
        self.endpoint = reverse('change_password')
        
    def test_chenge_password_authenticated_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "test12345",
            "new_password": "newtest12345",
            "confirm_password": "newtest12345"
        }
        res = self.client.put(self.endpoint,data)
        self.assertEqual(res.status_code,200)
        self.assertIn("message",res.data)

    def test_change_password_unauthenticated(self):
        data = {
            "old_password": "test12345",
            "new_password": "newtest12345",
            "confirm_password": "newtest12345"
        }
        res = self.client.put(self.endpoint,data)
        self.assertEqual(res.status_code,401)

    def test_change_password_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "Wrong12345",
            "new_password": "newtest12345",
            "confirm_password": "newtest12345"
        }
        response = self.client.put(self.endpoint, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("old_password", response.data)

    def test_not_match_passwords(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": "test12345",
            "new_password": "newtest12345",
            "confirm_password": "newtest"
        }
        res = self.client.put(self.endpoint,data)
        self.assertEqual(res.status_code,400)
        self.assertIn("confirm_password",res.data)

    