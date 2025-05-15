from django.contrib import admin
from .models import Work, Review, ListEntry

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'genre', 'rating', 'release_date')
    list_filter = ('type', 'genre')
    search_fields = ('title',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'work', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'work__title', 'user__username')

@admin.register(ListEntry)
class ListEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'work', 'status', 'added_at')
    list_filter = ('status', 'added_at')
    search_fields = ('work__title', 'user__username')

