import stripe
from datetime import timedelta

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Article, Category, PostType, DebtStatus, UserProfile, Transaction
from .forms import ArticleForm

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_stripe_customer(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.stripe_customer_id:
        return profile.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email or None,
        name=user.get_full_name() or user.username,
    )
    profile.stripe_customer_id = customer.id
    profile.save(update_fields=['stripe_customer_id'])
    return customer.id


def get_subscription_interval(plan_id):
    plan = settings.STRIPE_PLANS.get(plan_id, {})
    return plan.get('interval', 'month')


class LandingView(TemplateView):
    template_name = 'newspaper/landing.html'


class ArticleListView(ListView):
    model = Article
    template_name = 'newspaper/article-list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        queryset = Article.objects.all()
        status = self.request.GET.get('status', 'active').strip()
        if status == 'paid':
            queryset = queryset.filter(is_paid=True)
        elif status == 'active':
            queryset = queryset.filter(is_paid=False)

        post_type = self.request.GET.get('type')
        if post_type in dict(PostType.choices):
            queryset = queryset.filter(post_type=post_type)

        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status', 'active').strip()
        current_type = self.request.GET.get('type', 'gossip')
        current_category = self.request.GET.get('category', '')
        q = self.request.GET.get('q', '').strip()

        active_count = Article.objects.filter(is_paid=False).count()
        paid_count = Article.objects.filter(is_paid=True).count()
        total_count = active_count + paid_count
        health_percentage = int((paid_count / total_count) * 100) if total_count > 0 else 100

        categories = Category.objects.all()
        if current_type in dict(PostType.choices):
            categories = categories.filter(post_type=current_type)

        gossip_count = Article.objects.filter(post_type=PostType.GOSSIP).count()
        pana_count = Article.objects.filter(post_type=PostType.PANA_DEBT).count()
        serious_count = Article.objects.filter(post_type=PostType.SERIOUS_DEBT).count()

        context.update({
            'status': status,
            'current_type': current_type,
            'current_category': current_category,
            'q': q,
            'active_count': active_count,
            'paid_count': paid_count,
            'health_percentage': health_percentage,
            'categories': categories,
            'post_types': PostType.choices,
            'gossip_count': gossip_count,
            'pana_count': pana_count,
            'serious_count': serious_count,
        })
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'newspaper/article-detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        return super().get_object(queryset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_paid:
            if not request.user.is_authenticated or not getattr(request.user, 'profile', None) or not request.user.profile.has_premium_access():
                messages.warning(request, 'Este contenido requiere suscripción premium. Actualiza tu plan para continuar.')
                return redirect('pricing')

        self.object.views_count = F('views_count') + 1
        self.object.save(update_fields=['views_count'])
        self.object.refresh_from_db()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_articles'] = Article.objects.filter(
            category=self.object.category,
            post_type=self.object.post_type
        ).exclude(id=self.object.id)[:4]
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'newspaper/article_form.html'
    success_url = reverse_lazy('article-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            kwargs['post_type'] = self.request.POST.get('post_type', PostType.GOSSIP)
        else:
            kwargs['post_type'] = self.request.GET.get('post_type', PostType.GOSSIP)
        return kwargs

    def get(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not profile.can_create_publication():
            messages.warning(
                request,
                'Has alcanzado el límite de publicaciones gratuitas. Actualiza a Premium para crear ilimitadas.'
            )
            return redirect('pricing')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        if not profile.can_create_publication():
            messages.warning(
                self.request,
                'Has alcanzado el límite de publicaciones gratuitas. Actualiza a Premium para crear ilimitadas.'
            )
            return redirect('pricing')

        form.instance.author = self.request.user
        if form.instance.is_debt:
            form.instance.debt_status = form.instance.debt_status or DebtStatus.PENDING
        messages.success(self.request, "¡Publicación creada! Tu nueva historia quedó registrada.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_types'] = PostType.choices
        context['selected_type'] = self.request.GET.get('post_type', PostType.GOSSIP)
        context['users'] = User.objects.exclude(id=self.request.user.id)
        return context


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'newspaper/article_form.html'
    success_url = reverse_lazy('article-list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs['post_type'] = self.object.post_type
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "¡Publicación actualizada correctamente!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_types'] = PostType.choices
        context['selected_type'] = self.object.post_type
        context['users'] = User.objects.exclude(id=self.request.user.id)
        return context


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
        messages.success(request, "¡Publicación eliminada del tablón!")
        return super().delete(request, *args, **kwargs)


class ArticleTogglePaidView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=self.kwargs.get('pk'))
        if article.author != request.user:
            raise PermissionDenied

        article.is_paid = not article.is_paid
        if article.is_debt:
            article.debt_status = DebtStatus.PAID if article.is_paid else DebtStatus.PENDING
        article.save(update_fields=['is_paid', 'debt_status'] if article.is_debt else ['is_paid'])

        if article.is_paid:
            messages.success(request, f"¡Excelente! '{article.title}' ahora está marcado como pagado.")
            return redirect(f"{reverse('article-list')}?status=paid")

        messages.success(request, f"'{article.title}' se ha reabierto como cuenta activa.")
        return redirect(f"{reverse('article-list')}?status=active")


def pricing_view(request):
    plans = []
    for key, plan in settings.STRIPE_PLANS.items():
        plans.append({
            'id': key,
            'name': plan['name'],
            'price': plan['display_price'],
            'description': 'Acceso completo a funciones premium',
            'features': [
                'Publicaciones ilimitadas',
                'Acceso a contenido premium',
                'Soporte prioritario',
            ],
        })

    return render(request, 'monetization/pricing.html', {
        'plans': plans,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def create_checkout_session(request, plan_id):
    plan = settings.STRIPE_PLANS.get(plan_id)
    if not plan:
        messages.error(request, 'Plan no encontrado')
        return redirect('pricing')

    try:
        customer_id = get_or_create_stripe_customer(request.user)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer=customer_id,
            line_items=[{
                'price': plan['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('payment-success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('payment-cancel')),
            client_reference_id=str(request.user.id),
            metadata={'user_id': str(request.user.id), 'plan_id': plan_id},
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('pricing')


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    plan = None
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            plan_id = session.metadata.get('plan_id')
            plan = settings.STRIPE_PLANS.get(plan_id)
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.stripe_customer_id = profile.stripe_customer_id or session.customer
            profile.stripe_subscription_id = profile.stripe_subscription_id or session.get('subscription')
            profile.activate_premium(get_subscription_interval(plan_id))
            profile.save(update_fields=['stripe_customer_id', 'stripe_subscription_id', 'subscription_type', 'subscription_expires'])
            Transaction.objects.create(
                user=request.user,
                amount=session.amount_total / 100,
                transaction_type='subscription',
                status='completed',
                stripe_payment_id=session.id,
            )
            messages.success(request, '¡Pago completado con éxito! Ahora eres premium 🎉')
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {str(e)}')
    return render(request, 'monetization/success.html', {'plan': plan})


@login_required
def payment_cancel(request):
    messages.warning(request, 'El pago fue cancelado. Puedes intentarlo de nuevo más tarde.')
    return render(request, 'monetization/cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        if user_id:
            profile, created = UserProfile.objects.get_or_create(user_id=user_id)
            profile.stripe_customer_id = profile.stripe_customer_id or session.get('customer')
            profile.stripe_subscription_id = profile.stripe_subscription_id or session.get('subscription')
            profile.activate_premium(get_subscription_interval(plan_id))
            profile.save(update_fields=['stripe_customer_id', 'stripe_subscription_id', 'subscription_type', 'subscription_expires'])
            Transaction.objects.create(
                user_id=user_id,
                amount=session.amount_total / 100,
                transaction_type='subscription',
                status='completed',
                stripe_payment_id=session.id,
            )

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        customer_id = invoice.get('customer')
        if customer_id:
            profile = UserProfile.objects.filter(stripe_customer_id=customer_id).first()
            if profile:
                plan_interval = 'year' if invoice.get('lines', {}).get('data', [])[0].get('plan', {}).get('interval') == 'year' else 'month'
                profile.activate_premium(plan_interval)
                profile.save(update_fields=['subscription_type', 'subscription_expires'])
                Transaction.objects.create(
                    user=profile.user,
                    amount=invoice.get('amount_paid', 0) / 100,
                    transaction_type='subscription',
                    status='completed',
                    stripe_payment_id=invoice.get('payment_intent') or invoice.get('id'),
                )

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        customer_id = invoice.get('customer')
        if customer_id:
            profile = UserProfile.objects.filter(stripe_customer_id=customer_id).first()
            if profile:
                profile.subscription_type = 'free'
                profile.save(update_fields=['subscription_type'])

    return HttpResponse(status=200)
