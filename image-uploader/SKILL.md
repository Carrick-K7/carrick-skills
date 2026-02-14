# Image Uploader Skill

## 描述

图片上传图床工具，支持批量上传、进度报告，接口统一可扩展。

## 功能

- **Catbox 上传**: 临时图床，24小时有效期
- **批量上传**: 支持单文件、多文件、整个目录
- **进度报告**: 实时显示上传状态
- **可扩展**: 预留阿里云OSS等其他平台接口

## 使用方式

### 基础用法

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills')
from upload import upload_to_catbox

# 单文件
urls = upload_to_catbox("image.png")

# 多文件
urls = upload_to_catbox(["01.png", "02.png", "03.png"])
```

### 目录上传

```python
from upload import upload_directory

urls = upload_directory(
    dir_path="output/第08章_标题/",
    pattern="*.png",
    expiry="24h"
)
```

### 带进度报告

```python
from upload import upload_with_progress

result = upload_with_progress(["01.png", "02.png", "03.png"])
# 返回: {"success": [{"file": "...", "url": "..."}], "failed": [...]}
```

### 跨 Session 调用

```python
# 在另一个 session 中执行
task = """
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills')
from upload import upload_directory

output_dir = "output/第09章_标题/"
urls = upload_directory(output_dir)

print(f"✅ 上传完成: {len(urls)} 张图片")
for i, url in enumerate(urls, 1):
    print(f"{i}. {url}")
"""

# 使用 sessions_spawn 调用
sessions_spawn(task=task, label="upload-images")
```

## 返回值

所有上传函数返回 URL 列表（字符串列表），按文件名排序。

## 配置

### Catbox 过期时间

- `1h` - 1小时
- `12h` - 12小时
- `24h` - 24小时（默认）
- `72h` - 72小时

## 扩展其他图床

预留接口，可添加 `aliyun.py`, `qiniu.py` 等模块：

```python
# upload.py 中添加
from .aliyun import upload_to_oss

# 统一入口
def upload(files, provider="catbox", **kwargs):
    if provider == "catbox":
        return upload_to_catbox(files, **kwargs)
    elif provider == "aliyun":
        return upload_to_oss(files, **kwargs)
```

## 依赖

- Python 3.8+
- requests
- pathlib (标准库)

## 版本历史

- v1.0.0 - 初始版本，支持 Catbox 上传
