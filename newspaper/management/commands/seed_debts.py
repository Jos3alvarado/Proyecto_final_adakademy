import io
from PIL import Image
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from newspaper.models import Article

class Command(BaseCommand):
    help = "Poblar la base de datos con usuarios y deudas de prueba graciosas"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando semillero de datos...")

        # 1. Crear usuarios de prueba con contraseñas
        users_data = [
            {"username": "Jose", "email": "jose@adakademy.com", "pass": "JoseAdakademy2026!"},
            {"username": "Pedro", "email": "pedro@adakademy.com", "pass": "PedroAdakademy2026!"},
            {"username": "Maria", "email": "maria@adakademy.com", "pass": "MariaAdakademy2026!"},
        ]

        users = {}
        for u in users_data:
            user, created = User.objects.get_or_create(username=u["username"], email=u["email"])
            if created:
                user.set_password(u["pass"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario {user.username} creado."))
            else:
                self.stdout.write(f"Usuario {user.username} ya existe.")
            users[u["username"]] = user

        # 2. Limpiar deudas previas para evitar duplicidades
        Article.objects.all().delete()
        self.stdout.write("Deudas previas eliminadas.")

        # 3. Generar imágenes ficticias con Pillow para la evidencia visual
        def get_mock_image(name, color):
            file_obj = io.BytesIO()
            # Crear una imagen mock de 400x300 con el color indicado
            image = Image.new("RGB", (400, 300), color=color)
            image.save(file_obj, "PNG")
            file_obj.seek(0)
            return ContentFile(file_obj.read(), name=name)

        # 4. Crear deudas graciosas
        debts = [
            {
                "author": users["Jose"],
                "title": "Carlos me debe 1 Malta y 1 Cachito",
                "content": "Dijo que me lo pagaba al salir de clases de Algoritmos, pero cruzó la calle corriendo y se montó en un autobús en marcha. Lo vi sonriendo desde la ventana comiéndose el cachito.",
                "image_name": "malta_cachito.png",
                "color": (243, 156, 18) # Amber
            },
            {
                "author": users["Pedro"],
                "title": "Maria me debe 5 copias de Física II",
                "content": "Le saqué las copias de la guía del profesor antes del examen parcial. Dijo que me transfería en la noche, pero desde entonces solo responde mis estados con emojis de carita triste y me evade en la biblioteca.",
                "image_name": "fotocopias.png",
                "color": (79, 172, 254) # Blue
            },
            {
                "author": users["Maria"],
                "title": "Jose me debe 1 Empanada de Cazón",
                "content": "Se la compré caliente en la cantina porque no tenía saldo en el pago móvil. Dijo: 'te la pago mañana sin falta', pero ya han pasado tres semestres, se graduó y todavía estoy esperando.",
                "image_name": "empanada.png",
                "color": (0, 255, 102) # Green
            }
        ]

        for d in debts:
            article = Article.objects.create(
                author=d["author"],
                title=d["title"],
                content=d["content"]
            )
            # Guardar la imagen en el ImageField
            mock_img = get_mock_image(d["image_name"], d["color"])
            article.image.save(d["image_name"], mock_img, save=True)
            self.stdout.write(self.style.SUCCESS(f"Deuda registrada: '{article.title}' de {article.author.username}"))

        self.stdout.write(self.style.SUCCESS("¡Semillero de datos completado exitosamente!"))
