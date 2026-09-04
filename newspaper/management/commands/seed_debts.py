import io
from PIL import Image
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from newspaper.models import Article, Category, PostType, DebtStatus, LegalStatus, GossipLevel


class Command(BaseCommand):
    help = "Poblar la base de datos con usuarios y publicaciones de prueba graciosas"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando semillero de datos...")

        # 1. Crear usuarios de prueba
        users_data = [
            {"username": "Jose", "email": "jose@adakademy.com", "pass": "JoseAdakademy2026!"},
            {"username": "Pedro", "email": "pedro@adakademy.com", "pass": "PedroAdakademy2026!"},
            {"username": "Maria", "email": "maria@adakademy.com", "pass": "MariaAdakademy2026!"},
            {"username": "Carlos", "email": "carlos@adakademy.com", "pass": "CarlosAdakademy2026!"},
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

        # 2. Evitar duplicar publicaciones (idempotente)
        Article.objects.filter(
            title__in=[
                "Carlos me debe 1 Malta y 1 Cachito",
                "Jose aparecio en la fiesta y nadie le hablo",
                "Maria me debe 5 copias de Fisica II",
                "Pedro no ha pagado el alquiler de este mes",
                "Carlos pidio un prestamo para un PlayStation",
            ]
        ).delete()

        # 3. Generar imagen mock con Pillow
        def get_mock_image(name, color):
            file_obj = io.BytesIO()
            image = Image.new("RGB", (400, 300), color=color)
            image.save(file_obj, "PNG")
            file_obj.seek(0)
            return ContentFile(file_obj.read(), name=name)

        # 4. Crear publicaciones por tipo
        category_gossip = Category.objects.get(slug="gossip-fiestas-y-escándalos")
        category_pana = Category.objects.get(slug="pana_debt-salidas-y-fiestas")
        category_serious = Category.objects.get(
            slug="serious_debt-préstamos-personales"
        )

        # Chisme
        gossip = Article.objects.create(
            author=users["Pedro"],
            title="Jose aparecio en la fiesta y nadie le hablo",
            content=(
                "Jose llego a la fiesta de Algoritmos con una caja de kms para dabarse,\n"
                "pero nadie le hablo porque todos recuerdan que sigue debiendo la malta.\n"
                "Escribo esto de forma anonima por miedo a represalias (no, no es Maria)."
            ),
            post_type=PostType.GOSSIP,
            category=category_gossip,
            gossip_level=GossipLevel.EXTRA_SPICY,
            is_anonymous=True,
        )
        gossip.image.save("fiesta_nadie_hablo.png", get_mock_image("fiesta.png", (79, 172, 254)), save=True)

        # Cuenta entre panas
        pana = Article.objects.create(
            author=users["Jose"],
            title="Carlos me debe 1 Malta y 1 Cachito",
            content=(
                "Dijo que me lo pagaba al salir de clases de Algoritmos, pero cruzo la calle\n"
                "corriendo y se monto en un autobus en marcha. Lo vi sonriendo desde la\n"
                "ventana comiendose el cachito con calma."
            ),
            post_type=PostType.PANA_DEBT,
            category=category_pana,
            amount=3.50,
            agreed_payment_date=timezone.now().date() - timedelta(days=10),
            debtor=users["Carlos"],
            debt_status=DebtStatus.OVERDUE,
        )
        pana.image.save("malta_cachito.png", get_mock_image("malta.png", (243, 156, 18)), save=True)

        # Pana debt 2
        pana2 = Article.objects.create(
            author=users["Pedro"],
            title="Maria me debe 5 copias de Fisica II",
            content=(
                "Le saque las copias de la guia del profesor antes del examen parcial.\n"
                "Dijo que me transferia en la noche, pero desde entonces solo responde mis\n"
                "estados con emojis tristes y me evade en la biblioteca."
            ),
            post_type=PostType.PANA_DEBT,
            category=category_pana,
            amount=2.00,
            agreed_payment_date=timezone.now().date() - timedelta(days=20),
            debtor=users["Maria"],
            debt_status=DebtStatus.OVERDUE,
        )
        pana2.image.save("fotocopias.png", get_mock_image("copias.png", (0, 255, 102)), save=True)

        # Serious debt
        serious = Article.objects.create(
            author=users["Carlos"],
            title="Pedro no ha pagado el alquiler de este mes",
            content=(
                "Compartimos apartamento desde enero y este mes Pedro 'olvido' el\n"
                "alquiler. Ya van dos avisos y va a tocar hablar con su mama."
            ),
            post_type=PostType.SERIOUS_DEBT,
            category=category_serious,
            exact_amount=150.00,
            interest_rate=5.00,
            due_date=timezone.now().date() - timedelta(days=7),
            legal_status=LegalStatus.ACTIVE,
            debt_status=DebtStatus.OVERDUE,
        )
        serious.image.save("alquiler.png", get_mock_image("alquiler.png", (52, 73, 94)), save=True)

        # Serious debt 2
        serious2 = Article.objects.create(
            author=users["Pedro"],
            title="Prestamo para un PlayStation que nunca llego",
            content=(
                "Carlos pidio un prestamo para 'un proyecto de fisica' que resulto ser\n"
                "una PS5. Dice que la paga el mes que viene (septiembre del 2045)."
            ),
            post_type=PostType.SERIOUS_DEBT,
            category=category_serious,
            exact_amount=200.00,
            interest_rate=8.00,
            due_date=timezone.now().date() + timedelta(days=30),
            legal_status=LegalStatus.IN_COLLECTION,
            debt_status=DebtStatus.PENDING,
        )

        self.stdout.write(self.style.SUCCESS(f"Publicaciones creadas: {Article.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("¡Semillero de datos completado exitosamente!"))