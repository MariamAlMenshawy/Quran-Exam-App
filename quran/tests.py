from rest_framework.test import APITestCase
from django.urls import reverse
from globals.test_objects import create_surah,create_ayah

# Create your tests here.

class TestGetSurahs(APITestCase):
    def setUp(self):
        self.endpoint = reverse('get_surahs')
        self.surah1 = create_surah(
            surah_number=1,
            name="سورة الفاتحة"
        )
        self.surah2 = create_surah(
            surah_number=2,
            name="سورة البقرة"
        )
        self.surah3 = create_surah(
            surah_number=3,
            name="سورة ال عمران"
        )
        create_ayah(surah=self.surah1, number_in_surah=1, juz=1)      # ايه 1 سورة الفاتحة     
        create_ayah(surah=self.surah1, number_in_surah=2, juz=1)      # ايه 2 سورة الفاتحة     
        create_ayah(surah=self.surah2, number_in_surah=1, juz=1)      # ايه 1 سورة البقرة
        create_ayah(surah=self.surah3, number_in_surah=1, juz=2)      # ايه 1 سورة ال عمران    
    
    def test_get_all_surahs(self):
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 3)

    def test_filter_surahs_by_juz(self):
        res = self.client.get(self.endpoint,{'juz': 1})
        self.assertEqual(res.status_code, 200)
        surah_numbers = [surah['surah_number'] for surah in res.data]
        self.assertEqual(set(surah_numbers), {1, 2})
        self.assertEqual(len(surah_numbers), 2)

    def test_filter_surahs_by_juz_no_duplicates(self):
        res = self.client.get(self.endpoint,{'juz': 1})
        surah_numbers = [surah['surah_number'] for surah in res.data]
        self.assertEqual(len(surah_numbers),len(set(surah_numbers)))

    def test_filter_surahs_by_juz_no_results(self):
        res = self.client.get(self.endpoint,{'juz': 30})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_filter_surahs_by_juz_not_between_1_to_30(self):
        res = self.client.get(self.endpoint, {'juz': 31})
        self.assertEqual(res.status_code, 400)
