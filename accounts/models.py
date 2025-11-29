from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Prošireni profil korisnika sa dodatnim informacijama
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Kontakt informacije
    phone = models.CharField('Telefon', max_length=50, blank=True)
    mobile = models.CharField('Mobilni telefon', max_length=50, blank=True)
    address = models.CharField('Adresa', max_length=255, blank=True)
    city = models.CharField('Grad', max_length=100, blank=True)
    postal_code = models.CharField('Poštanski broj', max_length=20, blank=True)
    
    # Poslovne informacije
    business_number = models.CharField('Poslovni broj', max_length=50, blank=True)
    department = models.CharField('Odeljenje', max_length=100, blank=True)
    position = models.CharField('Pozicija', max_length=100, blank=True)
    
    # Dodatne informacije
    notes = models.TextField('Napomena', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Korisnički profil'
        verbose_name_plural = 'Korisnički profili'
    
    def __str__(self):
        return f'Profil: {self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatski kreira UserProfile kada se kreira novi User"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatski čuva UserProfile kada se čuva User"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
