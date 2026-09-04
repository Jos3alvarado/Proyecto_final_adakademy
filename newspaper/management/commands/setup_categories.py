from django.core.management.base import BaseCommand
from newspaper.models import Category, PostType


class Command(BaseCommand):
    help = 'Setup initial categories for different post types'

    def handle(self, *args, **kwargs):
        categories_data = {
            PostType.GOSSIP: [
                {'name': 'Amor y Desamor', 'icon': '💔'},
                {'name': 'Trabajo y Oficina', 'icon': '💼'},
                {'name': 'Familia y Vecinos', 'icon': '👨‍👩‍👧‍👦'},
                {'name': 'Fiestas y Escándalos', 'icon': '🎉'},
            ],
            PostType.PANA_DEBT: [
                {'name': 'Salidas y Fiestas', 'icon': '🍻'},
                {'name': 'Compras Compartidas', 'icon': '🛍️'},
                {'name': 'Alquiler y Gastos', 'icon': '🏠'},
                {'name': 'Gastos de Auto', 'icon': '🚗'},
            ],
            PostType.SERIOUS_DEBT: [
                {'name': 'Préstamos Personales', 'icon': '🏦'},
                {'name': 'Tarjetas de Crédito', 'icon': '💳'},
                {'name': 'Hipotecas', 'icon': '🏠'},
                {'name': 'Gastos Médicos', 'icon': '🚑'},
            ],
        }

        for post_type, categories in categories_data.items():
            for cat_data in categories:
                slug = f"{post_type}-{cat_data['name'].lower().replace(' ', '-')}"
                category, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': f"{cat_data['icon']} {cat_data['name']}",
                        'icon': cat_data['icon'],
                        'post_type': post_type,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Categoría creada: {category.name}"))
                else:
                    self.stdout.write(f"Categoría ya existe: {category.name}")
