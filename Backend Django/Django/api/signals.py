from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Evaluation, Link, Request, Provider, Services

@receiver(post_save, sender=Evaluation)
def update_provider_infos(sender, instance, **kwargs):
    """Met à jour le rating du provider après chaque évaluation"""
    provider = instance.link.provider
    provider.update_rating()

@receiver(post_save, sender=Link)
def update_clients_served(sender, instance, created, **kwargs):
    """Met à jour le nombre de clients servis lorsqu'un prestataire est assigné à une demande"""
    if created:
        provider = instance.provider
        provider.clients_served = Link.objects.filter(provider=provider).count()
        provider.save()

@receiver(post_save, sender=Request)
def update_service_requests_count(sender, instance, created, **kwargs):
    """Met à jour le nombre de demandes pour chaque service"""
    if created:
        service = instance.service
        service.requests_count = Request.objects.filter(service=service).count()
        service.save()
