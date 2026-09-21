import requests
from django.core.management.base import BaseCommand
from quran.models import Surah, Ayah

class Command(BaseCommand):
    help = "Import Quran data from Al-Quran Cloud API"

    def handle(self, *args, **options):
        res = requests.get("https://api.alquran.cloud/v1/quran/quran-uthmani")

        if res.status_code != 200:
            print("Failed to fetch Quran data")
            return

        data = res.json()
        surahs = data["data"]["surahs"]

        for surah_data in surahs:
            surah, created = Surah.objects.get_or_create(
                surah_number = surah_data["number"],
                defaults = {
                    "name" : surah_data["name"]
                }
            )

            ayahs = surah_data["ayahs"]
            for ayah_data in ayahs:
                ayah, created = Ayah.objects.get_or_create(
                    surah = surah,
                    numberInSurah = ayah_data["numberInSurah"],
                    defaults = {
                        "text" : ayah_data["text"],
                        "juz" : ayah_data["juz"],
                    }
                )

        print("Quran data imported successfully")
