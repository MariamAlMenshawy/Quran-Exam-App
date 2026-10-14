from rest_framework.test import APITestCase
from globals.test_objects import create_user,create_session,create_session_question,create_surah,create_ayah
from .models import Session,SessionQuestion
from django.urls import reverse
from django.core.cache import cache
from django.test import TestCase
from game.views import Leaderboard

# Create your tests here.

class TestGenerateSession(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = create_user()
        self.endpoint = reverse('generate_session')
        self.surah = create_surah()
        for num in range(1,10):
            create_ayah(
                surah=self.surah,
                number_in_surah=num,
                text=f'test ayah {num}',
                juz=1
            )

    def test_generate_random_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge_type": "random"
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,201)
        self.assertEqual(len(res.data["questions"]), 4)
        ayah_ids = [
            question["ayah_id"]
            for question in res.data["questions"]
        ]
        self.assertEqual(len(set(ayah_ids)), 4)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(SessionQuestion.objects.count(), 4)

    def test_generate_specific_surah_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge_type": "specific",
            "surah": 1
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,201)
        self.assertEqual(len(res.data["questions"]), 4)
        ayah_ids = [
            question["ayah_id"]
            for question in res.data["questions"]
        ]
        self.assertEqual(len(set(ayah_ids)), 4)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(SessionQuestion.objects.count(), 4)

    def test_generate_specific_juz_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge_type": "specific",
            "juz": 1
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,201)
        self.assertEqual(len(res.data["questions"]), 4)
        ayah_ids = [
            question["ayah_id"]
            for question in res.data["questions"]
        ]
        self.assertEqual(len(set(ayah_ids)), 4)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(SessionQuestion.objects.count(), 4)
    
    def test_generate_specific_surah_and_juz_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge_type": "specific",
            "surah": 1,
            "juz": 1
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,201)
        self.assertEqual(len(res.data["questions"]), 4)
        ayah_ids = [
            question["ayah_id"]
            for question in res.data["questions"]
        ]
        self.assertEqual(len(set(ayah_ids)), 4)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(SessionQuestion.objects.count(), 4)

    def test_generate_challenge_unauthenticated(self):
        data = {
            "challenge_type": "random",
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,401)

    def test_generate_challenge_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "challenge_type": "...",
            "surah": "",
            "juz": 1
        }
        res = self.client.post(self.endpoint,data,format="json")
        self.assertEqual(res.status_code,400)
        

class TestSubmitSession(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('submit_session')
        self.surah = create_surah(
            surah_number=1,
            name="الفاتحة"
        )
        self.correct_answer = create_ayah(
            surah=self.surah,
            number_in_surah=1,
            text="بسم الله الرحمن الرحيم",
            juz=1
        )
        self.wrong_answer = create_ayah(
            surah=self.surah,
            number_in_surah=2,
            text="الحمد لله رب العالمين",
            juz=1
        )
        self.session = create_session(
            user=self.user,
            challenge_type="specific",
            correct_answer=self.correct_answer
        )
        create_session_question(
            session=self.session,
            ayah=self.correct_answer
        )
        create_session_question(
            session=self.session,
            ayah=self.wrong_answer
        )

    def test_submit_correct_answer(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "session_id": self.session.id,
            "user_answer": self.correct_answer.id
        }
        res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(res.status_code, 200)
        self.session.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.session.user_answer_id,self.correct_answer.id)
        self.assertTrue(self.session.is_correct)
        self.assertEqual(self.user.total_points, 1)

    def test_submit_wrong_answer(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "session_id": self.session.id,
            "user_answer": self.wrong_answer.id
        }
        res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(res.status_code, 200)
        self.session.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.session.user_answer_id,self.wrong_answer.id)
        self.assertFalse(self.session.is_correct)
        self.assertEqual(self.user.total_points, 0)

    def test_submit_unauthenticated(self):
        data = {
            "session_id" : self.session.id,
            "user_answer": self.correct_answer.id
        }
        res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(res.status_code, 401)

    def test_submit_not_exist_session(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "session_id" : 2,
            "user_answer": self.correct_answer.id
        }
        res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(res.status_code, 400)

    def test_submit_session_twice(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "session_id" : self.session.id,
            "user_answer": self.correct_answer.id
        }
        first_res= self.client.post(self.endpoint, data,format="json")
        second_res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(first_res.status_code, 200)
        self.assertEqual(second_res.status_code, 400)

    def test_submit_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "session_id" : self.session.id,
        }
        res= self.client.post(self.endpoint, data,format="json")
        self.assertEqual(res.status_code, 400)
    

class TestUserSessionHistory(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.endpoint = reverse('user_history')
        self.surah = create_surah(
            surah_number=1,
            name='الفاتحة'
        )
        self.ayah1 = create_ayah(
            surah=self.surah,
            number_in_surah=1,
            text='بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
            juz=1
        )
        self.session1 = create_session(
            user=self.user,
            challenge_type='random',
            correct_answer=self.ayah1,
            user_answer=self.ayah1
        )

    def test_history_authenticated_success(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code,200)
        self.assertEqual(len(res.data), 1)

    def test_history_unauthenticated(self):
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code,401)

    def test_history_returns_only_user_sessions(self):
        self.other_user = create_user(email="other@gmail.com")
        self.session2 = create_session(
            user=self.other_user,
            challenge_type='random',
            correct_answer=self.ayah1,
            user_answer=self.ayah1
        )
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_history_empty(self):
        user_without_sessions = create_user(email="emptyhistory@gmail.com")
        self.client.force_authenticate(user=user_without_sessions)
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, [])

class TestLeaderboard(TestCase):

    def setUp(self):
        cache.clear()
        self.user1 = create_user(email="user1@gmail.com")
        self.user2 = create_user(email="user2@gmail.com")
        self.user3 = create_user(email="user3@gmail.com")

        self.user1.total_points = 5
        self.user1.save()

        self.user2.total_points = 10
        self.user2.save()

        self.user3.total_points = 3
        self.user3.save()

    def test_leaderboard_is_ordered_by_points(self):
        top_users = Leaderboard.get_top_users()
        self.assertEqual(
            [user["id"] for user in top_users],
            [self.user2.id, self.user1.id, self.user3.id]
        )
