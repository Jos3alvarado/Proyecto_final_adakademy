from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Article, PostType, UserProfile

FREE_MAX_PUBLICATIONS = 3


class ArticlePermissionsTestCase(TestCase):
    def setUp(self):
        self.user_jose = User.objects.create_user(username="Jose", password="Password123")
        self.user_pedro = User.objects.create_user(username="Pedro", password="Password123")
        self.article = Article.objects.create(
            author=self.user_jose,
            title="Carlos me debe 1 Malta",
            content="Contexto gracioso de algoritmia.",
            post_type=PostType.PANA_DEBT,
        )

    def test_landing_page_accessible(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newspaper/landing.html')

    def test_list_view_accessible_by_anonymous_user(self):
        response = self.client.get(reverse('article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newspaper/article-list.html')

    def test_create_article_requires_login(self):
        response = self.client.get(reverse('article-create'))
        self.assertEqual(response.status_code, 302)

    def test_create_article_sets_author_automatically(self):
        self.client.login(username="Jose", password="Password123")
        response = self.client.post(reverse('article-create'), {
            'post_type': PostType.GOSSIP,
            'title': 'Luis me debe 1 Empanada',
            'content': 'Se comió mi empanada y se marchó.',
            'gossip_level': 1,
        })
        self.assertEqual(response.status_code, 302)
        new_article = Article.objects.get(title="Luis me debe 1 Empanada")
        self.assertEqual(new_article.author, self.user_jose)

    def test_unauthorized_user_cannot_update_article(self):
        self.client.login(username="Pedro", password="Password123")
        response = self.client.get(reverse('article-update', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 403)
        response_post = self.client.post(reverse('article-update', kwargs={'pk': self.article.pk}), {
            'post_type': self.article.post_type,
            'title': 'Saboteando la cuenta',
            'content': 'Intento cambiarlo.',
        })
        self.assertEqual(response_post.status_code, 403)

    def test_unauthorized_user_cannot_delete_article(self):
        self.client.login(username="Pedro", password="Password123")
        response = self.client.get(reverse('article-delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 403)
        response_post = self.client.post(reverse('article-delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(response_post.status_code, 403)

    def test_owner_can_update_article(self):
        self.client.login(username="Jose", password="Password123")
        response = self.client.get(reverse('article-update', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 200)
        response_post = self.client.post(reverse('article-update', kwargs={'pk': self.article.pk}), {
            'post_type': self.article.post_type,
            'title': 'Carlos me debe 1 Malta y Galletas',
            'content': 'Añadí galletas al chisme.',
            'amount': '5.00',
            'agreed_payment_date': '2026-12-01',
            'debtor': self.user_pedro.id,
            'debt_status': 'pending',
        })
        self.assertEqual(response_post.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Carlos me debe 1 Malta y Galletas')

    def test_owner_can_delete_article(self):
        self.client.login(username="Jose", password="Password123")
        response = self.client.get(reverse('article-delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 200)
        response_post = self.client.post(reverse('article-delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(response_post.status_code, 302)
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())

    def test_owner_can_toggle_article_paid(self):
        self.client.login(username="Jose", password="Password123")
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_paid)

        response2 = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.article.pk}))
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_paid)

    def test_unauthorized_user_cannot_toggle_article_paid(self):
        self.client.login(username="Pedro", password="Password123")
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 403)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_paid)

    def test_anonymous_user_cannot_toggle_article_paid(self):
        response = self.client.post(reverse('article-toggle-paid', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_paid)


class FreemiumLimitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="FreeUser", password="Password123")
        self.client.login(username="FreeUser", password="Password123")

    def test_free_user_is_blocked_after_limit(self):
        for i in range(FREE_MAX_PUBLICATIONS):
            self.client.post(reverse('article-create'), {
                'post_type': PostType.GOSSIP,
                'title': f'Historia {i}',
                'content': 'contexto',
                'gossip_level': 1,
            })

        self.assertEqual(
            Article.objects.filter(author=self.user).count(),
            FREE_MAX_PUBLICATIONS
        )

        response = self.client.post(reverse('article-create'), {
            'post_type': PostType.GOSSIP,
            'title': 'Historia extra bloqueada',
            'content': 'contexto',
            'gossip_level': 1,
        })
        self.assertRedirects(response, reverse('pricing'))
        self.assertFalse(
            Article.objects.filter(author=self.user, title='Historia extra bloqueada').exists()
        )

    def test_premium_user_has_no_limit(self):
        profile = UserProfile.objects.get(user=self.user)
        profile.activate_premium('month')
        self.assertTrue(profile.has_premium_access())

        for i in range(FREE_MAX_PUBLICATIONS + 2):
            self.client.post(reverse('article-create'), {
                'post_type': PostType.GOSSIP,
                'title': f'Premium historia {i}',
                'content': 'contexto',
                'gossip_level': 1,
            })

        self.assertEqual(
            Article.objects.filter(author=self.user).count(),
            FREE_MAX_PUBLICATIONS + 2
        )
