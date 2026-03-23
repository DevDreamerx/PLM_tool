## PyInstaller 打包与图标（PyQt5）

PyInstaller 的 `--icon app.ico` / `icon=['app.ico']` 只会设置 **生成的 exe 文件图标**，不会自动设置 **窗口左上角图标**。窗口图标需要在代码里调用 `setWindowIcon()`（项目已在 `main.py` 中处理）。

### 推荐：用 spec 打包（已配置图标 + 资源）
```bash
pyinstaller main.spec
```

### 直接命令行打包（等价做法）
```bash
pyinstaller --onefile --windowed --icon app.ico --add-data "app.ico;." main.py
```

说明：
- `--add-data "app.ico;."` 用于把 `app.ico` 打进包里，确保运行时 `QIcon('app.ico')` 能找到图标（Windows 用 `;` 分隔）。
- 如果图标更新后仍显示旧图标，建议先清理：删除 `build/`、`dist/`，或加 `--clean`。

