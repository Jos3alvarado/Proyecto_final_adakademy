from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from .models import Article, PostType, DebtStatus, UserProfile


@receiver(pre_save, sender=Article)
def update_debt_status(sender, instance, **kwargs):
    if instance.is_debt:
        if instance.post_type == PostType.SERIOUS_DEBT and instance.due_date:
            if instance.due_date < timezone.now().date() and instance.debt_status == DebtStatus.PENDING:
                instance.debt_status = DebtStatus.OVERDUE
        elif instance.post_type == PostType.PANA_DEBT and instance.agreed_payment_date:
            if instance.agreed_payment_date < timezone.now().date() and instance.debt_status == DebtStatus.PENDING:
                instance.debt_status = DebtStatus.OVERDUE


@receiver(post_save, sender=Article)
def notify_debt_reminder(sender, instance, created, **kwargs):
    if instance.is_debt and not created and instance.debt_status == DebtStatus.PENDING:
        if instance.post_type == PostType.PANA_DEBT and instance.agreed_payment_date:
            days_until_due = (instance.agreed_payment_date - timezone.now().date()).days
        elif instance.post_type == PostType.SERIOUS_DEBT and instance.due_date:
            days_until_due = (instance.due_date - timezone.now().date()).days
        else:
            return

        if days_until_due == 3 and instance.author.email:
            send_mail(
                'Recordatorio de deuda: 3 días restantes',
                f'Tu publicación "{instance.title}" vence en 3 días.',
                'noreply@cuentasclaras.com',
                [instance.author.email],
                fail_silently=True,
            )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
