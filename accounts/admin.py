from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone')
    list_select_related = ('profile',)
    
    def get_phone(self, instance):
        return instance.profile.phone if hasattr(instance, 'profile') else '-'
    get_phone.short_description = 'Telefon'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Ponovo registruj User sa novim UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'mobile', 'city', 'business_number')
    search_fields = ('user__username', 'user__email', 'phone', 'mobile', 'business_number')
    list_filter = ('city', 'department')
