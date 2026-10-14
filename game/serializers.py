from rest_framework import serializers
from .models import Session,SessionQuestion
from quran.models import Surah,Ayah
from django.db import transaction

class ChallengeGenerateSerializer(serializers.Serializer):
    challenge_type = serializers.ChoiceField(choices=Session.CHALLENGE_CHOICES)
    surah = serializers.IntegerField(required=False, min_value=1)
    juz = serializers.IntegerField(required=False, min_value=1,max_value=30)

    def validate(self, attrs):
        challenge_type = attrs.get('challenge_type')
        surah = attrs.get('surah')
        juz = attrs.get('juz')

        if challenge_type == 'random':
            if surah is not None or juz is not None:
                raise serializers.ValidationError("Random challenge does not accept surah or juz.")
    
        if challenge_type == 'specific':
            if surah is None and juz is None:
                raise serializers.ValidationError('specific challenge requires a surah or a juz.')
            
            if surah is not None:
                if not Surah.objects.filter(surah_number=surah).exists():
                    raise serializers.ValidationError({'surah':'This surah does not exist.'})

            if juz is not None:
                if not Ayah.objects.filter(juz=juz).exists():
                    raise serializers.ValidationError({'juz':'This juz does not exist.'})

        return attrs
    

class SumbitSessionSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    user_answer = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context['request'].user
        session_id = attrs['session_id']
        user_answer_id = attrs['user_answer']

        try:
            session = Session.objects.get(pk=session_id,user=user)
        except Session.DoesNotExist:
            raise serializers.ValidationError({'session_id': 'Session not found.'})

        if session.user_answer_id is not None:
            raise serializers.ValidationError({'session_id': 'This session has already been submitted.'})

        if not SessionQuestion.objects.filter(session=session,ayah_id=user_answer_id).exists():
            raise serializers.ValidationError({'user_answer': 'Invalid answer for this session.'})
        
        attrs['session'] = session
        return attrs



class UserSessionHistorySerializer(serializers.ModelSerializer):
    surah = serializers.CharField(source='correct_answer.surah.name', read_only=True)
    juz = serializers.IntegerField(source='correct_answer.juz',read_only=True)
    class Meta:
        model = Session
        fields = ['challenge_type','surah','juz','is_correct','created_at',]