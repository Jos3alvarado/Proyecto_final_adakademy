from django.urls import path
from django.views.generic import TemplateView
from .views import (
    ArticleListView, 
    ArticleDetailView, 
    ArticleCreateView, 
    ArticleUpdateView, 
    ArticleDeleteView,
    ArticleTogglePaidView
)

urlpatterns = [
    path('', ArticleListView.as_view(), name='article-list'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('article/create/', ArticleCreateView.as_view(), name='article-create'),
    path('article/<int:pk>/update/', ArticleUpdateView.as_view(), name='article-update'),
    path('article/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article-delete'),
    path('article/<int:pk>/toggle-paid/', ArticleTogglePaidView.as_view(), name='article-toggle-paid'),
    
    # Static pages with university humor
    path('about/', TemplateView.as_view(template_name='newspaper/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='newspaper/contact.html'), name='contact'),
]
