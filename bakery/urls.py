from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),
    path('reviews/', views.reviews, name='reviews'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Сброс пароля
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),

    # Продукция (редактирование)
    path('edit/products/', views.edit_products, name='edit_products'),
    path('edit/products/add/', views.product_add, name='product_add'),
    path('edit/products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('edit/products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Редактирование «О нас»
    path('about/edit/new/', views.about_edit_new, name='about_edit_new'),
    path('about/edit/<int:pk>/', views.about_edit, name='about_edit'),

    # Пекарни (адреса)
    path('edit/stores/', views.store_list, name='store_list'),
    path('edit/stores/add/', views.store_add_edit, name='store_add_edit'),
    path('edit/stores/edit/<int:pk>/', views.store_add_edit, name='store_add_edit'),
    path('edit/stores/delete/<int:pk>/', views.store_delete, name='store_delete'),

    # Заказы
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/status/<int:pk>/', views.order_update_status, name='order_update_status'),
    
    # Пользователи
    path('users/', views.user_list, name='user_list'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    
    # Модерация отзывов
    path('reviews/moderation/', views.review_moderation, name='review_moderation'),
    path('reviews/moderate/<int:pk>/', views.review_moderate, name='review_moderate'),
    
    # Отмена заказа
    path('orders/cancel/<int:pk>/', views.order_cancel, name='order_cancel'),
]
