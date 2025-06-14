import uuid

from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField('Имя', max_length=64)
    last_name = models.CharField('Фамилия', max_length=64)
    photo_format = models.CharField('Формат фото', max_length=15, default='square_hd')
    referrer_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    generation_count = models.IntegerField('Количество генераций', default=0)
    refferal_link = models.CharField(null=True, blank=True)
    current_avatar_id = models.UUIDField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.id} | {self.first_name} {self.last_name}'
    
    
    class Meta:
        app_label = 'database' 
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'




    
class Tariffs(models.Model):
    name = models.CharField('Название', max_length=128)
    cost = models.PositiveIntegerField('Цена')
    count_generations = models.PositiveIntegerField('Количество генераций')
    
    def __str__(self):
        return f'Пакет: {self.name} | Стоимость: {self.cost} | Кол-во генераций: {self.count_generations}'
    
    
    class Meta:
        verbose_name = 'Пакет'
        verbose_name_plural = 'Пакеты'
    
    
class Promocode(models.Model):
    code = models.CharField('Промокод', max_length=1024)
    count_generations = models.PositiveIntegerField('Количество генераций', default=0)
    count_usage = models.IntegerField('Сколько раз можно использовать')
    
    
    def __str__(self):
        return f'Приз: {self.count_generations} | Кол-во {self.count_usage}'
    
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class UserPromocode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_users')
    used_promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, related_name='promocodes')
    

class Categories(models.Model):
    name = models.CharField('Название категории', max_length=258, default='without name')
    
    def __str__(self):
        return f'Категория: {self.name}'

    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    
class Styles(models.Model):
    name = models.CharField('Название стиля', max_length=258, default='without name')
    capture_for_lora = models.TextField('Промо для генерирования', null=True, blank=True)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True, help_text="ID платежа в ЮKassa")
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2, help_text="Сумма платежа")
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Платеж {self.payment_id} - {self.status}"
    
    class Meta:
        verbose_name = 'Платеж Юкасса'
        verbose_name_plural = 'Платежи Юкасса'


class UserArchive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_user_id = models.BigIntegerField(unique=True)
    archive_file = models.FileField(upload_to='archives/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archive for {self.telegram_user_id}"

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


class Avatar(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужчина'),
        ('female', 'Женщина'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, default="Model")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avatars")
    api_name = models.CharField(max_length=150, unique=True, editable=False, default="Уникальное имя для API LoRA", verbose_name="Уникальное имя для API LoRA")
    is_complete = models.BooleanField(default=False)
    trigger_phrase = models.CharField(max_length=100, default="Уникальная тригер-фраза для API LoRA")
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.api_name = f"u{self.user.id}_m{self.id.hex[:12]}"
            
            self.trigger_phrase = f"id{self.id.hex[:8]} person"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Avatar ({self.gender}) for {self.user.first_name}"
    
    class Meta:
        verbose_name = 'Аватар'
        verbose_name_plural = 'Аватары'