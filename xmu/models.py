import os
from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='姓名')
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    message = models.TextField(verbose_name='留言内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True, null=True)

    class Meta:
        verbose_name = '联系留言'
        verbose_name_plural = '联系留言'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"


class Paper(models.Model):
    title = models.CharField(max_length=200, verbose_name='论文名称')
    authors = models.CharField(max_length=300, verbose_name='作者')
    link = models.URLField(max_length=500, verbose_name='论文链接')
    published_date = models.DateTimeField(null=True, blank=True, verbose_name='发表日期', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '论文'
        verbose_name_plural = '论文'
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return self.title


class ResearchDirection(models.Model):
    direction_name = models.TextField(verbose_name='研究方向')
    weight = models.IntegerField(default=0, verbose_name='权重', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '研究方向'
        verbose_name_plural = '研究方向'
        ordering = ['-weight', 'id']

    def __str__(self):
        return self.direction_name


class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery_images/', verbose_name='图片')
    weight = models.IntegerField(default=0, verbose_name='权重', db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name='图片描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '科研图库'
        verbose_name_plural = '科研图库'
        ordering = ['-weight', '-created_at']

    def __str__(self):
        return f"Gallery Image {self.id} - Weight: {self.weight}"


class ResultImage(models.Model):
    image = models.ImageField(upload_to='result_images/', verbose_name='图片')
    weight = models.IntegerField(default=0, verbose_name='权重', db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name='图片描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '研究成果'
        verbose_name_plural = '研究成果'
        ordering = ['-weight', '-created_at']

    def __str__(self):
        return f"Result Image {self.id} - Weight: {self.weight}"


class Member(models.Model):
    POSITION_CHOICES = [
        ('Professor', 'Professor'),
        ('Member', 'Member'),
    ]

    name = models.CharField(max_length=100, verbose_name='姓名')
    position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        default='Member',
        verbose_name='职位',
        db_index=True
    )
    degree = models.CharField(max_length=100, blank=True, null=True, verbose_name='学位')
    education = models.TextField(blank=True, null=True, verbose_name='教育背景')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        default='avatar.jpg',
        verbose_name='头像'
    )
    weight = models.IntegerField(default=0, verbose_name='权重', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '团队成员'
        verbose_name_plural = '团队成员'
        ordering = ['-position', '-weight', 'id']

    def __str__(self):
        return self.name


class BackgroundImage(models.Model):
    avatar = models.ImageField(
        upload_to='bg/',
        blank=True,
        null=True,
        default='logo.jpg',
        verbose_name='背景图片'
    )
    weight = models.IntegerField(default=0, verbose_name='权重', db_index=True)
    quote = models.TextField(
        blank=True,
        null=True,
        default='If I have seen further it is by standing on the shoulders of giants.',
        verbose_name='名言'
    )
    author = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='Isaac Newton',
        verbose_name='名言作者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)

    class Meta:
        verbose_name = '背景配置'
        verbose_name_plural = '背景配置'
        ordering = ['-weight', '-created_at']

    def __str__(self):
        return f"Quote by {self.author}"


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    return f'files/{ext}/{filename}'


class UploadedFile(models.Model):
    file = models.FileField(upload_to=user_directory_path, verbose_name='文件')
    title = models.CharField(max_length=255, verbose_name='文件标题')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间', db_index=True)

    class Meta:
        verbose_name = '上传文件'
        verbose_name_plural = '上传文件'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def filename(self):
        return os.path.basename(self.file.name)

    def file_ext(self):
        return os.path.splitext(self.file.name)[1][1:].lower()


def treehole_image_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    return f'treehole/{instance.image_id}.{ext}'


class TreeHoleImage(models.Model):
    image_id = models.CharField(max_length=36, unique=True, verbose_name='图片唯一标识', db_index=True)
    image = models.ImageField(upload_to=treehole_image_path, verbose_name='图片')
    filename = models.CharField(max_length=255, blank=True, verbose_name='原始文件名')
    size = models.IntegerField(default=0, verbose_name='文件大小')
    width = models.IntegerField(default=0, verbose_name='图片宽度')
    height = models.IntegerField(default=0, verbose_name='图片高度')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True, null=True)

    class Meta:
        verbose_name = '树洞图片'
        verbose_name_plural = '树洞图片'
        ordering = ['-created_at']

    def __str__(self):
        return self.image_id


class TreeHoleContent(models.Model):
    content_id = models.CharField(max_length=36, unique=True, verbose_name='内容唯一标识', db_index=True)
    content = models.TextField(verbose_name='留言内容')
    word_count = models.IntegerField(default=0, verbose_name='字数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True, null=True)

    class Meta:
        verbose_name = '树洞内容'
        verbose_name_plural = '树洞内容'
        ordering = ['-created_at']

    def __str__(self):
        return self.content_id[:8]

    def content_summary(self):
        if not self.content:
            return '无内容'
        return self.content[:50] + '...' if len(self.content) > 50 else self.content


class TreeHoleMessage(models.Model):
    message_id = models.CharField(max_length=36, unique=True, verbose_name='留言唯一标识', db_index=True)
    name = models.CharField(max_length=50, verbose_name='姓名', default='匿名')
    content_ref = models.ForeignKey('TreeHoleContent', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='内容引用', related_name='messages')
    image = models.ImageField(upload_to='treehole/', blank=True, null=True, verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True, null=True)

    class Meta:
        verbose_name = '树洞留言'
        verbose_name_plural = '树洞留言'
        ordering = ['-created_at']

    def __str__(self):
        return self.message_id[:8]

    def content_summary(self):
        if not self.content_ref or not self.content_ref.content:
            return '无内容'
        return self.content_ref.content_summary()

    def has_image(self):
        return bool(self.image)
    has_image.boolean = True
    has_image.short_description = '有图片'