from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from .models import PaymentRecord, Mailing


@receiver(post_save, sender=PaymentRecord)
def handle_new_model_instance(sender, instance, created, **kwargs):
    if created:
        print(f"Создана новая запись {instance}")
        
        
@receiver(post_save, sender=Mailing)
def mailing_post_save(sender, instance: Mailing, created, **kwargs):
    from .tasks import send_mailing

    if created:
        transaction.on_commit(lambda: send_mailing.apply_async(args=[instance.id], eta=instance.datetime))