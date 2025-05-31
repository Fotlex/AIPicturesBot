from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    refferal_balance = models.IntegerField(default=0)
    referrer_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    generation_count = models.IntegerField(default=0)
    refferal_link = models.CharField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.id} | {self.first_name} {self.last_name}'
    
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    
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
    
    
class PhotoFormat(models.Model):
    pass


    class Meta:
        verbose_name = 'Формат'
        verbose_name_plural = 'Форматы фото'
    

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



