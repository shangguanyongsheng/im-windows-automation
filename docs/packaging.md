# EXE 打包指南

将项目打包成 Windows exe，无需 Python 环境即可运行。

---

## 快速打包

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包命令

```bash
# 单文件打包
pyinstaller --onefile --name "IM-Windows-Automation" src/main.py

# 带 GUI 图标
pyinstaller --onefile --noconsole --icon=icon.ico src/main.py
```

### 3. 输出

打包后在 `dist/` 目录生成 `IM-Windows-Automation.exe`

---

## 一键打包脚本

**build.bat**

```batch
@echo off
echo 正在打包...

pip install pyinstaller
pyinstaller --onefile --name "IM-Windows-Automation" src/main.py

echo 打包完成！输出在 dist/ 目录
pause
```

双击 `build.bat` 即可打包。

---

## 用户使用流程

1. 下载 exe 文件
2. 配置 API Key（编辑同目录的 .env 文件）
3. 双击运行
4. 扫码登录微信
5. 在微信发消息控制 Windows

---

## 打包体积优化

```bash
# 排除不需要的大型模块
pyinstaller --onefile \
  --exclude-module matplotlib \
  --exclude-module numpy \
  --exclude-module pandas \
  src/main.py
```

---

## 注意事项

- 杀毒软件可能误报，需加入白名单
- 首次运行需要配置 API Key
- 建议以管理员权限运行