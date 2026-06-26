from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Article

class DebtPermissionsTestCase(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.user_jose = User.objects.create_user(username="Jose", password="Password123")
        self.user_pedro = User.objects.create_user(username="Pedro", password="Password123")
        
        # Crear una deuda donde el autor es Jose
        self.debt = Article.objects.create(
            author=self.user_jose,
            title="Carlos me debe 1 Malta",
            content="Contexto gracioso de algoritmia."
        )

    def test_list_view_accessible_by_anonymous_user(self):
        """Un usuario anónimo puede ver la lista de deudas."""
        response = self.client.get(reverse('article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newspaper/article-list.html')

    def test_list_view_accessible_by_logged_in_user(self):
        """Cualquiera que inicie sesión puede ver la lista de deudores."""
        self.client.login(username="Pedro", password="Password123")
        response = self.client.get(reverse('article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newspaper/article-list.html')

    def test_create_debt_requires_login(self):
        """No se puede registrar deudas sin haber iniciado sesión."""
        response = self.client.get(reverse('article-create'))
        self.assertEqual(response.status_code, 302)

    def test_create_debt_sets_author_automatically(self):
        """Al guardar la deuda, el autor se asigna automáticamente al usuario logueado."""
        self.client.login(username="Jose", password="Password123")
        response = self.client.post(reverse('article-create'), {
            'title': 'Luis me debe 1 Empanada',
            'content': 'Se comió mi empanada y se marchó.'
        })
        self.assertEqual(response.status_code, 302)  # Redirección exitosa
        
        # Verificar la deuda creada
        new_debt = Article.objects.get(title="Luis me debe 1 Empanada")
        self.assertEqual(new_debt.author, self.user_jose)

    def test_unauthorized_user_cannot_update_debt(self):
        """Un usuario que no sea el autor recibe un error 403 (No autorizado) al intentar editar."""
        self.client.login(username="Pedro", password="Password123")
        response = self.client.get(reverse('article-update', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 403)  # Forbidden

        response_post = self.client.post(reverse('article-update', kwargs={'pk': self.debt.pk}), {
            'title': 'Saboteando la cuenta',
            'content': 'Intento cambiarlo.'
        })
        self.assertEqual(response_post.status_code, 403)

    def test_unauthorized_user_cannot_delete_debt(self):
        """Un deudor o tercero no puede eliminar deudas ajenas (retorna 403)."""
        self.client.login(username="Pedro", password="Password123")
        response = self.client.get(reverse('article-delete', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 403)

        response_post = self.client.post(reverse('article-delete', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response_post.status_code, 403)

    def test_owner_can_update_debt(self):
        """El autor legítimo sí puede modificar la deuda."""
        self.client.login(username="Jose", password="Password123")
        response = self.client.get(reverse('article-update', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 200)

        response_post = self.client.post(reverse('article-update', kwargs={'pk': self.debt.pk}), {
            'title': 'Carlos me debe 1 Malta y Galletas',
            'content': 'Añadí galletas al chisme.'
        })
        self.assertEqual(response_post.status_code, 302)
        self.debt.refresh_from_db()
        self.assertEqual(self.debt.title, 'Carlos me debe 1 Malta y Galletas')

    def test_owner_can_delete_debt(self):
        """El autor legítimo sí puede eliminar (marcar como pagado) la deuda."""
        self.client.login(username="Jose", password="Password123")
        response = self.client.get(reverse('article-delete', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 200)

        response_post = self.client.post(reverse('article-delete', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response_post.status_code, 302)
        self.assertFalse(Article.objects.filter(pk=self.debt.pk).exists())

    def test_owner_can_toggle_debt_paid(self):
        """El autor de la deuda puede marcarla como pagada y reabrirla."""
        self.client.login(username="Jose", password="Password123")
        
        # Marcar como pagada
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 302)
        self.debt.refresh_from_db()
        self.assertTrue(self.debt.is_paid)

        # Reabrir de nuevo
        response2 = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response2.status_code, 302)
        self.debt.refresh_from_db()
        self.assertFalse(self.debt.is_paid)

    def test_unauthorized_user_cannot_toggle_debt_paid(self):
        """Un tercero no autorizado no puede marcar la deuda de otro como pagada (retorna 403)."""
        self.client.login(username="Pedro", password="Password123")
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 403)
        self.debt.refresh_from_db()
        self.assertFalse(self.debt.is_paid)

    def test_anonymous_user_cannot_toggle_debt_paid(self):
        """Un usuario anónimo es redirigido al login si intenta alternar el estado de pago."""
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.debt.pk}))
        self.assertEqual(response.status_code, 302)
        self.debt.refresh_from_db()
        self.assertFalse(self.debt.is_paid)
