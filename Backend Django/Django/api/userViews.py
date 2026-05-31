from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, CategorySerializer, ServicesSerializer, RequestSerializer, ProviderSerializer, NotificationSerializer, LinkSerializer, EvaluationSerializer, ReportSerializer, FavoriteServicesSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import  User, Category, Services, Request, Provider, Link, Notification, Evaluation, Report, FavoriteServices
from django.db import models
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser
from rest_framework import status
from .models import Notification, create_notification, get_available_providers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync  
from django.shortcuts import get_object_or_404
from .views import Notification, send_realtime_notification

#Views pour les utilisateurs (beneficiaires)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification

    def get(self, request):
        user = request.user  # Récupère l'utilisateur connecté
        serializer = UserSerializer(user, context = {'request': request})  # Sérialise l'utilisateur avec le sérialiseur existant
        return Response(serializer.data, status=200)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True,context = {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
#-------------------------------------------------------------------------------------------------
#Views pour les prestataires
class UserProviderView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les prestataires
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            providers = Provider.objects.all()

        else:
            try:
                provider_id = int(search_query)
                providers = Provider.objects.filter(id=provider_id)
            except ValueError:
                providers = Provider.objects.filter(
                    models.Q(fullname__icontains=search_query) |  # Recherche par nom
                    models.Q(service__service_name__icontains=search_query) |  # Recherche par service
                    models.Q(email__iexact=search_query) |  # Recherche exacte sur l'email
                    models.Q(phone__iexact=search_query)  # Recherche exacte sur le téléphone
                )

        serializer = ProviderSerializer(providers, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
#--------------------------------------------------------------------------------------------------
#Views pour les categories
class UserCategoryView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
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

#------------------------------------------------------------------------------------------------- 
#Views pour les services
class UserServicesView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    parser_classes = [MultiPartParser, FormParser]
    
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
#-------------------------------------------------------------------------------------------------
#Views pour les demandes de service (requests)
from datetime import timedelta
from django.utils import timezone

MAX_REQUESTS_PER_WEEK_VIP = 10
MAX_REQUESTS_PER_WEEK_NON_VIP = 3

class UserRequestView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les demandes
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Paramètre de recherche facultatif

        # Filtrer les demandes de l'utilisateur connecté
        requests = Request.objects.filter(user=request.user)

        # Si une recherche est fournie, appliquer un filtre supplémentaire
        if search_query:
            requests = requests.filter(service__service_name__icontains=search_query)

        serializer = RequestSerializer(requests, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter une demande
    def post(self, request):
        service_id = request.data['service']
        if not service_id:
            return Response({"error": "Le champ service est requis."}, status=400)
        
        # 🔍 Vérifier s'il existe déjà une demande en attente pour ce service
        existing_request = Request.objects.filter(
            user=request.user,
            service_id=service_id,
            request_status='pending'  # ou le champ équivalent selon ton modèle
        ).exists()
        if existing_request:
            return Response(
                {"error": "Vous avez déjà une demande en attente pour ce service."},
                status=400
            )

        user = request.user
        now = timezone.now()
        start_of_week = now - timedelta(days=now.weekday())  # Lundi de la semaine
        end_of_week = start_of_week + timedelta(days=7)

        # Compter le nombre de requêtes créées par l'utilisateur cette semaine
        weekly_requests_count = Request.objects.filter(
            user=user,
            request_date__range=(start_of_week, end_of_week)
        ).count()
        # Déterminer la limite selon le statut VIP
        request_limit = MAX_REQUESTS_PER_WEEK_VIP if user.is_vip else MAX_REQUESTS_PER_WEEK_NON_VIP
        if weekly_requests_count >= request_limit:
            return Response({
                "error": f"Vous avez atteint la limite hebdomadaire de {request_limit} demandes."
            }, status=400)

        serializer = RequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
        
            # Récupérer l'objet Service à partir de l'ID
            service = get_object_or_404(Services, service_id=service_id)  # Récupère le service ou renvoie une 404 si non trouvé
        
            # ✅ Envoi d'une notification à l'admin
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                create_notification(admin, f"{request.user.username} a demandé le service de {service.service_name}.")

            send_realtime_notification(f"{request.user.username} a demandé le service de {service.service_name}.")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #modifier une demande
    def put(self, request):
        request_id = request.query_params.get('id', None)
        user_request = Request.objects.get(request_id=request_id)
        serializer = RequestSerializer(user_request, data=request.data, partial=True, context={'request': request})
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
#-------------------------------------------------------------------------------------------------
#Views pour links
class UserLinkView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les liens
    def get(self, request):
        search_query = request.query_params.get('query', None)  # Un seul paramètre pour la recherche

        if not search_query:
            links = Link.objects.filter(request__user=request.user)
        else:
            links = Link.objects.filter(request__user=request.user)(
                models.Q(provider__fullname__icontains=search_query) |  # Recherche par nom du prestataire
                models.Q(request__service__service_name__icontains=search_query)  # Recherche par service
            )

        serializer = LinkSerializer(links, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    
class InProgressLinksCountView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ L'utilisateur doit être connecté
    authentication_classes = [JWTAuthentication]  # ✅ Utilise le JWT pour l'authentification

    def get(self, request):
        # ✅ Filtrer les links "in progress" de l'utilisateur connecté
        in_progress_count = Link.objects.filter(request__user=request.user, status='in progress').count()

        return Response({"in_progress_links_count": in_progress_count}, status=200)
#-----------------------------------------------------------------------------------
#Views pour les evaluations
class EvaluationView(APIView):
    permission_classes = [IsAuthenticated]  # L'utilisateur doit être authentifié
    authentication_classes = [JWTAuthentication]  

    def post(self, request):
        link_id = request.data.get("link_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment")
        
        # Vérification des champs obligatoires
        if not link_id or rating is None or not comment:
            return Response({"error": "link_id, rating et comment sont requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si le link existe
        link = get_object_or_404(Link, link_id=link_id)

        # Vérifier que l'utilisateur connecté est bien le bénéficiaire du service
        if link.request.user != request.user:
            return Response({"error": "Vous ne pouvez évaluer que vos propres services."}, status=status.HTTP_403_FORBIDDEN)

        # Vérifier si une évaluation existe déjà pour ce link
        if Evaluation.objects.filter(link=link).exists():
            return Response(
                {"error": "Ce service a déjà été évalué."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Vérifier que la note est valide
        if rating < 1 or rating > 5:
            return Response({"error": "La note doit être comprise entre 1 et 5."}, status=status.HTTP_400_BAD_REQUEST)
        # Vérifier que le commentaire n'est pas vide
        if not comment.strip():
            return Response({"error": "Le commentaire ne peut pas être vide."}, status=status.HTTP_400_BAD_REQUEST)

        # Créer l'évaluation
        evaluation = Evaluation.objects.create(
            link=link,
            rating=rating,
            comment=comment
        )

        return Response({"message": "Évaluation enregistrée avec succès."}, status=status.HTTP_201_CREATED)
#-------------------------------------------------------------------------------------------------
#Views pour les services preferes:
class UserFavoriteServicesView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que l'utilisateur est authentifié
    authentication_classes = [JWTAuthentication]  # Utilise le JWT pour l'authentification
    #lister les services preferes
    def get(self, request):
        search_query = request.query_params.get('query', None)

        favorite_services = FavoriteServices.objects.filter(user=request.user)
    
        if search_query:
            favorite_services = favorite_services.filter(
                models.Q(service__service_name__icontains=search_query) |
                models.Q(service__service_description__icontains=search_query)
            )

        serializer = FavoriteServicesSerializer(favorite_services, context={'request': request}, many=True)
        return Response(serializer.data, status=200)
    #ajouter un service prefere
    def post(self, request):
        request.data['user'] = request.user.id
        serializer = FavoriteServicesSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    #supprimer un service prefere
    def delete(self, request):
        service_id = request.query_params.get('id', None)
        favorite_service = FavoriteServices.objects.get(service_id=service_id, user=request.user)
        favorite_service.delete()
        return Response(status=204)
#-------------------------------------------------------------------------------------------------