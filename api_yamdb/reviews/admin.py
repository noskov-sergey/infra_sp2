from django.contrib import admin

from .models import User, Genre, Category


class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'role',
        'bio',
        'email',
        'confirmation_code',
    )
    search_fields = ('username',)
    empty_value_display = '-пусто-'
    list_editable = ('role',)


admin.site.register(User, UserAdmin)


@admin.register(Genre)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
