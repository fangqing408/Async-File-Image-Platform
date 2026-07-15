# XMU-LLAP API 接口文档 V1.0

> 对应需求基线：V1.0（来源：docs/requirements.md）
> 对应交互设计：V1.0（来源：docs/ui-design.md）
> 最后更新：2026-07-15
> 本文档由 API 契约建筑师 V2.0 维护

## 一、概述

### 1.1 基础信息

- **基础 URL**：`/api`
- **字符编码**：UTF-8
- **请求格式**：JSON（普通接口）/ multipart/form-data（文件上传接口）
- **响应格式**：JSON

### 1.2 全局响应结构

所有接口统一返回以下 JSON 结构：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `code` | integer | 业务状态码，`0` 表示成功，非 `0` 表示失败 |
| `message` | string | 提示信息，成功时为 `"success"`，失败时为具体错误描述 |
| `data` | object / null | 业务数据，失败时为 `null` |

### 1.3 认证与鉴权

需要登录的接口，需在 Header 中携带：

```
Authorization: Bearer {access_token}
```

### 1.4 错误码总表

| 业务码 | HTTP 状态 | 说明 | 用户提示 |
|:---|:---|:---|:---|
| 0 | 200 | 成功 | - |
| 1001 | 400 | 参数缺失 | 「请填写完整内容」 |
| 1002 | 400 | 内容超过长度限制 | 「留言内容不能超过 500 字」 |
| 1003 | 400 | 文件过大 | 「图片大小超过限制（最大 10MB）」 |
| 1004 | 400 | 不支持的文件格式 | 「不支持的图片格式，请使用 JPG/PNG/GIF」 |
| 1005 | 400 | 图片数量超过限制 | 「最多上传 9 张图片」 |
| 1006 | 400 | 内容为空 | 「请输入留言内容或上传图片」 |
| 2001 | 401 | 未登录 | 「请先登录」 |
| 2002 | 403 | 无权限 | 「无操作权限」 |
| 3001 | 404 | 资源不存在 | 「资源不存在」 |
| 9999 | 500 | 服务器内部错误 | 「系统繁忙，请稍后重试」 |

### 1.5 字段分歧决策记录

| 分歧点 | 决策 | 理由 |
|:---|:---|:---|
| **文件上传方式** | multipart/form-data | 需同时传输文本和二进制图片，Base64 编码会增加 33% 体积且无法支持流式上传 |
| **时间格式** | ISO 8601 字符串（UTC） | 如 `"2026-07-15T08:30:00Z"`，可读性好，前端可直接展示 |
| **图片上传策略** | 粘贴时独立上传，提交时仅传 URL | 降低提交接口复杂度，支持上传进度展示和失败重试 |
| **空值表示** | 返回 `null` | 统一使用 `null` 表示空值，前端统一处理 |

---

## 二、接口详细定义

### 2.1 树洞留言模块

#### API-001 上传树洞图片

- **接口**：`POST /api/tree-hole/upload-image/`
- **描述**：用户粘贴图片后自动调用此接口上传单张图片，返回图片 URL 供后续留言提交使用
- **关联需求**：REQ-001, REQ-002, REQ-004
- **关联交互**：UI-001 粘贴后状态 → 上传中状态 → 成功/失败状态
- **认证**：需要登录
- **Content-Type**：`multipart/form-data`

**请求参数**：

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|:---|:---|:---|:---|:---|
| `image` | file | 是 | 图片文件，支持 JPG/JPEG/PNG/GIF/BMP/WebP，单张不超过 10MB | `<binary>` |

**请求示例**：

```
POST /api/tree-hole/upload-image/ HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="pasted-image.png"
Content-Type: image/png

<binary data>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**成功响应** (HTTP 200)：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "image_id": "img_a1b2c3d4e5f6",
    "url": "/media/treehole/img_a1b2c3d4e5f6.png",
    "thumbnail_url": "/media/treehole/img_a1b2c3d4e5f6_thumb.png",
    "filename": "pasted-image.png",
    "size": 456789,
    "width": 1920,
    "height": 1080
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `data.image_id` | string | 图片唯一标识，后续提交留言时引用 |
| `data.url` | string | 图片完整 URL 路径 |
| `data.thumbnail_url` | string | 缩略图 URL 路径（最大 200x150） |
| `data.filename` | string | 原始文件名 |
| `data.size` | integer | 文件大小（字节） |
| `data.width` | integer | 图片宽度（像素） |
| `data.height` | integer | 图片高度（像素） |

**失败响应**：

文件过大 (HTTP 400)：

```json
{
  "code": 1003,
  "message": "图片大小超过限制（最大 10MB）",
  "data": null
}
```

不支持的格式 (HTTP 400)：

```json
{
  "code": 1004,
  "message": "不支持的图片格式，请使用 JPG/PNG/GIF",
  "data": null
}
```

未登录 (HTTP 401)：

```json
{
  "code": 2001,
  "message": "请先登录",
  "data": null
}
```

服务器错误 (HTTP 500)：

```json
{
  "code": 9999,
  "message": "系统繁忙，请稍后重试",
  "data": null
}
```

**错误码**：

| 业务码 | HTTP 状态 | 场景 | 用户提示 | 前端处理建议 |
|:---|:---|:---|:---|:---|
| 1003 | 400 | 图片超过 10MB | 「图片大小超过限制（最大 10MB）」 | Toast 提示，不进入上传中状态 |
| 1004 | 400 | 格式不支持 | 「不支持的图片格式，请使用 JPG/PNG/GIF」 | Toast 提示，不进入上传中状态 |
| 2001 | 401 | 未登录 | 「请先登录」 | 跳转登录页 |
| 9999 | 500 | 服务器错误 | 「服务器繁忙，请稍后重试」 | 进入失败状态，显示重试按钮 |

**非功能性**：

| 维度 | 说明 |
|:---|:---|
| **限流** | 单用户每分钟最多 30 次上传 |
| **超时** | 客户端建议 10 秒超时，超时后进入失败状态 |
| **文件限制** | 单张最大 10MB，支持格式：JPG/JPEG/PNG/GIF/BMP/WebP |

---

#### API-002 提交树洞留言

- **接口**：`POST /api/tree-hole/`
- **描述**：用户点击发送按钮提交留言，包含文本内容和已上传图片的 ID 列表
- **关联需求**：REQ-001, REQ-003, REQ-004
- **关联交互**：UI-001 成功状态 → 发送 → 初始状态（重置）
- **认证**：需要登录
- **Content-Type**：`multipart/form-data`

> **设计说明**：虽然此接口不直接上传文件，但使用 `multipart/form-data` 而非 `application/json`，原因是：(1) 与上传接口保持一致的 Content-Type，降低前端切换成本；(2) 为未来可能的"文本+图片混合提交"场景预留兼容性。若团队倾向 JSON，可将 Content-Type 改为 `application/json`，字段定义不变。

**请求参数**：

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|:---|:---|:---|:---|:---|
| `content` | string | 否 | 留言文本内容，最多 500 字 | `"这是一条树洞留言"` |
| `image_ids` | string | 否 | 图片 ID 列表，逗号分隔，最多 9 张 | `"img_a1b2c3d4e5f6,img_b2c3d4e5f6g7"` |

> **校验规则**：`content` 和 `image_ids` 至少传其一，不能同时为空。

**请求示例**：

```
POST /api/tree-hole/ HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="content"

