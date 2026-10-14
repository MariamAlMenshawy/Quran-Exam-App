from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Surah
from .serializers import SurahSerializer
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response

# Create your views here.

class GetSurahs(ListAPIView):
    serializer_class = SurahSerializer
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'juz',
                openapi.IN_QUERY,
                description="Filter surahs by juz number (1-30)",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        juz = request.query_params.get('juz')
        if juz is not None:
            try:
                juz = int(juz)
            except (ValueError, TypeError):
                return Response({"error": "Juz must be a valid integer."},status=400)
            if not 1 <= juz <= 30:
                return Response({"error": "Juz must be between 1 and 30."},status=400)
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        juz = self.request.query_params.get('juz')
        if juz is not None:
            return Surah.objects.filter(ayah__juz=juz).distinct()
        return Surah.objects.all()

