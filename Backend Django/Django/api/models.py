from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.db import models
from django.db.models import Avg


# Création d'un manager personnalisé pour le modèle utilisateur
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email doit être défini')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashage du mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

# Modèle utilisateur personnalisé (table 1)
class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Le mot de passe est stocké de manière sécurisée
    phone = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    person_relative_phone = models.CharField(max_length=15, default='')
    is_vip = models.BooleanField(default=False)
    avatarUrl = models.CharField(max_length=255, blank=True, null=True)    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Champ pour déterminer l'accès à l'admin
    is_superuser = models.BooleanField(default=False)  # Champ pour déterminer si l'utilisateur est un superutilisateur
    date_joined = models.DateTimeField(auto_now_add=True)

    # Champs obligatoires pour l'authentification
    USERNAME_FIELD = 'username'  # Tu peux utiliser email ou username comme champ pour l'authentification
    REQUIRED_FIELDS = ['email']  # Ce champ est requis lors de la création d'un superutilisateur

    objects = UserManager()

    def __str__(self):
        return self.username
#-------------------------------------------------------------------------------------------------------------
#Modele de categorie de services (table 2)
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    category_description = models.TextField()

    def __str__(self):
        return self.category_name
    
#Modele de services (table 3)
class Services(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255)
    service_description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    service_price = models.FloatField()
    service_image = models.ImageField(upload_to='service_images/', default='service_images/default.png') 
    request_count = models.IntegerField(default=0)  # Compteur de demandes pour ce service


    def __str__(self):
        return self.service_name
    
#Modele de services preferes (table 4)
class FavoriteServices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Utilisateur qui ajoute aux favoris
    service = models.ForeignKey(Services, on_delete=models.CASCADE)  # Service ajouté aux favoris
    added_at = models.DateTimeField(auto_now_add=True)  # Date d'ajout

    class Meta:
        unique_together = ('user', 'service')  # Un service ne peut être ajouté qu'une seule fois par utilisateur

    def __str__(self):
        return f"{self.user.username} - {self.service.service_name}"


#Modele de prestataire du service (table 5)
class Provider(models.Model):
    fullname = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, default='1')
    is_disponible = models.BooleanField(default=True)
        
    experience_years = models.IntegerField(default=0)  # Ajout des années d'expérience
    clients_served = models.IntegerField(default=0)  # Ajout du nombre de clients servis
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
    def update_rating(self):
        """Met à jour la moyenne des évaluations de ce provider"""
        avg_rating = Evaluation.objects.filter(link__provider=self).aggregate(Avg('rating'))['rating__avg']
        self.rating_avg = avg_rating if avg_rating is not None else 0
        self.save()
    
    def update_clients_served(self):
        clients_count = Link.objects.filter(provider=self).count()  # Compte le nombre de services fournis
        self.clients_served = clients_count

        self.save()

#-------------------------------------------------------------------------------------------------------------
#Modele de demande de service (table 6)
class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    selected_dates = models.JSONField()
    request_date = models.DateTimeField(auto_now_add=True)
    request_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.user.username} requested {self.service.service_name}"
#-------------------------------------------------------------------------------------------------------------
#Fonction pour obtenir les prestataires disponibles pour un service donné et des dates sélectionnées
# def get_available_providers(service_id, selected_dates):
#     # Étape 1: Filtrer les prestataires qui offrent le service demandé et qui sont disponibles
#     available_providers = Provider.objects.filter(service_id=service_id, is_disponible=True)
    
#     # Étape 2: Exclure les prestataires qui sont déjà liés à une demande aux mêmes dates
#     occupied_providers = Link.objects.filter(
#         request__selected_dates__overlap=selected_dates  # Vérifie si les dates se chevauchent
#     ).values_list('provider_id', flat=True)

#     # Étape 3: Exclure les prestataires occupés
#     free_providers = available_providers.exclude(id__in=occupied_providers)
    
#     return free_providers
def get_available_providers(service_id, selected_dates):
    # Récupérer tous les prestataires du service donné
    providers = Provider.objects.filter(service_id=service_id)

    # Vérifier pour chaque prestataire s'il est libre aux dates demandées
    available_providers = []
    for provider in providers:
        is_available = True
        for date_time in selected_dates:  # selected_dates contient date + heure
            date, time = date_time.split("T")  # Supposons un format "YYYY-MM-DDTHH:MM"
            if Availability.objects.filter(provider=provider, date=date, start_time__lte=time, end_time__gte=time).exists():
                is_available = False
                break

        if is_available:
            available_providers.append(provider)

    return Provider.objects.filter(id__in=[p.id for p in available_providers])

class Availability(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="availabilities")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ("provider", "date", "start_time", "end_time")

#-------------------------------------------------------------------------------------------------------------

#Modele de link entre utilisateur et prestataire (table 7)
class Link(models.Model):
    link_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    # service = models.ForeignKey(Services, on_delete=models.CASCADE)
    linked_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'pending'),
        ('in progress', 'in progress'),
        ('finished', 'finished')
    ], default='pending')

    def __str__(self):
        return f"{self.request.user} linked to {self.provider.fullname}"
    
    
#-------------------------------------------------------------------------------------------------------------
#Modele de note et commentaire(table 8)
class Evaluation(models.Model):
    evaluation_id = models.AutoField(primary_key=True)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1)
    comment = models.TextField()
    evaluation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('link',)  # Empêche plusieurs évaluations sur le même link

    def __str__(self):
        return f"{self.link.request.user.username} rated {self.link.request.service.service_name} with {self.rating} stars"

#Modele de reclamation (table 9)
class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    report_text = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'),('Treated','Treated')], default='Pending')
    report_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reported {self.provider.fullname}"
    
#-------------------------------------------------------------------------------------------------------------
#Modele de paiement (table 10)
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    price = models.FloatField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')], default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} paid {self.link.link_id}"
    
#-------------------------------------------------------------------------------------------------------------
#Modele reset password (table 11)
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # Code OTP à 6 chiffres
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        from datetime import timedelta
        from django.utils.timezone import now
        return now() - self.created_at < timedelta(minutes=10)  # Valide pendant 10 minutes

    def __str__(self):
        return f"OTP for {self.user.email}"
    
#Modele de notification (table 12)
class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_text = models.TextField()
    notification_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} received a notification"
#fonction de notification  
def create_notification(user, message):
    Notification.objects.create(user=user, notification_text=message)
    print(f"✅ Notification envoyée à {user.username}: {message}")