from django import forms
from django.core.validators import FileExtensionValidator
from .models import UploadedFile


MAX_FILE_SIZE = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
    'jpg', 'jpeg', 'png', 'gif', 'svg',
    'txt', 'md', 'csv', 'json'
]


class UploadForm(forms.ModelForm):
    file = forms.FileField(
        label='选择文件',
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)
        ],
        help_text=f'支持的格式: {", ".join(ALLOWED_EXTENSIONS)}，最大大小: 50MB'
    )

    class Meta:
        model = UploadedFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')

        if file:
            if file.size > MAX_FILE_SIZE:
                raise forms.ValidationError('文件大小不能超过 50MB')

            extension = file.name.split('.')[-1].lower()
            if extension not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(f'不支持的文件格式，请上传以下格式: {", ".join(ALLOWED_EXTENSIONS)}')

        return file