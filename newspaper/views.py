from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Article

from django.db.models import Q

class ArticleListView(ListView):
    model = Article
    template_name = 'newspaper/article-list.html'
    context_object_name = 'articles'
    
    def get_queryset(self):
        status = self.request.GET.get('status', 'active').strip()
        if status == 'paid':
            queryset = Article.objects.filter(is_paid=True)
        else:
            queryset = Article.objects.filter(is_paid=False)
            
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', 'active').strip()
        context['q'] = self.request.GET.get('q', '').strip()
        
        # Estadísticas reales
        active_count = Article.objects.filter(is_paid=False).count()
        paid_count = Article.objects.filter(is_paid=True).count()
        total_count = active_count + paid_count
        
        if total_count > 0:
            health_percentage = int((paid_count / total_count) * 100)
        else:
            health_percentage = 100
            
        context['active_count'] = active_count
        context['paid_count'] = paid_count
        context['health_percentage'] = health_percentage
        
        context['recent_articles'] = Article.objects.filter(is_paid=False).order_by('-created_at')[:4]
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'newspaper/article-detail.html'
    context_object_name = 'article'

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    fields = ['title', 'content', 'image']
    template_name = 'newspaper/article-create.html'
    success_url = reverse_lazy('article-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "¡Deuda registrada exitosamente! Que no se te olvide cobrarla.")
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    fields = ['title', 'content', 'image']
    template_name = 'newspaper/article-update.html'
    success_url = reverse_lazy('article-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "¡Deuda modificada correctamente! El deudor ha sido notificado (en espíritu).")
        return super().form_valid(form)

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'newspaper/article-delete.html'
    success_url = reverse_lazy('article-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "¡Deuda cobrada/perdonada! Ha sido removida del tablón de buscados.")
        return super().delete(request, *args, **kwargs)

class ArticleTogglePaidView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=self.kwargs.get('pk'))
        if article.author != request.user:
            raise PermissionDenied
            
        article.is_paid = not article.is_paid
        article.save()
        
        from django.urls import reverse
        if article.is_paid:
            messages.success(request, f"¡Excelente! La cuenta con '{article.title}' ha sido registrada como PAGADA y se ha archivado en tu historial. 🕊️")
            return redirect(f"{reverse('article-list')}?status=paid")
        else:
            messages.success(request, f"La cuenta con '{article.title}' ha sido REABIERTA con éxito y está de vuelta en el tablón activo.")
            return redirect(f"{reverse('article-list')}?status=active")
