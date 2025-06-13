from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from .models import PaymentRecord, Mailing


@receiver(post_save, sender=PaymentRecord)
def handle_new_model_instance(sender, instance, created, **kwargs):
    from .tasks import check_payment_request
    
    if created:
        transaction.on_commit(lambda: check_payment_request.apply_async(args=[instance.payment_id], countdown=120))
        
        
@receiver(post_save, sender=Mailing)
def mailing_post_save(sender, instance: Mailing, created, **kwargs):
    from .tasks import send_mailing

    if created:
        transaction.on_commit(lambda: send_mailing.apply_async(args=[instance.id], eta=instance.datetime))
        
        
