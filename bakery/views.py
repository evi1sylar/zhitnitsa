from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from .models import Product, Review, AboutPage, Profile, Order, OrderItem, Store
from .decorators import staff_required
from .utils import validate_image_file


def home(request):
    return render(request, 'bakery/home.html')


def about(request):
    about_page = AboutPage.objects.first()
    stores = Store.objects.filter(is_active=True)
    return render(request, 'bakery/about.html', {'about_page': about_page, 'stores': stores})


def products(request):
    """Список продукции с фильтрацией по тегам."""
    # Фильтрация по тегам
    product_tag = request.GET.get('product_tag', '').strip()
    cuisine_tag = request.GET.get('cuisine_tag', '').strip()
    
    products_list = Product.objects.all()
    if product_tag:
        products_list = products_list.filter(product_tags__icontains=product_tag)
    if cuisine_tag:
        products_list = products_list.filter(cuisine_tags__icontains=cuisine_tag)
    
    # Получаем уникальные теги за один запрос
    all_products = Product.objects.values_list('product_tags', 'cuisine_tags')
    all_product_tags = set()
    all_cuisine_tags = set()
    for product_tags, cuisine_tags in all_products:
        if product_tags:
            all_product_tags.update(tag.strip().lower() for tag in product_tags.split(',') if tag.strip())
        if cuisine_tags:
            all_cuisine_tags.update(tag.strip().lower() for tag in cuisine_tags.split(',') if tag.strip())
    
    # Подготавливаем теги для каждого продукта
    for product in products_list:
        product.product_tags_list = [tag.strip() for tag in (product.product_tags or '').split(',') if tag.strip()]
        product.cuisine_tags_list = [tag.strip() for tag in (product.cuisine_tags or '').split(',') if tag.strip()]
    
    return render(request, 'bakery/products.html', {
        'products': products_list,
        'product_tag': product_tag,
        'cuisine_tag': cuisine_tag,
        'all_product_tags': sorted(all_product_tags),
        'all_cuisine_tags': sorted(all_cuisine_tags),
    })


def reviews(request):
    # Показываем только одобренные отзывы
    reviews_list = Review.objects.filter(moderation_status='approved')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Только авторизованные пользователи могут оставлять отзывы.')
            return redirect('login')
        author = request.POST.get('author', '').strip()
        text = request.POST.get('text', '').strip()
        rating = int(request.POST.get('rating', 5))
        if author and text:
            # Отзыв отправляется на модерацию
            Review.objects.create(
                author=author, 
                text=text, 
                rating=rating,
                moderation_status='pending'
            )
            messages.success(request, 'Спасибо за отзыв! Он появится после модерации.')
            return redirect('reviews')
    return render(request, 'bakery/reviews.html', {'reviews': reviews_list})


# --- Управление продукцией (только для staff/admin) ---

@staff_required
def edit_products(request):
    products_list = Product.objects.all()
    return render(request, 'bakery/edit_products.html', {'products': products_list})


@staff_required
def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        ingredients = request.POST.get('ingredients', '').strip()
        product_tags = request.POST.get('product_tags', '').strip()
        cuisine_tags = request.POST.get('cuisine_tags', '').strip()
        price = request.POST.get('price', '0').strip()
        image = request.FILES.get('image')
        
        # Валидация изображения
        if image:
            try:
                validate_image_file(image)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('edit_products')
        
        if name and description:
            try:
                Product.objects.create(
                    name=name,
                    description=description,
                    ingredients=ingredients,
                    product_tags=product_tags,
                    cuisine_tags=cuisine_tags,
                    price=price or 0,
                    image=image,
                )
                messages.success(request, f'Продукт «{name}» добавлен!')
                return redirect('edit_products')
            except Exception as e:
                messages.error(request, f'Ошибка при добавлении продукта: {str(e)}')
    return render(request, 'bakery/product_form.html', {'action': 'Добавить'})


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.description = request.POST.get('description', '').strip()
        product.ingredients = request.POST.get('ingredients', '').strip()
        product.product_tags = request.POST.get('product_tags', '').strip()
        product.cuisine_tags = request.POST.get('cuisine_tags', '').strip()
        product.price = request.POST.get('price', '0').strip() or 0
        image = request.FILES.get('image')
        
        # Валидация изображения
        if image:
            try:
                validate_image_file(image)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('product_edit', pk=pk)
        
        if image:
            product.image = image
        product.save()
        messages.success(request, f'Продукт «{product.name}» сохранён!')
        return redirect('edit_products')
    price_str = str(product.price) if product.price else ''
    return render(request, 'bakery/product_form.html', {'product': product, 'action': 'Изменить', 'price_str': price_str})


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Продукт «{name}» удалён.')
        return redirect('edit_products')
    return render(request, 'bakery/product_confirm_delete.html', {'product': product})


