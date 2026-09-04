from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PostType(models.TextChoices):
    GOSSIP = 'gossip', 'Chisme Jugoso'
    PANA_DEBT = 'pana_debt', 'Cuentas entre Panas'
    SERIOUS_DEBT = 'serious_debt', 'Deuda Serena'


class GossipLevel(models.IntegerChoices):
    MILD = 1, '🌶️ Suavecito'
    SPICY = 2, '🌶️🌶️ Picante'
    EXTRA_SPICY = 3, '🌶️🌶️🌶️ Extra Picante'


class DebtStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    PAID = 'paid', 'Pagado'
    DISPUTED = 'disputed', 'En Disputa'
    OVERDUE = 'overdue', 'Vencido'


class LegalStatus(models.TextChoices):
    ACTIVE = 'active', 'Activa'
    IN_COLLECTION = 'in_collection', 'En Cobranza'
    RESOLVED = 'resolved', 'Resuelta'


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='📰')
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.GOSSIP)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['post_type', 'name']

    def __str__(self):
        return self.name


class GossipTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#ff00e4')

    class Meta:
        verbose_name = 'Etiqueta de Chisme'
        verbose_name_plural = 'Etiquetas de Chismes'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Título",
        help_text="Ej: 'Carlos me debe 1 Malta'"
    )
    content = models.TextField(
        verbose_name="Contenido",
        help_text="Describe el chisme, la deuda o el acuerdo entre panas."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Autor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False, verbose_name="¿Pagada?")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.GOSSIP)

    is_anonymous = models.BooleanField(default=False)
    gossip_level = models.IntegerField(choices=GossipLevel.choices, default=GossipLevel.MILD)
    gossip_tags = models.ManyToManyField(GossipTag, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    agreed_payment_date = models.DateField(null=True, blank=True)
    debtor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debts'
    )
    debt_status = models.CharField(
        max_length=20,
        choices=DebtStatus.choices,
        default=DebtStatus.PENDING,
        blank=True,
        null=True
    )

    exact_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    guarantee_document = models.FileField(upload_to='guarantees/', null=True, blank=True)
    legal_status = models.CharField(
        max_length=20,
        choices=LegalStatus.choices,
        default=LegalStatus.ACTIVE,
        blank=True,
        null=True
    )

    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post_type', '-created_at']),
            models.Index(fields=['author', 'post_type']),
            models.Index(fields=['debtor', 'debt_status']),
        ]
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'

    def __str__(self):
        return f"{self.get_post_type_display()}: {self.title[:40]}"

    @property
    def is_gossip(self):
        return self.post_type == PostType.GOSSIP

    @property
    def is_debt(self):
        return self.post_type in [PostType.PANA_DEBT, PostType.SERIOUS_DEBT]

    @property
    def debt_days_overdue(self):
        if not self.is_debt:
            return 0
        target_date = self.due_date if self.post_type == PostType.SERIOUS_DEBT else self.agreed_payment_date
        if not target_date:
            return 0
        delta = timezone.now().date() - target_date
        return max(0, delta.days)

    def get_gossip_display_name(self):
        if self.is_gossip and self.is_anonymous:
            return f"👤 Anónimo ({self.created_at.strftime('%b %Y')})"
        return self.author.get_full_name() or self.author.username

    def get_debt_amount(self):
        if self.post_type == PostType.SERIOUS_DEBT:
            return self.exact_amount or 0
        return self.amount or 0

    def calculate_interest(self):
        if self.post_type != PostType.SERIOUS_DEBT or not self.interest_rate:
            return 0
        debt_amount = self.get_debt_amount()
        if debt_amount <= 0:
            return 0
        days_overdue = self.debt_days_overdue
        if days_overdue <= 0:
            return 0
        daily_interest = (debt_amount * self.interest_rate) / 100 / 30
        return round(daily_interest * days_overdue, 2)

    def get_total_debt(self):
        if not self.is_debt:
            return 0
        return round(self.get_debt_amount() + self.calculate_interest(), 2)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('premium', 'Premium'),
            ('creator', 'Content Creator')
        ],
        default='free'
    )
    subscription_expires = models.DateTimeField(null=True, blank=True)
    credits = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def has_premium_access(self):
        return self.subscription_type == 'premium' and self.subscription_expires and self.subscription_expires > timezone.now()

    def can_create_publication(self):
        if self.subscription_type == 'free':
            return self.user.articles.count() < 3
        return True

    def activate_premium(self, interval='month'):
        self.subscription_type = 'premium'
        if interval == 'year':
            self.subscription_expires = timezone.now() + timedelta(days=365)
        else:
            self.subscription_expires = timezone.now() + timedelta(days=30)
        self.save(update_fields=['subscription_type', 'subscription_expires'])

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('subscription', 'Suscripción'),
            ('credit_purchase', 'Compra de créditos'),
            ('content_purchase', 'Compra de contenido'),
            ('commission', 'Comisión'),
            ('refund', 'Reembolso')
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
            ('refunded', 'Reembolsado')
        ],
        default='pending'
    )
    stripe_payment_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.transaction_type}"


class ArticleAnalytics(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='analytics')
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    premium_views = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def update_metrics(self):
        total_views = self.article.views_count
        if total_views > 0:
            self.conversion_rate = round((self.premium_views / total_views) * 100, 2)
        self.save()

    def __str__(self):
        return f"Analytics para {self.article.title[:30]}"
