# Video Clip Assembler — 部署指南

> 版本：1.0 | 更新日期：2026-04-01

---

## 1. 本地运行（当前方式）

### 前置条件

| 依赖 | 说明 |
|------|------|
| Python 3.9+ | macOS 自带或通过 pyenv 安装 |
| ffmpeg | 通过 `imageio-ffmpeg` 自带，无需单独安装 |
| Python venv | 复用 `~/.claude/skills/xhs-video-downloader/.venv` |
| Gemini API Key | 需设置环境变量 `GEMINI_API_KEY` |

### venv 中需要的包

```
google-generativeai >= 0.8.6
imageio-ffmpeg >= 0.6.0
httpx >= 0.28.1
```

### 一键启动

```bash
bash ~/.claude/skills/video-clip-assembler/scripts/launch.sh
```

`launch.sh` 会自动：
1. 激活 Python venv
2. 检查 `GEMINI_API_KEY`（或 `GOOGLE_API_KEY`）
3. 创建 temp 目录
4. 启动 HTTP 服务（默认端口 8765）
5. 用浏览器打开 `http://localhost:8765`

### 手动启动

```bash
source ~/.claude/skills/xhs-video-downloader/.venv/bin/activate
export GEMINI_API_KEY="你的API密钥"
cd ~/.claude/skills/video-clip-assembler/scripts
python server.py
```

---

## 2. 临时分享（SSH 隧道）

无需注册，利用 `localhost.run` 免费服务：

```bash
# 确保本地服务已启动（端口 8765）
ssh -R 80:localhost:8765 nokey@localhost.run
```

终端会输出公网地址，如：
```
https://a8bf1eb9aebe0e.lhr.life
```

将此链接发给对方即可。

**注意事项**：
- 你的电脑必须保持开机且网络连接
- SSH 断开后链接失效，重连会生成新地址
- 所有数据处理和 API 调用走你的机器
- 无用户认证，任何知道链接的人都能访问
- 免费版带宽有限，大文件传输可能较慢

**关闭隧道**：`Ctrl+C` 终止 SSH 进程

---

## 3. 云服务器部署（推荐方案）

### 3.1 推荐配置

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2 核 | 4 核 |
| 内存 | 4 GB | 8 GB |
| 存储 | 40 GB SSD | 80 GB SSD |
| 系统 | Ubuntu 22.04 | Ubuntu 22.04 |
| 带宽 | 5 Mbps | 10+ Mbps |

> ffmpeg 视频处理是 CPU 密集型，4 核以上体验明显更好。

### 3.2 部署步骤

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg

# 2. 创建项目目录
mkdir -p /opt/video-clip-assembler
cd /opt/video-clip-assembler

# 3. 上传项目文件（从本地）
# scp -r ~/.claude/skills/video-clip-assembler/* user@server:/opt/video-clip-assembler/

# 4. 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install google-generativeai imageio-ffmpeg httpx

# 5. 设置环境变量
echo 'export GEMINI_API_KEY="你的API密钥"' >> ~/.bashrc
source ~/.bashrc

# 6. 修改 launch.sh 中的 venv 路径
# 将 VENV_DIR 改为 /opt/video-clip-assembler/venv

# 7. 启动服务（后台运行）
nohup python scripts/server.py > server.log 2>&1 &
```

### 3.3 Nginx 反向代理（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 500M;  # 允许大文件上传

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 600s;  # 长任务需要长超时
        proxy_send_timeout 600s;
    }
}
```

### 3.4 HTTPS（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3.5 进程管理（systemd）

创建 `/etc/systemd/system/video-assembler.service`：

```ini
[Unit]
Description=Video Clip Assembler
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/video-clip-assembler/scripts
Environment=GEMINI_API_KEY=你的API密钥
ExecStart=/opt/video-clip-assembler/venv/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable video-assembler
sudo systemctl start video-assembler
sudo systemctl status video-assembler
```

---

## 4. 部署前需要改动的代码

部署到公网时，以下内容需要调整：

### 4.1 用户认证（必须）

当前无任何认证。建议加一个简单的密码保护：

```python
# server.py 中加一个简单的 token 校验
ALLOWED_TOKEN = os.environ.get("APP_TOKEN", "")

def check_auth(self):
    if ALLOWED_TOKEN:
        token = self.headers.get("Authorization", "").replace("Bearer ", "")
        if token != ALLOWED_TOKEN:
            self.send_json({"error": "Unauthorized"}, 401)
            return False
    return True
```

### 4.2 API Key 安全

- 绝对不要在前端暴露 Gemini API Key
- 当前架构中 API Key 只在后端使用，是安全的
- 但要确保 `.env` 文件不被版本控制追踪

### 4.3 临时文件清理

建议加定时清理机制：

```python
# 清理超过 1 小时的临时文件
import time
def cleanup_old_files(directory, max_age_hours=1):
    for item in Path(directory).iterdir():
        if time.time() - item.stat().st_mtime > max_age_hours * 3600:
            shutil.rmtree(item) if item.is_dir() else item.unlink()
```

### 4.4 多用户支持

当前 `http.server` 是单线程的，多用户并发会出问题。生产部署建议：
- 迁移到 **FastAPI** 或 **Flask**
- 用 **Gunicorn** 多 worker 进程
- 每个用户的 state 用 session 隔离

---

## 5. 环境变量

| 变量名 | 必须 | 说明 |
|--------|------|------|
| `GEMINI_API_KEY` | 是 | Google Gemini API 密钥 |
| `GOOGLE_API_KEY` | 否 | 备选（如果没设 GEMINI_API_KEY） |
| `PORT` | 否 | 服务端口，默认 8765 |
| `APP_TOKEN` | 否 | 简单认证 token（部署时建议设置） |

---

## 6. 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 端口被占用 | 之前的进程未退出 | `lsof -ti:8765 \| xargs kill -9` |
| Gemini 报错 | API Key 无效或配额用完 | 检查 key，查看 Google AI Studio 配额 |
| ffmpeg 找不到 | imageio_ffmpeg 未装 | `pip install imageio-ffmpeg` |
| 字幕乱码 | 字体文件缺失 | 确认 `fonts/NotoSansCJKsc-Bold.otf` 存在 |
| 上传失败 | 文件过大/网络超时 | 检查 Nginx `client_max_body_size` |
| 视频无声音 | 原始视频音轨问题 | 检查源视频是否有音频轨道 |
