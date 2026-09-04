from django.urls import path
from django.views.generic import TemplateView
from .views import (
    LandingView,
    ArticleListView,
    ArticleDetailView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleTogglePaidView,
    pricing_view,
    create_checkout_session,
    payment_success,
    payment_cancel,
    stripe_webhook,
)

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('tablon/', ArticleListView.as_view(), name='article-list'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('article/create/', ArticleCreateView.as_view(), name='article-create'),
    path('article/<int:pk>/update/', ArticleUpdateView.as_view(), name='article-update'),
    path('article/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article-delete'),
    path('article/<int:pk>/toggle-paid/', ArticleTogglePaidView.as_view(), name='article-toggle-paid'),

    path('about/', TemplateView.as_view(template_name='newspaper/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='newspaper/contact.html'), name='contact'),
    path('precios/', pricing_view, name='pricing'),

    path('checkout/<str:plan_id>/', create_checkout_session, name='create-checkout-session'),
    path('payment/success/', payment_success, name='payment-success'),
    path('payment/cancel/', payment_cancel, name='payment-cancel'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