这是一条树洞留言
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image_ids"

img_a1b2c3d4e5f6,img_b2c3d4e5f6g7
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**成功响应** (HTTP 200)：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message_id": "msg_x1y2z3w4",
    "content": "这是一条树洞留言",
    "images": [
      {
        "image_id": "img_a1b2c3d4e5f6",
        "url": "/media/treehole/img_a1b2c3d4e5f6.png",
        "thumbnail_url": "/media/treehole/img_a1b2c3d4e5f6_thumb.png"
      },
      {
        "image_id": "img_b2c3d4e5f6g7",
        "url": "/media/treehole/img_b2c3d4e5f6g7.jpg",
        "thumbnail_url": "/media/treehole/img_b2c3d4e5f6g7_thumb.jpg"
      }
    ],
    "created_at": "2026-07-15T08:30:00Z"
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `data.message_id` | string | 留言唯一标识 |
| `data.content` | string | 留言文本内容 |
| `data.images` | array | 图片信息数组 |
| `data.images[].image_id` | string | 图片唯一标识 |
| `data.images[].url` | string | 图片完整 URL |
| `data.images[].thumbnail_url` | string | 缩略图 URL |
| `data.created_at` | string | 留言创建时间，ISO 8601 格式 |

**失败响应**：

内容为空 (HTTP 400)：

```json
{
  "code": 1006,
  "message": "请输入留言内容或上传图片",
  "data": null
}
```

内容超长 (HTTP 400)：

```json
{
  "code": 1002,
  "message": "留言内容不能超过 500 字",
  "data": null
}
```

图片数量超限 (HTTP 400)：

```json
{
  "code": 1005,
  "message": "最多上传 9 张图片",
  "data": null
}
```

**错误码**：

| 业务码 | HTTP 状态 | 场景 | 用户提示 | 前端处理建议 |
|:---|:---|:---|:---|:---|
| 1001 | 400 | 参数缺失 | 「请填写完整内容」 | 检查必填字段 |
| 1002 | 400 | 内容超过 500 字 | 「留言内容不能超过 500 字」 | 输入框红色边框提示 |
| 1005 | 400 | 图片超过 9 张 | 「最多上传 9 张图片」 | 禁用粘贴，Toast 提示 |
| 1006 | 400 | 内容和图片都为空 | 「请输入留言内容或上传图片」 | 发送按钮保持禁用 |
| 2001 | 401 | 未登录 | 「请先登录」 | 跳转登录页 |
| 9999 | 500 | 服务器错误 | 「系统繁忙，请稍后重试」 | Toast 提示，保留输入内容 |

**非功能性**：

| 维度 | 说明 |
|:---|:---|
| **限流** | 单用户每分钟最多 10 条留言 |
| **超时** | 客户端建议 15 秒超时 |
| **幂等性** | 客户端可携带 `X-Idempotency-Key` Header 防止重复提交 |

---

## 三、附录

### 3.1 枚举值字典

| 字段名 | 枚举值 | 说明 |
|:---|:---|:---|
| `code` | 0 | 成功 |
| `code` | 1001-1999 | 参数/业务校验错误 |
| `code` | 2001-2999 | 认证/授权错误 |
| `code` | 3001-3999 | 资源不存在/冲突 |
| `code` | 9999 | 系统错误 |

### 3.2 需求-交互-API 追溯矩阵

| 需求ID | 交互页面 | API 接口 | 状态 |
|:---|:---|:---|:---|
| REQ-001 | UI-001 输入框、粘贴功能 | API-001 上传树洞图片 | ✅ 已定义 |
| REQ-002 | UI-001 图片预览区、删除按钮 | API-001 上传树洞图片（返回缩略图 URL） | ✅ 已定义 |
| REQ-003 | UI-001 发送按钮、字数统计 | API-002 提交树洞留言 | ✅ 已定义 |
| REQ-004 | UI-001 错误处理、异常预案 | API-001 / API-002 错误码 | ✅ 已定义 |
| REQ-005 | UI-001 移动端上传按钮 | API-001 上传树洞图片（文件选择器复用） | ✅ 已定义 |