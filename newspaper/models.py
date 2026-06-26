from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    title = models.CharField(
        max_length=200, 
        verbose_name="A quién y qué se debe", 
        help_text="Ej: 'Carlos me debe 1 Malta'"
    )
    content = models.TextField(
        verbose_name="El chisme/contexto", 
        help_text="Ej: 'Dijo que me la pagaba al salir de clases de Algoritmos y se fue corriendo'"
    )
    image = models.ImageField(
        upload_to='articles/', 
        blank=True, 
        null=True, 
        verbose_name="La evidencia física", 
        help_text="La foto del culpable comiéndose la malta, o un meme gracioso de cobradera"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='articles', 
        verbose_name="El Acreedor"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha del préstamo"
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="¿Pagada?",
        help_text="Indica si esta deuda ya fue cobrada o perdonada por el acreedor."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"

    def __str__(self):
        return f"{self.title} (Acreedor: {self.author.username})"
