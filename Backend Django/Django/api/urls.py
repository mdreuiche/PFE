from django.urls import path
from .AuthenticationView import SignUpView, LogiInView, LogoutView, SendResetOTPView, VerifyResetOTPView, ResetPasswordView, AdminLoginView
from .views import NotificationView, PopularServicesView, PopularProvidersView
from .userViews import UserProfileView, UserRequestView, UserCategoryView, UserServicesView, UserProviderView, UserLinkView,EvaluationView, UserFavoriteServicesView, InProgressLinksCountView
from .adminViews import UserView, CategoryView, ServicesView, ProviderView, RequestView, LinkView, AvailableProvidersView, AssignProviderView, ProviderProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




urlpatterns = [
    # Les endpoints pour l'authentification
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogiInView.as_view(), name='signin'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #------------------------------------------------------------------------------------------------- 
    #Endpoint pour la recuperation des informations de l'utilisateur connecté
    path('profile/', UserProfileView.as_view(), name='users'),
    #Endpoint pour la recuperation/ajout/modification/suppression des utilisateurs pour l'administrateur
    path('users/', UserView.as_view(), name='users'), #exemple:http://
    #-------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation/ajout/modification/suppression  des prestataires
    path('providers/', ProviderProfileView.as_view(), name='providers'), #exemple:http://127.0.0.1:8000/providers/?query=Mohamed Dreuiche
    path('provider/', ProviderView.as_view(), name='provider'), #exemple:http://
    path('user-providers/', UserProviderView.as_view(), name='user_providers'),
    #-------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation/ajout/suppression des categories pour l'administateur
    path('categories/', CategoryView.as_view(), name='categories'), #exemple:http://127.0.0.1:8000/categories/?id=1
    #Endpoint pour la recuperation des categories pour l'utilisateur connecté
    path('user-categories/', UserCategoryView.as_view(), name='user_categories'),
    #------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation/ajout/suppression des services
    path('services/', ServicesView.as_view(), name='services'),
    #Endpoint pour la recuperation des services pour l'utilisateur connecté
    path('user-services/', UserServicesView.as_view(), name='user_services'),
    #------------------------------------------------------------------------------------------------- 
    #Endpoint pour la recuperation/creation des demandes de service
    path('requests/', RequestView.as_view(), name='requests'),
    #Endpoint pour la recuperation/creation des demandes de service d'un utilisateur connecté
    path('user-requests/', UserRequestView.as_view(), name='user_requests'),
    #-------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation/ajout/modification/suppression des liens entre les demandes et les prestataires
    path('links/', LinkView.as_view(), name='links'),
    #Endpoint pour la recuperation des liens entre les demandes et les prestataires pour un utilisateur connecté
    path('user-links/', UserLinkView.as_view(), name='user_links'),
    #Endpoint pour la recuperation du nombre de liens en cours pour un utilisateur connecté
    path('in-progress-links-count/', InProgressLinksCountView.as_view(), name='in_progress_links_count'),
    #--------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation/ajout/modification/suppression des services favoris d'un utilisateur
    path('favorite-services/', UserFavoriteServicesView.as_view(), name='favorite_services'),
    #Endpoint pour la recuperation des services les plus populaires
    path('popular-services/', PopularServicesView.as_view(), name='popular_services'),
    #-------------------------------------------------------------------------------------------------
    #Endpoint pour la recuperation des prestataires disponibles
    path('available-providers/', AvailableProvidersView.as_view(), name='available_providers'),
    #Endpoint pour l'attribution d'un prestataire à une demande
    path('assign-providers/', AssignProviderView.as_view(), name='assign_provider'),
    #Endpoint pour la recuperation des prestataires les plus populaires
    path('popular-providers/', PopularProvidersView.as_view(), name='popular_providers'),
    #------------------------------------------------------------------------------------------------- 
    #Endpoint pour l'evaluation d'un link par l'utilisateur
    path('evaluation/', EvaluationView.as_view(), name='evaluation'),
    #------------------------------------------------------------------------------------------------- 
    # Les endpoints pour obtenir et rafraichir un token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),   
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #------------------------------------------------------------------------------------------------- 
    # Les endpoints pour reset password
    path('password-reset/send-otp/', SendResetOTPView.as_view(), name='send_reset_otp'),
    path('password-reset/verify-otp/', VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('password-reset/reset/', ResetPasswordView.as_view(), name='reset_password'), 
    #-------------------------------------------------------------------------------------------------
    # Les endpoints pour les notifications
    path('notifications/', NotificationView.as_view(), name='notifications'), 
]


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Test API Django",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
   