from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Product, Review, AboutPage, Profile, Order, OrderItem, Store


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_tags', 'cuisine_tags', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'ingredients', 'product_tags', 'cuisine_tags')
    list_editable = ('price',)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'working_hours', 'is_active', 'display_order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'display_order')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'moderation_status', 'created_at')
    list_filter = ('moderation_status', 'rating')
    actions = ['approve_reviews', 'reject_reviews', 'delete_selected_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(moderation_status='approved')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'

    def reject_reviews(self, request, queryset):
        queryset.update(moderation_status='rejected')
    reject_reviews.short_description = 'Отклонить выбранные отзывы'

    def delete_selected_reviews(self, request, queryset):
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Удалено {deleted_count} отзыв(ов).')
    delete_selected_reviews.short_description = 'Удалить выбранные отзывы'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = 'Профиль'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'cancelled_by_customer', 'store', 'total', 'created_at')
    list_filter = ('status', 'cancelled_by_customer', 'created_at', 'store')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    inlines = [OrderItemInline]
    list_editable = ('status',)
