from django.db import models


class User(models.Model):
    PHOTO_FORMAT = [
        ('1:1', '1:1'),
        ('3:4', '3:4'),
        ('9:16', '9:16'),
        ('16:9', '16:9'),
    ]
    
    id = models.BigIntegerField(primary_key=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    refferal_balance = models.IntegerField(default=0)
    photo_format = models.CharField(max_length=15, choices=PHOTO_FORMAT, blank=True, null=True)
    referrer_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    generation_count = models.IntegerField(default=0)
    refferal_link = models.CharField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.id} | {self.first_name} {self.last_name}'
    
    
    class Meta:
        app_label = 'database' 
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Avatar(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    ]

    name = models.CharField(max_length=100, default="Model")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avatars")
    dataset_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    element_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    element_name = models.CharField(max_length=100, blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    api_credit_cost = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def str(self):
        return f"Avatar ({self.gender}) for {self.user.first_name}"
    
    class Meta:
        verbose_name = 'Формат'
        verbose_name_plural = 'Форматы фото'

    
class Tariffs(models.Model):
    name = models.CharField(max_length=128)
    cost = models.PositiveIntegerField()
    count_generations = models.PositiveIntegerField()
    
    def __str__(self):
        return f'Пакет: {self.name} | Стоимость: {self.cost} | Кол-во генераций: {self.count_generations}'
    
    
    class Meta:
        verbose_name = 'Пакет'
        verbose_name_plural = 'Пакеты'
    
    
class Promocode(models.Model):
    code = models.CharField(max_length=1024)
    count_generations = models.PositiveIntegerField(default=0)
    count_usage = models.IntegerField()
    
    
    def __str__(self):
        return f'Приз: {self.count_generations} | Кол-во {self.count_usage}'
    
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class UserPromocode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_users')
    used_promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name='promocodes')
    

class Categories(models.Model):
    name = models.CharField(max_length=258, default='without name')
    
    def __str__(self):
        return f'Категория: {self.name}'

    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    
class Styles(models.Model):
    name = models.CharField(max_length=258, default='without name')
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='styles'
    )
    
    def __str__(self):
        return f'{self.name}'
    
    
    class Meta:
        verbose_name = 'Стиль'
        verbose_name_plural = 'Стили'
        
        
        
class PaymentRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('succeeded', 'Успешно'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True, help_text="ID платежа в ЮKassa")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Сумма платежа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Платеж {self.payment_id} - {self.status}"
    
    class Meta:
        verbose_name = 'Платеж Юкасса'
        verbose_name_plural = 'Платежи Юкасса'



class Attachments(models.Model):
    types = {
        'photo': 'Фото',
        'video': 'Видео',
        'document': 'Документ'
    }

    type = models.CharField('Тип вложения', choices=types)
    file = models.FileField('Файл')
    file_id = models.TextField(null=True)
    mailing = models.ForeignKey('Mailing', on_delete=models.SET_NULL, null=True, related_name='attachments')

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'


class Mailing(models.Model):
    text = models.TextField('Текст')
    datetime = models.DateTimeField('Дата/Время')
    is_ok = models.BooleanField('Статус отправки')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

