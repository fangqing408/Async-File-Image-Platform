from django.contrib import admin
from .models import (
    ContactMessage,
    Paper,
    ResearchDirection,
    GalleryImage,
    ResultImage,
    Member,
    BackgroundImage,
    UploadedFile,
    TreeHoleImage,
    TreeHoleContent,
    TreeHoleMessage
)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'published_date', 'link')
    list_filter = ('published_date',)
    search_fields = ('title', 'authors')
    ordering = ('-published_date',)
    fields = ('title', 'authors', 'link', 'published_date')


@admin.register(ResearchDirection)
class ResearchDirectionAdmin(admin.ModelAdmin):
    list_display = ('direction_name', 'weight', 'created_at')
    list_filter = ('weight',)
    search_fields = ('direction_name',)
    ordering = ('-weight',)
    fields = ('direction_name', 'weight')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'weight', 'description', 'created_at')
    list_filter = ('weight', 'created_at')
    search_fields = ('description',)
    ordering = ('-weight', '-created_at')
    fields = ('image', 'weight', 'description')


@admin.register(ResultImage)
class ResultImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'weight', 'description', 'created_at')
    list_filter = ('weight', 'created_at')
    search_fields = ('description',)
    ordering = ('-weight', '-created_at')
    fields = ('image', 'weight', 'description')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'degree', 'email', 'weight')
    list_filter = ('position',)
    search_fields = ('name', 'email', 'education')
    ordering = ('-position', '-weight')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'position', 'degree', 'email')
        }),
        ('详细信息', {
            'fields': ('education', 'avatar', 'weight')
        })
    )


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ('author', 'weight', 'created_at')
    list_filter = ('weight',)
    search_fields = ('quote', 'author')
    ordering = ('-weight',)
    fields = ('avatar', 'weight', 'quote', 'author')


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    fields = ('file', 'title')


@admin.register(TreeHoleImage)
class TreeHoleImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'filename', 'size_display', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('image_id', 'filename')
    ordering = ('-created_at',)
    readonly_fields = ('image_id', 'filename', 'size', 'width', 'height', 'created_at')
    fields = ('image',)

    def size_display(self, obj):
        if obj.size < 1024:
            return f'{obj.size} B'
        elif obj.size < 1024 * 1024:
            return f'{(obj.size / 1024):.1f} KB'
        else:
            return f'{(obj.size / (1024 * 1024)):.1f} MB'
    size_display.short_description = '文件大小'


@admin.register(TreeHoleContent)
class TreeHoleContentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'content_summary', 'word_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'content_id')
    ordering = ('-created_at',)
    readonly_fields = ('content_id', 'word_count', 'created_at')
    fields = ('content',)


@admin.register(TreeHoleMessage)
class TreeHoleMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'name', 'content_summary', 'has_image', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'content_ref__content', 'message_id')
    ordering = ('-created_at',)
    readonly_fields = ('message_id', 'created_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('message_id', 'name', 'content_ref', 'created_at')
        }),
        ('图片', {
            'fields': ('image',)
        })
    )