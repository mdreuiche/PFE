from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, CategorySerializer, ServicesSerializer, RequestSerializer, ProviderSerializer, NotificationSerializer, LinkSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import  User, Category, Services, Request, Provider, Link, Notification
from django.db import models
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser
from .models import Notification, create_notification, get_available_providers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync  
from rest_framework import status


#View pour les notifications
class NotificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-notification_date')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Marquer toutes les notifications comme lues"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read."})

def send_realtime_notification(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",  # Groupe WebSocket
        {
            "type": "send_notification",
            "message": message
        }
    )
#View pour les services populaires
class PopularServicesView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        # 🔥 Obtenir les services les plus demandés (triés par `requests_count`)
        popular_services = Services.objects.all().order_by('-request_count')[:10]  # Top 10 services
        serializer = ServicesSerializer(popular_services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
#View pour les prestataires populaires
class PopularProvidersView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # 🔥 Obtenir les prestataires les plus actifs (triés par `clients_served`)
        popular_providers = Provider.objects.all().order_by('-clients_served')[:10]  # Top 10 prestataires
        serializer = ProviderSerializer(popular_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)