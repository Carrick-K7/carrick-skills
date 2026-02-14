# image-uploader

图片上传图床 Skill，支持多平台。

## 功能

- 上传单张或多张图片到 Catbox
- 上传整个目录
- 带进度报告
- 可扩展其他图床（阿里云OSS预留）

## 使用方式

### 直接调用

```python
from image_uploader import upload_to_catbox, upload_directory

# 单文件
url = upload_to_catbox("image.png")[0]

# 多文件
urls = upload_to_catbox(["01.png", "02.png", "03.png"])

# 整个目录
urls = upload_directory("output/第08章_标题/")

# 带进度
result = upload_with_progress(["01.png", "02.png"])
# result = {"success": [...], "failed": [...]}
```

### 跨 Session 调用

```python
task = """
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills')
from upload import upload_directory

urls = upload_directory("output/第08章_标题/")
print(f"上传完成: {len(urls)} 个URL")
for url in urls:
    print(url)
"""
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `expiry` | 过期时间 | `24h` (可选: 1h, 12h, 24h, 72h) |
| `pattern` | 文件匹配 | `*.png` |

## 依赖

- requests
- pathlib

## 版本

v1.0.0 - 初始版本，支持 Catbox
