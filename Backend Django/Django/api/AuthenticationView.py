from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from .models import PasswordResetOTP
import random
from django.contrib.auth.hashers import make_password


#SignupView
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Génération des tokens JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User created successfully!",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#AdminloginView
class AdminLoginView(APIView):
    permission_classes = [AllowAny]  # Tout le monde peut tenter de se connecter

    def post(self, request):
        identifier = request.data.get('identifier')  # Peut être email ou username
        password = request.data.get('password')

        try:
            user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()

            if user and check_password(password, user.password):
                if not user.is_staff:  # Vérifie si l'utilisateur est admin
                    return Response({"error": "Access denied. Admins only."}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Admin login successful!",
                    "username": user.username,
                    "email": user.email,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#LoginView    
class LogiInView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier')  # Peut être email ou username
        password = request.data.get('password')

        try:
            # Recherche par email ou username
            user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()
            
            if user and check_password(password, user.password):
                # Génération des tokens JWT
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful!",
                    "username": user.username,
                    "email": user.email,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#LogoutView
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#SendResetOTPView
class SendResetOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            otp = f"{random.randint(100000, 999999)}"  # Générer un OTP à 6 chiffres
            
            # Stocker l'OTP
            PasswordResetOTP.objects.filter(user=user).delete()  # Supprime les anciens OTP
            PasswordResetOTP.objects.create(user=user, otp=otp)

            # Envoyer l'email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'no-reply@example.com',  # Adresse email de l'expéditeur
                [email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
#VerifyResetOTPView       
class VerifyResetOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).first()

            if otp_record and otp_record.is_valid():
                return Response({"message": "OTP verified."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

#ResetPasswordView
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            PasswordResetOTP.objects.filter(user=user).delete()  # Supprimer les OTP après utilisation
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        