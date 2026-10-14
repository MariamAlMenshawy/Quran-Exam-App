from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Session,SessionQuestion
from .serializers import ChallengeGenerateSerializer,SumbitSessionSerializer,UserSessionHistorySerializer
from quran.models import Surah,Ayah
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
import random
from django.core.cache import cache
from accounts.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create your views here.

class GenerateSession(CreateAPIView):
    serializer_class = ChallengeGenerateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        challenge_type = serializer.validated_data['challenge_type']
        surah = serializer.validated_data.get('surah')
        juz = serializer.validated_data.get('juz')
        
        if challenge_type == 'specific':
            if surah is not None and juz is not None:
                cache_key = f'quran:surah:{surah}:juz:{juz}'
                filters = {'surah__surah_number': surah, 'juz': juz}
            elif surah is not None:
                cache_key = f'quran:surah:{surah}'
                filters = {'surah__surah_number': surah}
            else:
                cache_key = f'quran:juz:{juz}'
                filters = {'juz': juz}
        else:                             #random
            cache_key = 'quran:all'
            filters = {}

        ayahs = cache.get(cache_key)

        if ayahs is None:
            print("CACHE MISS")
            ayahs = list(Ayah.objects.filter(**filters))
            cache.set(cache_key, ayahs, timeout=3600)
        else:
            print("CACHE HIT")

        if not ayahs:
            return Response({"detail": "No ayahs found for this challenge."},status=status.HTTP_404_NOT_FOUND)

        target_ayah = random.choice(ayahs)
        previous_ayah = Ayah.objects.filter(surah=target_ayah.surah,numberInSurah=target_ayah.numberInSurah-1).first()
        next_ayah = Ayah.objects.filter(surah=target_ayah.surah,numberInSurah=target_ayah.numberInSurah+1).first()

        excluded_ayahs = [target_ayah.pk]
        if previous_ayah:
            excluded_ayahs.append(previous_ayah.pk)
        if next_ayah:
            excluded_ayahs.append(next_ayah.pk)
            
        wrong_ayahs = []
        for ayah in ayahs:
            if ayah.pk not in excluded_ayahs:
                wrong_ayahs.append(ayah)

        if len(wrong_ayahs) < 3:       #لو السورة اقل من 3 ايات خاطئة 
            needed = 3 - len(wrong_ayahs)   # عدد الايات الناقصةعشان يجيبها من سور تانية
            other_ayahs = Ayah.objects.exclude(surah=target_ayah.surah).exclude(pk__in=excluded_ayahs).exclude(pk__in=[ayah.pk for ayah in wrong_ayahs])
            other_ayahs = list(other_ayahs)
            if len(other_ayahs) < needed:
                return Response({"detail": "Not enough ayahs to generate choices."},status=status.HTTP_400_BAD_REQUEST)
            wrong_ayahs.extend(random.sample(other_ayahs, needed))
        else:
            wrong_ayahs = random.sample(wrong_ayahs, 3)

        choices = [target_ayah] + wrong_ayahs
        random.shuffle(choices) #بتغير ترتيب الاختيارات

        with transaction.atomic():
            session = Session.objects.create(
                user=request.user,
                challenge_type=challenge_type,
                correct_answer=target_ayah
            )
            SessionQuestion.objects.bulk_create([
                SessionQuestion(session=session, ayah=ayah) for ayah in choices
            ])

        response_data = {
            "session_id": session.id,
            "questions": []
        }
        for ayah in choices:
            response_data["questions"].append({
                "ayah_id": ayah.id,
                "text": ayah.text
            })

        if challenge_type == 'specific':
            response_data["surah"] = {
                "surah_number": target_ayah.surah.surah_number,
                "name": target_ayah.surah.name
            }

        if previous_ayah:
            response_data["previous_ayah"] = previous_ayah.text
    
        if next_ayah:
            response_data["next_ayah"] = next_ayah.text
    
        return Response(response_data, status=status.HTTP_201_CREATED)

class SumbitSession(CreateAPIView):
    serializer_class = SumbitSessionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        session_id = serializer.validated_data['session_id']
        user_answer_id = serializer.validated_data['user_answer']
        with transaction.atomic():
            try:
                session = Session.objects.select_for_update().get(pk=session_id,user=user)
            except Session.DoesNotExist:
                return Response({'session_id': 'Session not found.'},status=status.HTTP_404_NOT_FOUND)
            if session.user_answer_id is not None:
                return Response({'session_id': 'This session has already been submitted.'},status=status.HTTP_400_BAD_REQUEST)
            
            answer = Ayah.objects.get(pk=user_answer_id)
            session.user_answer = answer
            session.save(update_fields=['user_answer'])

            is_correct = session.is_correct
            if is_correct:
                user.total_points += 1
                user.save(update_fields=['total_points'])

        if is_correct:
            Leaderboard.invalidate_cache()  #بنمسح ترتيب ال 10 القديم
            top_users = Leaderboard.get_top_users()  #بنحدث الترتيب
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "leaderboard",
                {
                    "type": "leaderboard_update",
                    "data": {
                        "type": "leaderboard_update",
                        "users": top_users
                    }
                }
            )
        else:
            top_users = Leaderboard.get_top_users()
        return Response({'is_correct': is_correct,'correct_answer': session.correct_answer_id},status=status.HTTP_200_OK)


class UserSessionHistory(ListAPIView):
    serializer_class = UserSessionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)


#Leaderboard(Top 10)
class Leaderboard:
    CACHE_KEY = "leaderboard:top10"
    CACHE_TIMEOUT = 300

    @classmethod
    def get_top_users(cls):
        cached_users = cache.get(cls.CACHE_KEY)

        if cached_users is not None:
            return cached_users

        users = User.objects.order_by(
            "-total_points", "id"
        ).values(
            "id", "full_name", "total_points"
        )[:10]
        result = list(users)

        cache.set(cls.CACHE_KEY,result,timeout=cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def invalidate_cache(cls):
        cache.delete(cls.CACHE_KEY)
