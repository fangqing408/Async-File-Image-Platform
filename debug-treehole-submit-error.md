# Debug Session: treehole-submit-error

## Metadata
- **Session ID**: treehole-submit-error
- **Status**: [CLOSED]
- **Created**: 2026-07-15
- **Resolved**: 2026-07-15
- **Description**: 用户提交树洞留言时显示"系统繁忙，请稍后重试"（code 9999）

## Hypotheses

| # | Hypothesis | Status | Evidence |
|:---|:---|:---|:---|
| H1 | `TreeHoleContent` 模型未正确导入到 services.py | ✅ 确认 | services.py 中缺少 TreeHoleContent 的导入 |
| H2 | 数据库字段变更导致 ORM 查询失败 | ❌ 排除 | 迁移已成功应用 |
| H3 | 视图层参数传递与服务层签名不匹配 | ❌ 排除 | 签名已匹配 |
| H4 | Django 迁移未正确应用导致表结构不一致 | ❌ 排除 | 迁移成功 |

## Root Cause

**`services.py` 中缺少 `TreeHoleContent` 模型的导入**，导致在 `submit_message` 方法中创建 `TreeHoleContent` 对象时抛出 `NameError` 异常，被全局异常捕获后返回"系统繁忙"错误。

## Fix Applied

**文件**: [services.py](file:///d:/Trae/Files/03-xmu-llap/xmu/services.py#L13)

在 `from .models import (...)` 中添加了 `TreeHoleContent`：

```python
from .models import (
    ...
    TreeHoleImage,
    TreeHoleContent,  # 新增
    TreeHoleMessage
)
```

## Verification

- ✅ 服务器启动成功，无报错
- ✅ Django 系统检查通过（0 issues）

## Cleanup

- 移除了 views.py 中的调试日志代码（待清理）