# --- Редактирование страницы «О нас» ---

@staff_required
def about_edit_new(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if title and content:
            AboutPage.objects.create(title=title, content=content)
            messages.success(request, 'Страница «О нас» создана!')
            return redirect('about')
    return render(request, 'bakery/about_form.html', {'action': 'Создать'})


@staff_required
def about_edit(request, pk):
    about_page = get_object_or_404(AboutPage, pk=pk)
    if request.method == 'POST':
        about_page.title = request.POST.get('title', '').strip()
        about_page.content = request.POST.get('content', '').strip()
        about_page.save()
        messages.success(request, 'Страница «О нас» обновлена!')
        return redirect('about')
    return render(request, 'bakery/about_form.html', {'about_page': about_page, 'action': 'Изменить'})


# --- Авторизация и регистрация ---

def login_view(request):
    error = None
    if request.method == 'POST':
        if request.POST.get('register') == '1':
            # Регистрация
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')
            phone = request.POST.get('phone', '').strip()
            birth_date = request.POST.get('birth_date', '').strip()

            if not first_name or not last_name or not username or not password or not email:
                error = 'Заполните все обязательные поля.'
            elif password != password2:
                error = 'Пароли не совпадают.'
            elif User.objects.filter(username=username).exists():
                error = 'Пользователь с таким логином уже существует.'
            elif User.objects.filter(email=email).exists():
                error = 'Email уже занят.'
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Profile.objects.create(
                    user=user,
                    phone=phone,
                    birth_date=birth_date or None,
                )
                auth_login(request, user)
                messages.success(request, f'Добро пожаловать, {first_name}!')
                return redirect('home')
        else:
            # Вход
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                error = 'Неверное имя пользователя или пароль'
    return render(request, 'bakery/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


# --- Сброс пароля ---

def password_reset_request(request):
    """Запрос на сброс пароля"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                user = User.objects.get(email=email)
                # Создаем токен для сброса
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes
                
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Сохраняем токен во временное хранилище (для упрощения - в сессию)
                request.session['password_reset'] = {'uid': uid, 'token': token, 'email': email}
                
                # В реальной версии - отправляем email с ссылкой
                messages.success(request, f'Если email {email} зарегистрирован, мы отправили инструкцию для сброса пароля.')
                return redirect('password_reset_confirm', uidb64=uid, token=token)
            except User.DoesNotExist:
                pass
        messages.info(request, 'Если email зарегистрирован, вы получите инструкцию.')
        return redirect('home')
    return render(request, 'bakery/password_reset_request.html')


def password_reset_confirm(request, uidb64, token):
    """Подтверждение сброса пароля"""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_bytes, force_str
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')
            if password and password == password2:
                user.set_password(password)
                user.save()
                messages.success(request, 'Пароль успешно изменён! Теперь вы можете войти.')
                return redirect('login')
            else:
                messages.error(request, 'Пароли не совпадают.')
        return render(request, 'bakery/password_reset_confirm.html', {'user': user})
    else:
        messages.error(request, 'Ссылка сброса пароля недействительна.')
        return redirect('password_reset_request')


# --- Заказы ---

@login_required
def order_list(request):
    """Список заказов: админ видит все, пользователь — только свои."""
    if request.user.is_staff:
        orders = Order.objects.all()
        is_staff = True
    else:
        orders = request.user.orders.all()
        is_staff = False
    return render(request, 'bakery/orders.html', {
        'orders': orders,
        'is_staff': is_staff,
        'is_authenticated': request.user.is_authenticated
    })


@login_required
def order_create(request):
    """Оформление заказа."""
    products_list = Product.objects.all()
    stores = Store.objects.filter(is_active=True)
    preselected_product = None
    preselected_store = None
    
    if request.method == 'GET':
        product_id = request.GET.get('product')
        store_id = request.GET.get('store')
        if product_id:
            preselected_product = get_object_or_404(Product, pk=product_id)
        if store_id:
            preselected_store = get_object_or_404(Store, pk=store_id)
    
    if request.method == 'POST':
        comment = request.POST.get('comment', '')[:500]
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        store_id = request.POST.get('store')

        if not product_ids:
            messages.error(request, 'Выберите хотя бы один продукт.')
            return render(request, 'bakery/order_create.html', {
                'products': products_list,
                'stores': stores,
                'preselected_product': preselected_product,
                'preselected_store': preselected_store,
            })

        store = get_object_or_404(Store, pk=store_id) if store_id else None
        order = Order.objects.create(user=request.user, comment=comment, store=store)
        for pid, qty in zip(product_ids, quantities):
            try:
                qty = int(qty) if qty else 1
                if 0 < qty <= 100:
                    product = get_object_or_404(Product, pk=pid)
                    OrderItem.objects.create(order=order, product=product, quantity=qty)
            except (ValueError, Product.DoesNotExist):
                continue

        messages.success(request, f'Заказ №{order.pk} оформлен!')
        return redirect('order_list')
    
    return render(request, 'bakery/order_create.html', {
        'products': products_list,
        'stores': stores,
        'preselected_product': preselected_product,
        'preselected_store': preselected_store,
    })


# --- Пекарни (админка) ---

@staff_required
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'bakery/store_list.html', {'stores': stores})
    

@staff_required
def store_add_edit(request, pk=None):
    store = get_object_or_404(Store, pk=pk) if pk else None
    if request.method == 'POST':
        store_data = {
            'name': request.POST.get('name', '').strip(),
            'address': request.POST.get('address', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'working_hours': request.POST.get('working_hours', '').strip(),
            'is_active': request.POST.get('is_active') == 'on',
            'display_order': int(request.POST.get('order', 0)),
        }
        image = request.FILES.get('image')
        
        # Валидация изображения
        if image:
            try:
                validate_image_file(image)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('store_list')
        
        if image:
            store_data['image'] = image
        store = Store(**store_data)
        if pk:
            store.pk = pk
        store.save()
        messages.success(request, f'Пекарня «{store.name}» сохранена!')
        return redirect('store_list')
    
    return render(request, 'bakery/store_form.html', {'store': store, 'action': 'Изменить' if pk else 'Добавить'})


@staff_required
def store_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        name = store.name
        store.delete()
        messages.success(request, f'Пекарня «{name}» удалена.')
        return redirect('store_list')
    return render(request, 'bakery/store_confirm_delete.html', {'store': store})


@staff_required
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа №{order.pk} изменён на "{order.get_status_display()}"')
        else:
            messages.error(request, 'Неверный статус.')
    return redirect('order_list')


@staff_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'bakery/user_list.html', {'users': users})


@staff_required
def user_delete(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if user_to_delete.pk == request.user.pk:
        messages.error(request, 'Вы не можете удалить самого себя.')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user_to_delete.get_full_name() or user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'Пользователь «{username}» удалён.')
        return redirect('user_list')
    
    return render(request, 'bakery/user_confirm_delete.html', {'user': user_to_delete})


# --- Модерация отзывов ---

@staff_required
def review_moderate(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            review.moderation_status = 'approved'
            review.save()
            messages.success(request, 'Отзыв опубликован.')
        elif action == 'reject':
            review.moderation_status = 'rejected'
            review.save()
            messages.success(request, 'Отзыв отклонён.')
        elif action == 'delete':
            review.delete()
            messages.success(request, 'Отзыв удалён.')
        return redirect('review_moderation')
    
    return render(request, 'bakery/review_moderate.html', {'review': review})


@staff_required
def review_moderation(request):
    pending_reviews = Review.objects.filter(moderation_status='pending')
    all_reviews = Review.objects.order_by('-created_at')
    return render(request, 'bakery/review_moderation.html', {'pending': pending_reviews, 'all': all_reviews})


# --- Отмена заказа ---

@login_required
def order_cancel(request, pk):
    """Отмена заказа пользователем"""
    order = get_object_or_404(Order, pk=pk)
    
    # Пользователь может отменить только свои заказы, которые ещё не в работе/не готовы
    if order.user != request.user:
        messages.error(request, 'Вы можете отменять только свои заказы.')
        return redirect('order_list')
    
    if order.status in ['processing', 'ready', 'delivered']:
        messages.error(request, 'Заказ уже передан в работу и не может быть отменён.')
        return redirect('order_list')
    
    if request.method == 'POST':
        order.status = 'cancelled'
        order.cancelled_by_customer = True
        order.save()
        messages.success(request, 'Заказ отменён.')
        return redirect('order_list')
    
    return render(request, 'bakery/order_cancel_confirm.html', {'order': order})

