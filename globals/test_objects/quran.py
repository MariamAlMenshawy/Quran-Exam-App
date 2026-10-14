from quran.models import Surah, Ayah


def create_surah(
    surah_number=1,
    name="test surah name",
):
    return Surah.objects.create(
        surah_number=surah_number,
        name=name,
    )

def create_ayah(
    surah,
    number_in_surah=1,
    text="Test ayah",
    juz=1,
):
    return Ayah.objects.create(
        surah=surah,
        numberInSurah=number_in_surah,
        text=text,
        juz=juz,
    )
