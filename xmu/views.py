import logging
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from .services import HomePageService, ContactService, MemberService, FileService, TreeHoleService
from .forms import UploadForm
from .utils import handle_exception

logger = logging.getLogger(__name__)


@cache_page(60 * 15)
def home(request):
    try:
        papers = HomePageService.get_papers()
        directions = HomePageService.get_directions()
        gallery_images = HomePageService.get_gallery_images(limit=3)
        result_images = HomePageService.get_result_images(limit=4)
        config = HomePageService.get_config()

        return render(request, 'login.html', {
            'papers': papers,
            'directions': directions,
            'galleryimages': gallery_images,
            'resultimages': result_images,
            'conf': config
        })
    except Exception as e:
        handle_exception(request, e)
        logger.error(f'Home page error: {e}')
        return render(request, 'login.html', {
            'papers': [],
            'directions': [],
            'galleryimages': [],
            'resultimages': [],
            'conf': None
        })


@require_http_methods(['POST'])
def submit_contact(request):
    try:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email:
            referer = request.META.get('HTTP_REFERER', '/')
            return render(request, 'contact_success.html', {
                'referer': referer,
                'error': '姓名和邮箱不能为空'
            })

        ContactService.create_contact_message(name, email, phone, message)
        logger.info(f'Contact message created by {name} ({email})')

        referer = request.META.get('HTTP_REFERER', '/')
        return render(request, 'contact_success.html', {'referer': referer})

    except Exception as e:
        handle_exception(request, e)
        logger.error(f'Contact submit error: {e}')
        referer = request.META.get('HTTP_REFERER', '/')
        return render(request, 'contact_success.html', {
            'referer': referer,
            'error': str(e)
        })


def contact_success(request):
    referer = request.META.get('HTTP_REFERER', '/')
    return render(request, 'contact_success.html', {'referer': referer})


@cache_page(60 * 15)
def members(request):
    try:
        members_list = MemberService.get_all_members()
        return render(request, 'members.html', {'members': members_list})
    except Exception as e:
        handle_exception(request, e)
        logger.error(f'Members page error: {e}')
        return render(request, 'members.html', {'members': []})


def upload_file(request):
    try:
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.save(commit=False)
                uploaded_file.title = request.FILES['file'].name
                uploaded_file.save()
                logger.info(f'File uploaded: {uploaded_file.title}')
                return redirect('upload_file')
            else:
                logger.warning(f'Upload form invalid: {form.errors}')

        else:
            form = UploadForm()

        show_all = request.GET.get('all') == '1'
        files = FileService.get_files(show_all=show_all, limit=10)

        return render(request, 'upload.html', {
            'form': form,
            'files': files,
            'show_all': show_all
        })

    except Exception as e:
        handle_exception(request, e)
        logger.error(f'Upload file error: {e}')
        return render(request, 'upload.html', {
            'form': UploadForm(),
            'files': [],
            'show_all': False
        })


def download_file(request, file_id):
    try:
        file_obj = FileService.get_file_by_id(file_id)
        if not file_obj:
            raise Http404('文件不存在')

        logger.info(f'File downloaded: {file_obj.title} (id: {file_id})')
        return FileResponse(
            file_obj.file.open(),
            as_attachment=True,
            filename=file_obj.filename()
        )

    except Http404:
        raise
    except Exception as e:
        handle_exception(request, e)
        logger.error(f'Download file error: {e}')
        raise Http404('文件下载失败')


def api_papers(request):
    try:
        papers = HomePageService.get_papers()
        data = [{
            'id': p.id,
            'title': p.title,
            'authors': p.authors,
            'link': p.link,
            'published_date': p.published_date.isoformat() if p.published_date else None
        } for p in papers]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def api_members(request):
    try:
        members_list = MemberService.get_all_members()
        data = [{
            'id': m.id,
            'name': m.name,
            'position': m.position,
            'degree': m.degree,
            'email': m.email,
            'education': m.education,
            'avatar': m.avatar.url if m.avatar else None
        } for m in members_list]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def api_directions(request):
    try:
        directions = HomePageService.get_directions()
        data = [{
            'id': d.id,
            'direction_name': d.direction_name,
            'weight': d.weight
        } for d in directions]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def api_gallery(request):
    try:
        images = HomePageService.get_gallery_images()
        data = [{
            'id': img.id,
            'image_url': img.image.url,
            'description': img.description,
            'weight': img.weight
        } for img in images]
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def api_config(request):
    try:
        config = HomePageService.get_config()
        if config:
            data = {
                'id': config.id,
                'quote': config.quote,
                'author': config.author,
                'background_image': config.avatar.url if config.avatar else None
            }
        else:
            data = {}
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(['POST'])
def api_treehole_upload_image(request):
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'code': 1001, 'message': '图片不能为空', 'data': None}, status=400)

        uploaded_file = request.FILES['image']
        result = TreeHoleService.upload_image(uploaded_file)

        status_code = 200 if result['code'] == 0 else 400
        return JsonResponse(result, status=status_code)

    except Exception as e:
        logger.error(f'Tree hole upload image error: {e}')
        return JsonResponse({'code': 9999, 'message': '系统繁忙，请稍后重试', 'data': None}, status=500)


@require_http_methods(['POST'])
def api_treehole_submit(request):
    try:
        content = request.POST.get('content', '')
        image_id = request.POST.get('image_id', '')
        image_file = request.FILES.get('image')

        result = TreeHoleService.submit_message(content, image_file, image_id)

        status_code = 200 if result['code'] == 0 else 400
        return JsonResponse(result, status=status_code)

    except Exception as e:
        logger.error(f'Tree hole submit error: {e}')
        return JsonResponse({'code': 9999, 'message': '系统繁忙，请稍后重试', 'data': None}, status=500)


def tree_hole_page(request):
    return render(request, 'tree-hole.html')