from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit_contact/', views.submit_contact, name='submit_contact'),
    path('contact_success/', views.contact_success, name='contact_success'),
    path('members/', views.members, name='members'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('api/papers/', views.api_papers, name='api_papers'),
    path('api/members/', views.api_members, name='api_members'),
    path('api/directions/', views.api_directions, name='api_directions'),
    path('api/gallery/', views.api_gallery, name='api_gallery'),
    path('api/config/', views.api_config, name='api_config'),
    path('th/', views.tree_hole_page, name='tree_hole_page'),
    path('api/th/upload-image/', views.api_treehole_upload_image, name='api_treehole_upload_image'),
    path('api/th/', views.api_treehole_submit, name='api_treehole_submit'),
]