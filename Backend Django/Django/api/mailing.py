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
