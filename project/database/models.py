from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    
    def __str__(self):
        return f'{self.id} | {self.first_name} {self.last_name}'
    
    
class Tariffs(models.Model):
    name = models.CharField(max_length=128)
    cost = models.PositiveIntegerField()
    count_generations = models.PositiveIntegerField()
    
    def __str__(self):
        return f'Название: {self.name}\nСтоимость:{self.cost}\nКол-во генераций{self.count_generations}'
    
    
class Styles(models.Model):
    pass


class Categories(models.Model):
    pass
    

