(function () {
    'use strict';

    var API_UPLOAD_IMAGE = '/api/th/upload-image/';
    var API_SUBMIT_MESSAGE = '/api/th/';
    var MAX_IMAGE_SIZE = 10 * 1024 * 1024;
    var MAX_TEXT_LENGTH = 5000;
    var SUPPORTED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    var UPLOAD_TIMEOUT = 10000;

    var imageList = [];
    var isSubmitting = false;

    var nameEl = document.getElementById('tree-hole-name');
    var inputEl = document.getElementById('tree-hole-input');
    var previewArea = document.getElementById('image-preview-area');
    var previewList = document.getElementById('image-preview-list');
    var charCounter = document.getElementById('char-counter');
    var submitBtn = document.getElementById('submit-btn');
    var mobileFileInput = document.getElementById('mobile-file-input');
    var toastEl = document.getElementById('toast');
    var inputArea = document.querySelector('.tree-hole-input-area');

    var toastTimer = null;

    function showToast(message, type) {
        toastEl.textContent = message;
        toastEl.className = 'toast ' + (type || 'info');
        toastEl.style.display = 'block';

        if (toastTimer) {
            clearTimeout(toastTimer);
        }
        toastTimer = setTimeout(function () {
            toastEl.style.display = 'none';
        }, 2000);
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function generateId() {
        return 'local_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function getCSRFToken() {
        var name = 'csrftoken';
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateSubmitButton() {
        var hasText = inputEl.value.trim().length > 0;
        var hasSuccessImage = imageList.some(function (img) {
            return img.status === 'success';
        });
        var hasUploading = imageList.some(function (img) {
            return img.status === 'uploading';
        });

        if (isSubmitting || hasUploading) {
            submitBtn.disabled = true;
            submitBtn.textContent = '上传中...';
        } else if (hasText || hasSuccessImage) {
            submitBtn.disabled = false;
            submitBtn.textContent = '发送';
        } else {
            submitBtn.disabled = true;
            submitBtn.textContent = '发送';
        }
    }

    function updateCharCounter() {
        var len = inputEl.value.length;
        charCounter.textContent = len + '/' + MAX_TEXT_LENGTH;
        if (len >= MAX_TEXT_LENGTH) {
            charCounter.classList.add('exceed');
        } else {
            charCounter.classList.remove('exceed');
        }
    }

    function updatePreviewArea() {
        if (imageList.length === 0) {
            previewArea.style.display = 'none';
        } else {
            previewArea.style.display = 'block';
        }
    }

    function renderPreviewList() {
        previewList.innerHTML = '';

        imageList.forEach(function (img) {
            var item = document.createElement('div');
            item.className = 'preview-item';
            item.setAttribute('data-id', img.id);

            var imgEl = document.createElement('img');
            imgEl.src = img.previewUrl;
            imgEl.alt = '预览图';
            item.appendChild(imgEl);

            if (img.status === 'uploading') {
                var overlay = document.createElement('div');
                overlay.className = 'upload-overlay';
                var spinner = document.createElement('div');
                spinner.className = 'upload-spinner';
                overlay.appendChild(spinner);
                item.appendChild(overlay);
            }

            if (img.status === 'success') {
                var mark = document.createElement('div');
                mark.className = 'success-mark';
                mark.textContent = '✓';
                item.appendChild(mark);
            }

            if (img.status === 'error') {
                var errorMark = document.createElement('div');
                errorMark.className = 'error-mark';
                var errorIcon = document.createElement('div');
                errorIcon.className = 'error-icon';
                errorIcon.textContent = '✕';
                var errorText = document.createElement('div');
                errorText.className = 'error-text';
                errorText.textContent = img.errorMessage || '上传失败';
                errorMark.appendChild(errorIcon);
                errorMark.appendChild(errorText);
                item.appendChild(errorMark);

                var retryBtn = document.createElement('button');
                retryBtn.className = 'retry-btn';
                retryBtn.textContent = '重试';
                retryBtn.onclick = function (e) {
                    e.stopPropagation();
                    retryUpload(img.id);
                };
                item.appendChild(retryBtn);
            }

            var deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = '✕';
            deleteBtn.onclick = function (e) {
                e.stopPropagation();
                removeImage(img.id);
            };
            item.appendChild(deleteBtn);

            var info = document.createElement('div');
            info.className = 'image-info';
            info.textContent = img.file.name + ' · ' + formatFileSize(img.file.size);
            item.appendChild(info);

            previewList.appendChild(item);
        });

        updatePreviewArea();
        updateSubmitButton();
    }

    function addImage(file) {
        if (!file || !file.type || file.type.indexOf('image/') !== 0) {
            showToast('仅支持图片文件', 'error');
            return;
        }

        if (SUPPORTED_TYPES.indexOf(file.type) === -1) {
            showToast('不支持的图片格式，请使用 JPG/PNG/GIF', 'error');
            return;
        }

        if (file.size > MAX_IMAGE_SIZE) {
            showToast('图片大小超过限制（最大 10MB）', 'error');
            return;
        }

        var previewUrl = URL.createObjectURL(file);
        var imgData = {
            id: generateId(),
            file: file,
            previewUrl: previewUrl,
            status: 'uploading',
            imageId: null,
            retryCount: 0,
            errorMessage: null
        };

        imageList.push(imgData);
        renderPreviewList();

        setTimeout(function () {
            uploadImage(imgData.id);
        }, 300);
    }

    function removeImage(id) {
        var idx = imageList.findIndex(function (img) { return img.id === id; });
        if (idx === -1) return;

        if (imageList[idx].previewUrl) {
            URL.revokeObjectURL(imageList[idx].previewUrl);
        }
        imageList.splice(idx, 1);
        renderPreviewList();
    }

    function uploadImage(id) {
        var imgData = imageList.find(function (img) { return img.id === id; });
        if (!imgData) return;

        imgData.status = 'uploading';
        imgData.errorMessage = null;
        renderPreviewList();

        var formData = new FormData();
        formData.append('image', imgData.file, imgData.file.name || 'pasted-image.png');

        var controller = null;
        var timeoutId = null;

        if (window.AbortController) {
            controller = new AbortController();
            timeoutId = setTimeout(function () {
                controller.abort();
            }, UPLOAD_TIMEOUT);
        }

        var csrfToken = getCSRFToken();
        var fetchOptions = {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': csrfToken || ''
            }
        };

        if (controller) {
            fetchOptions.signal = controller.signal;
        }

        fetch(API_UPLOAD_IMAGE, fetchOptions)
            .then(function (response) {
                return response.json();
            })
            .then(function (res) {
                if (timeoutId) clearTimeout(timeoutId);

                if (res.code === 0 && res.data) {
                    imgData.status = 'success';
                    imgData.imageId = res.data.image_id;
                    imgData.serverUrl = res.data.url;
                    imgData.thumbnailUrl = res.data.thumbnail_url;
                    showToast('图片上传成功', 'success');
                } else {
                    imgData.status = 'error';
                    imgData.errorMessage = res.message || '上传失败';
                    showToast(res.message || '上传失败', 'error');
                }
                renderPreviewList();
            })
            .catch(function (err) {
                if (timeoutId) clearTimeout(timeoutId);

                imgData.status = 'error';

                if (err.name === 'AbortError') {
                    imgData.errorMessage = '上传超时';
                    showToast('上传超时，请重试', 'error');
                } else {
                    imgData.errorMessage = '网络异常';
                    showToast('上传失败，网络异常', 'error');
                }
                renderPreviewList();
            });
    }

    function retryUpload(id) {
        var imgData = imageList.find(function (img) { return img.id === id; });
        if (!imgData) return;

        if (imgData.retryCount >= 3) {
            showToast('上传失败，建议检查网络或更换图片', 'error');
            return;
        }

        imgData.retryCount++;
        uploadImage(id);
    }

    function submitTreeHole() {
        if (isSubmitting) return;

        var name = nameEl.value.trim();
        var content = inputEl.value.trim();
        var successImages = imageList.filter(function (img) {
            return img.status === 'success' && img.imageId;
        });

        if (!name) {
            showToast('请输入您的姓名', 'warning');
            nameEl.focus();
            return;
        }

        if (!content && successImages.length === 0) {
            showToast('请输入留言内容或上传图片', 'warning');
            return;
        }

        if (content.length > MAX_TEXT_LENGTH) {
            showToast('留言内容不能超过 ' + MAX_TEXT_LENGTH + ' 字', 'error');
            return;
        }

        isSubmitting = true;
        submitBtn.classList.add('loading');
        submitBtn.textContent = '发送中...';
        submitBtn.disabled = true;

        var formData = new FormData();
        formData.append('name', name);
        if (content) {
            formData.append('content', content);
        }
        if (successImages.length > 0) {
            formData.append('image_id', successImages[0].imageId);
        }

        var idempotencyKey = generateId();

        fetch(API_SUBMIT_MESSAGE, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': getCSRFToken() || '',
                'X-Idempotency-Key': idempotencyKey
            }
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (res) {
                if (res.code === 0) {
                    showToast('留言发送成功', 'success');
                    resetForm();
                } else {
                    showToast(res.message || '发送失败', 'error');

                    if (res.code === 2001) {
                        setTimeout(function () {
                            window.location.href = '/login/';
                        }, 1500);
                    }
                }
            })
            .catch(function (err) {
                showToast('网络异常，请稍后重试', 'error');
            })
            .finally(function () {
                isSubmitting = false;
                submitBtn.classList.remove('loading');
                updateSubmitButton();
            });
    }

    function resetForm() {
        inputEl.value = '';

        imageList.forEach(function (img) {
            if (img.previewUrl) {
                URL.revokeObjectURL(img.previewUrl);
            }
        });
        imageList = [];

        updateCharCounter();
        renderPreviewList();
        updateSubmitButton();
    }

    function handlePaste(e) {
        var items = e.clipboardData && e.clipboardData.items;
        var files = e.clipboardData && e.clipboardData.files;

        var hasImage = false;

        if (items) {
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                if (item.type && item.type.indexOf('image/') === 0) {
                    hasImage = true;
                    var file = item.getAsFile();
                    if (file) {
                        if (!file.name) {
                            var ext = file.type.split('/')[1] || 'png';
                            file = new File([file], 'pasted-image.' + ext, { type: file.type });
                        }
                        addImage(file);
                    }
                }
            }
        } else if (files) {
            for (var j = 0; j < files.length; j++) {
                var f = files[j];
                if (f.type && f.type.indexOf('image/') === 0) {
                    hasImage = true;
                    addImage(f);
                }
            }
        }

        if (hasImage) {
            e.preventDefault();
        }
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        inputArea.classList.add('drag-over');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        inputArea.classList.remove('drag-over');
    }

    function handleDragEnter(e) {
        e.preventDefault();
        e.stopPropagation();
        inputArea.classList.add('drag-over');
    }

    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        inputArea.classList.remove('drag-over');

        var files = e.dataTransfer && e.dataTransfer.files;
        if (!files || files.length === 0) {
            showToast('未检测到文件', 'warning');
            return;
        }

        var hasValidImage = false;
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            if (file.type && file.type.indexOf('image/') === 0) {
                hasValidImage = true;
                addImage(file);
            }
        }

        if (!hasValidImage) {
            showToast('请拖拽图片文件', 'warning');
        }
    }

    function init() {
        inputEl.addEventListener('paste', handlePaste);

        inputArea.addEventListener('dragover', handleDragOver);
        inputArea.addEventListener('dragleave', handleDragLeave);
        inputArea.addEventListener('dragenter', handleDragEnter);
        inputArea.addEventListener('drop', handleDrop);

        inputEl.addEventListener('input', function () {
            updateCharCounter();
            updateSubmitButton();
        });

        inputEl.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                submitTreeHole();
            }

            if (e.key === 'Escape') {
                resetForm();
            }
        });

        if (mobileFileInput) {
            mobileFileInput.addEventListener('change', function (e) {
                var files = e.target.files;
                for (var i = 0; i < files.length; i++) {
                    addImage(files[i]);
                }
                mobileFileInput.value = '';
            });
        }

        updateCharCounter();
        updateSubmitButton();
        updatePreviewArea();
    }

    window.submitTreeHole = submitTreeHole;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();