from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import *




class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')  
    actions = ['delete_selected']  

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add_user/', self.add_user_view),
            path('delete_user/', self.delete_user_view),
        ]
        return custom_urls + urls

    def add_user_view(self, request):
        """
        Редирект на стандартную страницу добавления пользователя в админке
        """
        url = reverse('admin:%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_user_view(self, request):
        """
        Редирект на стандартную страницу изменения пользователей в админке
        """
        url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        return HttpResponseRedirect(url)

    def delete_selected(self, request, queryset):
        """
        Это действие для массового удаления пользователей.
        """
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} пользователей успешно удалено.")

    delete_selected.short_description = "Удалить выбранных пользователей"

admin.site.register(User, UserAdmin)
admin.site.register(Tariffs)
admin.site.register(Promocode)
admin.site.register(Styles)
admin.site.register(Categories)
admin.site.register(PhotoFormat)
