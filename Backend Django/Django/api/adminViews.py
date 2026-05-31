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
from .models import Notification, create_notification, get_available_providers, Availability
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync 
from django.shortcuts import get_object_or_404
from .views import Notification, send_realtime_notification

#Views pour les utilisateurs (beneficiaires)
class UserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les utilisateurs
    def get(self, request):
        user_id = request.query_params.get('id', None)
        user_name = request.query_params.get('username', None)

        # Filtrer en fonction des paramètres fournis
        filters = {}
        if user_id:
            filters['id'] = user_id
        if user_name:
            filters['username__icontains'] = user_name  # Recherche insensible à la casse

        users = User.objects.filter(**filters)
        serializer = UserSerializer(users, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter un utilisateur
    def post(self, request):
        many = isinstance(request.data, list)  # Vérifie si les données sont une liste
        serializer = UserSerializer(data=request.data, context = {'request': request}, many = many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #modifier un utilisateur
    def put(self, request):
        user_id = request.query_params.get('id', None)
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    #supprimer un utilisateur
    def delete(self, request):
        user_id = request.query_params.get('id', None)
        user = User.objects.get(id=user_id)
        user.delete()
        return Response(status=204)
#-------------------------------------------------------------------------------------------------    
#Views pour les prestataires
class ProviderProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les prestataires
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            providers = Provider.objects.all()

        else:
            providers = Provider.objects.filter(
                models.Q(fullname__icontains=search_query) |  # Recherche par nom
                models.Q(service__service_name__icontains=search_query) |  # Recherche par service
                models.Q(email__iexact=search_query) |  # Recherche exacte sur l'email
                models.Q(phone__iexact=search_query)  # Recherche exacte sur le téléphone
            )

        serializer = ProviderSerializer(providers, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter un prestataire
    def post(self, request):
        many = isinstance(request.data, list)
        serializer = ProviderSerializer(data=request.data, context={'request': request}, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #modifier un prestataire
    def put(self, request):
        provider_id = request.query_params.get('id', None)
        provider = Provider.objects.get(id=provider_id)
        serializer = ProviderSerializer(provider, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    #supprimer un prestataire
    def delete(self, request):
        provider_id = request.query_params.get('id', None)
        provider = Provider.objects.get(id=provider_id)
        provider.delete()
        return Response(status=204)
 #la recherche par Id:
class ProviderView(APIView):
    permission_classes = [IsAuthenticated,  IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification

    def get(self, request):
        provider_id = request.query_params.get('id', None)

        # Filtrer en fonction des paramètres fournis
        filters = {}
        if provider_id:
            filters['id'] = provider_id

        providers = Provider.objects.filter(**filters)
        serializer = ProviderSerializer(providers, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
#--------------------------------------------------------------------------------------------------
#Views pour les categories
class CategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les categories
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            categories = Category.objects.all()

        else:
            try:
                category_id = int(search_query)
                categories = Category.objects.filter(category_id=category_id)
            except ValueError:
                categories = Category.objects.filter(
                    models.Q(category_name__icontains=search_query) |  # Recherche par nom
                    models.Q(category_description__icontains=search_query)   # Recherche par service
                )

        serializer = CategorySerializer(categories, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter une categorie
    def post(self, request):
        many = isinstance(request.data, list)  # Vérifie si les données sont une liste
        serializer = CategorySerializer(data=request.data, context = {'request': request}, many = many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #supprimer une categorie
    def delete(self, request):
        category_id = request.query_params.get('id', None)
        category = Category.objects.get(category_id=category_id)
        category.delete()
        return Response(status=204)
#--------------------------------------------------------------------------------------------------
#Views pour les services
class ServicesView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    #lister les services
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            services = Services.objects.all()

        else:
            filters = Q(service_name__icontains=search_query) | Q(service_description__icontains=search_query) | Q(category__category_name__icontains=search_query)

            try:
                # Convertir la requête en float si possible (pour la recherche de prix exact)
                price_value = float(search_query)
                filters |= Q(service_price=price_value)
            except ValueError:
                pass  # Ignore si ce n'est pas un nombre valide

            services = Services.objects.filter(filters)

        serializer = ServicesSerializer(services, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter un service
    def post(self, request):
        many = isinstance(request.data, list)  # Vérifie si les données sont une liste
        serializer = ServicesSerializer(data=request.data, context = {'request': request}, many = many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #supprimer un service
    def delete(self, request):
        service_id = request.query_params.get('id', None)
        service = Services.objects.get(service_id=service_id)
        service.delete()
        return Response(status=204)
#-------------------------------------------------------------------------------------------------
#Views pour les demandes de service (requests)
class RequestView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les demandes
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            requests = Request.objects.all()
        else:
            requests = Request.objects.filter(
                models.Q(service__service_name__icontains=search_query)  # Recherche par service
            )

        serializer = RequestSerializer(requests, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter une demande
    def post(self, request):
        many = isinstance(request.data, list)  # Vérifie si les données sont une liste
        serializer = RequestSerializer(data=request.data, context = {'request': request}, many = many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #modifier une demande
    def put(self, request):
        request_id = request.query_params.get('id', None)
        request = Request.objects.get(request_id=request_id)
        serializer = RequestSerializer(request, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    #supprimer une demande
    def delete(self, request):
        request_id = request.query_params.get('id', None)
        request = Request.objects.get(request_id=request_id)
        request.delete()
        return Response(status=204)
#View pour les prestateurs disponibles
from rest_framework import status
class AvailableProvidersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        service_id = request.data.get('service_id')
        selected_dates = request.data.get('selected_dates')  # Liste des dates sélectionnées par l'utilisateur
        
        # Vérification des champs obligatoires
        if not service_id or not selected_dates:
            return Response(
                {"error": "service_id and selected_dates are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtenir la liste des prestataires disponibles
        available_providers = get_available_providers(service_id, selected_dates)

        if available_providers.exists():
            # Construire une réponse avec les prestataires disponibles
            providers_data = [
                {
                    "id": provider.id,
                    "fullname": provider.fullname,
                    "email": provider.email,
                    "phone": provider.phone,
                    "service": provider.service.service_name,
                    "is_disponible": provider.is_disponible,
                }
                for provider in available_providers
            ]
            
            return Response(
                {"available_providers": providers_data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Aucun prestataire disponible pour ces dates."},
                status=status.HTTP_404_NOT_FOUND
            )

class AssignProviderView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        request_id = request.data.get('request_id')
        provider_id = request.data.get('provider_id')

        # Vérifier les champs obligatoires
        if not request_id or not provider_id:
            return Response(
                {"error": "request_id and provider_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer les objets correspondants
        request_instance = get_object_or_404(Request, request_id=request_id)
        provider_instance = get_object_or_404(Provider, id=provider_id)

        # Vérifier si le prestataire est bien disponible
        available_providers = get_available_providers(request_instance.service.service_id, request_instance.selected_dates)

        if provider_instance not in available_providers:
            return Response(
                {"error": "Ce prestataire n'est pas disponible pour les dates sélectionnées."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Assigner le prestataire à la demande
        Link.objects.create(provider=provider_instance, request=request_instance, status='in progress')
        # Ajouter les disponibilités du prestataire pour cette demande
        for date_time in request_instance.selected_dates:
            date, time = date_time.split("T")
            Availability.objects.create(
                provider=provider_instance,
                date=date,
                start_time=time,  # Ajustez selon vos besoins
                end_time=time  # Ajustez selon la durée du service
            )

        provider_instance.save()
        # ✅ Envoi d'une notification à l'utilisateur concerné
        user = request_instance.user
        create_notification(user, f"Un prestataire a été assigné à votre demande de service : {request_instance.service.service_name}.")

        # ✅ Notification en temps réel
        send_realtime_notification(f"Un prestataire a été assigné à la demande de {user.username} pour le service {request_instance.service.service_name}.")

        return Response(
            {"message": f"Le prestataire {provider_instance.fullname} a été assigné avec succès."},
            status=status.HTTP_200_OK
        )
#-------------------------------------------------------------------------------------------------
#Views pour links
class LinkView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les links
    def get(self, request):
        links = Link.objects.all()
        serializer = LinkSerializer(links, context = {'request': request}, many = True)
        return Response(serializer.data, status=200)
    #ajouter un link
    def post(self, request):
        many = isinstance(request.data, list)  # Vérifie si les données sont une liste
        serializer = LinkSerializer(data=request.data, context = {'request': request}, many = many)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #modifier un link
    def put(self, request):
        link_id = request.query_params.get('id', None)
        link = Link.objects.get(link_id=link_id)
        serializer = LinkSerializer(link, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    #supprimer un link
    def delete(self, request):
        link_id = request.query_params.get('id', None)
        link = Link.objects.get(link_id=link_id)
        link.delete()
        return Response(status=204)