import uuid
from django.core.cache import cache
from .models import (
    Paper,
    ResearchDirection,
    GalleryImage,
    ResultImage,
    Member,
    BackgroundImage,
    ContactMessage,
    UploadedFile,
    TreeHoleImage,
    TreeHoleContent,
    TreeHoleMessage
)


class HomePageService:
    CACHE_KEY_PAPERS = 'home_papers'
    CACHE_KEY_DIRECTIONS = 'home_directions'
    CACHE_KEY_GALLERY = 'home_gallery'
    CACHE_KEY_RESULT = 'home_result'
    CACHE_KEY_CONFIG = 'home_config'
    CACHE_TIMEOUT = 3600

    @classmethod
    def get_papers(cls):
        papers = cache.get(cls.CACHE_KEY_PAPERS)
        if papers is None:
            papers = list(Paper.objects.all())
            cache.set(cls.CACHE_KEY_PAPERS, papers, cls.CACHE_TIMEOUT)
        return papers

    @classmethod
    def get_directions(cls):
        directions = cache.get(cls.CACHE_KEY_DIRECTIONS)
        if directions is None:
            directions = list(ResearchDirection.objects.all())
            cache.set(cls.CACHE_KEY_DIRECTIONS, directions, cls.CACHE_TIMEOUT)
        return directions

    @classmethod
    def get_gallery_images(cls, limit=3):
        gallery = cache.get(cls.CACHE_KEY_GALLERY)
        if gallery is None:
            gallery = list(GalleryImage.objects.order_by('-weight')[:limit])
            cache.set(cls.CACHE_KEY_GALLERY, gallery, cls.CACHE_TIMEOUT)
        return gallery

    @classmethod
    def get_result_images(cls, limit=4):
        result = cache.get(cls.CACHE_KEY_RESULT)
        if result is None:
            result = list(ResultImage.objects.order_by('-weight')[:limit])
            cache.set(cls.CACHE_KEY_RESULT, result, cls.CACHE_TIMEOUT)
        return result

    @classmethod
    def get_config(cls):
        config = cache.get(cls.CACHE_KEY_CONFIG)
        if config is None:
            config = BackgroundImage.objects.order_by('-weight').first()
            cache.set(cls.CACHE_KEY_CONFIG, config, cls.CACHE_TIMEOUT)
        return config

    @classmethod
    def clear_cache(cls):
        cache.delete_many([
            cls.CACHE_KEY_PAPERS,
            cls.CACHE_KEY_DIRECTIONS,
            cls.CACHE_KEY_GALLERY,
            cls.CACHE_KEY_RESULT,
            cls.CACHE_KEY_CONFIG
        ])


class ContactService:
    @classmethod
    def create_contact_message(cls, name, email, phone='', message=''):
        if not name or not email:
            raise ValueError('姓名和邮箱不能为空')

        return ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

    @classmethod
    def get_contact_messages(cls):
        return ContactMessage.objects.all()


class MemberService:
    @classmethod
    def get_all_members(cls):
        return Member.objects.all().order_by('-position', '-weight')

    @classmethod
    def get_professors(cls):
        return Member.objects.filter(position='Professor').order_by('-weight')

    @classmethod
    def get_students(cls):
        return Member.objects.filter(position='Member').order_by('-weight')


class FileService:
    @classmethod
    def upload_file(cls, file, title=None):
        if not file:
            raise ValueError('文件不能为空')

        if not title:
            title = file.name

        return UploadedFile.objects.create(
            file=file,
            title=title
        )

    @classmethod
    def get_files(cls, show_all=False, limit=10):
        queryset = UploadedFile.objects.order_by('-uploaded_at')
        if not show_all:
            queryset = queryset[:limit]
        return queryset

    @classmethod
    def get_file_by_id(cls, file_id):
        try:
            return UploadedFile.objects.get(id=file_id)
        except UploadedFile.DoesNotExist:
            return None


class TreeHoleService:
    MAX_IMAGE_SIZE = 5 * 1024 * 1024
    MAX_TEXT_LENGTH = 5000
    SUPPORTED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']

    @classmethod
    def upload_image(cls, uploaded_file):
        if not uploaded_file:
            return {'code': 1001, 'message': '图片不能为空', 'data': None}

        if uploaded_file.size > cls.MAX_IMAGE_SIZE:
            return {'code': 1003, 'message': '图片大小超过限制（最大 5MB）', 'data': None}

        if uploaded_file.content_type not in cls.SUPPORTED_TYPES:
            return {'code': 1004, 'message': '不支持的图片格式，请使用 JPG/PNG/GIF', 'data': None}

        image_id = 'img_' + str(uuid.uuid4()).replace('-', '')[:12]

        try:
            from PIL import Image
            img = Image.open(uploaded_file)
            width, height = img.size
        except Exception:
            width, height = 0, 0

        treehole_image = TreeHoleImage.objects.create(
            image_id=image_id,
            image=uploaded_file,
            filename=uploaded_file.name,
            size=uploaded_file.size,
            width=width,
            height=height
        )

        image_url = treehole_image.image.url if treehole_image.image else None

        return {
            'code': 0,
            'message': 'success',
            'data': {
                'image_id': image_id,
                'url': image_url,
                'thumbnail_url': image_url,
                'filename': uploaded_file.name,
                'size': uploaded_file.size,
                'width': width,
                'height': height
            }
        }

    @classmethod
    def submit_message(cls, name='', content='', image=None, image_id=None):
        name = (name or '').strip()
        content = (content or '').strip()

        if not name:
            return {'code': 1007, 'message': '请输入您的姓名', 'data': None}

        if not content and not image and not image_id:
            return {'code': 1006, 'message': '请输入留言内容或上传图片', 'data': None}

        if len(content) > cls.MAX_TEXT_LENGTH:
            return {'code': 1002, 'message': '留言内容不能超过 5000 字', 'data': None}

        message_id = 'msg_' + str(uuid.uuid4()).replace('-', '')[:8]

        content_ref = None
        if content:
            content_id = 'cnt_' + str(uuid.uuid4()).replace('-', '')[:8]
            content_ref = TreeHoleContent.objects.create(
                content_id=content_id,
                content=content,
                word_count=len(content)
            )

        treehole_message = TreeHoleMessage.objects.create(
            message_id=message_id,
            name=name,
            content_ref=content_ref
        )

        if image:
            treehole_message.image = image
            treehole_message.save()
        elif image_id:
            try:
                treehole_image = TreeHoleImage.objects.get(image_id=image_id)
                treehole_message.image = treehole_image.image
                treehole_message.save()
            except TreeHoleImage.DoesNotExist:
                pass

        image_url = treehole_message.image.url if treehole_message.image else None

        created_at_str = None
        if treehole_message.created_at:
            created_at_str = treehole_message.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')

        return {
            'code': 0,
            'message': 'success',
            'data': {
                'message_id': message_id,
                'name': name,
                'content': content,
                'image': image_url,
                'created_at': created_at_str
            }
        }

    @classmethod
    def get_message_by_id(cls, message_id):
        try:
            return TreeHoleMessage.objects.get(message_id=message_id)
        except TreeHoleMessage.DoesNotExist:
            return None

    @classmethod
    def get_all_messages(cls, limit=20):
        return TreeHoleMessage.objects.order_by('-created_at')[:limit]