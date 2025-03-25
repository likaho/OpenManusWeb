import argparse
import os
import sys
from pathlib import Path

import uvicorn


# 检查WebSocket依赖
def check_websocket_dependencies():
    pass

    return True


# 确保目录结构存在
def ensure_directories():
    # 创建templates目录
    templates_dir = Path("app/web/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # 创建static目录
    static_dir = Path("app/web/static")
    static_dir.mkdir(parents=True, exist_ok=True)

    # 确保__init__.py文件存在
    init_file = Path("app/web/__init__.py")
    if not init_file.exists():
        init_file.touch()


if __name__ == "__main__":
    # 添加命令行参数
    parser = argparse.ArgumentParser(description="OpenManus Web Application Server")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser on startup")
    parser.add_argument("--port", type=int, default=8000, help="Server listening port number (default: 8000)")

    args = parser.parse_args()

    ensure_directories()

    if not check_websocket_dependencies():
        print("Exit the application. Please install necessary dependencies and try again.")
        sys.exit(1)

    # 设置环境变量以控制是否自动打开浏览器
    if args.no_browser:
        os.environ["AUTO_OPEN_BROWSER"] = "0"
    else:
        os.environ["AUTO_OPEN_BROWSER"] = "1"

    port = args.port

    print(f"🚀 The OpenManus web application is starting up...")
    print(f"访问 http://localhost:{port} 开始使用")

    uvicorn.run("app.web.app:app", host="0.0.0.0", port=port, reload=True)
