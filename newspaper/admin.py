from django.contrib import admin
from .models import Article, Category, GossipTag, UserProfile, Transaction, ArticleAnalytics


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'is_paid', 'debt_status', 'created_at')
    list_filter = ('post_type', 'is_paid', 'debt_status', 'legal_status')
    search_fields = ('title', 'content', 'author__username', 'category__name')
    raw_id_fields = ('author', 'debtor')
    filter_horizontal = ('gossip_tags',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_type', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('post_type',)


@admin.register(GossipTag)
class GossipTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'credits', 'total_earnings')
    search_fields = ('user__username',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('user__username', 'article__title')


@admin.register(ArticleAnalytics)
class ArticleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('article', 'total_revenue', 'premium_views', 'conversion_rate')
