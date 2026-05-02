from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    ingredients = models.TextField('Состав', blank=True, help_text='Например: слоёное тесто, нежный сыр, куриная грудка')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    product_tags = models.TextField('Тип продукции', blank=True, help_text='Через запятую: хлеб, выпечка, фастфуд, десерты')
    cuisine_tags = models.TextField('Тип кухни', blank=True, help_text='Через запятую: русская, кавказская, американская, европейская')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукция'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AboutPage(models.Model):
    title = models.CharField('Заголовок', max_length=200, default='О нас')
    content = models.TextField('Содержание')

    class Meta:
        verbose_name = 'Страница «О нас»'
        verbose_name_plural = 'Страница «О нас»'

    def __str__(self):
        return self.title


class Store(models.Model):
    """Пекарни/точки самовывоза"""
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    working_hours = models.CharField('Часы работы', max_length=100, blank=True)
    image = models.ImageField('Фото', upload_to='stores/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    display_order = models.PositiveIntegerField('Порядок отображения', default=0)

    class Meta:
        verbose_name = 'Пекарня'
        verbose_name_plural = 'Пекарни'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f'{self.name} — {self.address}'


class Review(models.Model):
    MODERATION_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Опубликован'),
        ('rejected', 'Отклонён'),
    ]
    author = models.CharField('Имя', max_length=100)
    text = models.TextField('Отзыв')
    rating = models.IntegerField('Оценка', choices=[(i, str(i)) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    moderation_status = models.CharField('Статус модерации', max_length=20, choices=MODERATION_CHOICES, default='pending')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.author} ({self.get_moderation_status_display()})'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль: {self.user.get_full_name() or self.user.username}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В работе'),
        ('ready', 'Готов'),
        ('delivered', 'Выдан'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Точка самовывоза', related_name='orders')
    cancelled_by_customer = models.BooleanField('Отменён заказчиком', default=False)
    comment = models.TextField('Комментарий к заказу', blank=True)
    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.pk} — {self.user.get_full_name() or self.user.username}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def subtotal(self):
        return self.product.price * self.quantity
