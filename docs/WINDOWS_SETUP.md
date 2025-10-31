# Windows Setup Guide

This guide provides step-by-step instructions for setting up the RAG Pipeline on Windows.

## 🎯 Prerequisites

### 1. Install Visual C++ Redistributable (REQUIRED)

PyTorch (used by sentence-transformers) requires the Microsoft Visual C++ Redistributable to be installed on Windows.

**Download and Install:**
1. Download: [vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Run the installer
3. Follow the installation wizard
4. **Restart your PowerShell terminal** after installation

**Why is this needed?**
PyTorch includes compiled C++ libraries (like `c10.dll`) that depend on the Visual C++ runtime. Without it, you'll get errors like:
```
OSError: [WinError 1114] Error loading "c10.dll" or one of its dependencies.
```

### 2. Install Python 3.11+

Download Python from [python.org](https://www.python.org/downloads/) or use:
```powershell
winget install Python.Python.3.11
```

Verify installation:
```powershell
python --version
# Should show Python 3.11.x or higher
```

## 🚀 Installation Steps

### Step 1: Install uv (Recommended Package Manager)

```powershell
# Using pip
pip install uv

# Or using PowerShell installer
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Clone the Repository

```powershell
cd D:\projects\python  # Or your preferred location
git clone https://github.com/wedsamuel1230/rag-pipeline.git
cd rag-pipeline
```

### Step 3: Install Dependencies

```powershell
# Using uv (recommended - handles versions correctly)
uv sync

# Or using pip
pip install -e .
```

**Important Notes:**
- First installation will download ~500MB of dependencies
- PyTorch is the largest dependency (~200MB)
- Sentence transformer models (~100MB) download on first run

### Step 4: Set Your POE API Key

Get your API key from [poe.com](https://poe.com), then set it:

```powershell
# Temporary (current session only)
$env:POE_API_KEY = "your-api-key-here"

# Permanent (add to PowerShell profile)
notepad $PROFILE
# Add this line to the file:
$env:POE_API_KEY = "your-api-key-here"
```

## ✅ Verify Installation

### Test GUI Launch

```powershell
uv run gui_main.py
```

Expected result: A window opens with "RAG Pipeline - PDF Q&A System" title.

### Test CLI

```powershell
uv run cli_main.py
```

Expected result: Command-line interface starts without errors.

## 🐛 Common Windows Issues

### Issue 1: DLL Error (c10.dll)

**Symptom:**
```
OSError: [WinError 1114] 動態連結程式庫 (DLL) 初始化例行程序失敗
```

**Solution:**
Install Visual C++ Redistributable (see Prerequisites above).

### Issue 2: Execution Policy Error

**Symptom:**
```
... cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 3: Path Too Long

**Symptom:**
```
[Errno 2] No such file or directory: '...[very long path]...'
```

**Solution:**
Enable long path support:
1. Open Registry Editor (Win + R, type `regedit`)
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` to `1`
4. Restart your computer

Or move the project to a shorter path (e.g., `C:\Projects\rag-pipeline`).

## 🎨 GUI Features on Windows

The Tkinter GUI provides a native Windows look and feel:

- **File picker**: Standard Windows file selection dialog
- **Model selection**: Dropdown with 12+ LLM models
- **Streaming responses**: Real-time answer updates
- **Native widgets**: Windows-native buttons, labels, and text areas

## 🔧 Performance Tips

### Windows Defender Exclusion

Add your project folder to Windows Defender exclusions to speed up file operations:

```powershell
# Run as Administrator
Add-MpPreference -ExclusionPath "D:\projects\python\rag-pipeline"
```

### Use SSD Storage

For best performance:
- Store the project on an SSD (not HDD)
- The ML model cache (`.cache/`) benefits significantly from SSD speeds

### Resource Monitoring

Monitor resource usage:
```powershell
# Open Task Manager
taskmgr

# Look for "python.exe" process
# Expected usage:
# - RAM: 1-2GB (idle), 2-4GB (processing)
# - CPU: 10-30% (idle), 50-100% (embedding generation)
```

## 📝 Development on Windows

### Using VS Code

Recommended extensions:
- Python
- Pylance
- Python Debugger

Open the project:
```powershell
code .
```

### Running Tests

```powershell
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_integration.py

# Run with coverage
uv run pytest --cov=src
```

### Building for Distribution

```powershell
# Create standalone executable (optional)
pip install pyinstaller
pyinstaller --onefile --windowed gui_main.py
# Output: dist/gui_main.exe
```

## 🌐 Proxy Configuration

If behind a corporate proxy:

```powershell
# Set proxy for pip/uv
$env:HTTP_PROXY = "http://proxy.company.com:8080"
$env:HTTPS_PROXY = "http://proxy.company.com:8080"

# For authenticated proxy
$env:HTTP_PROXY = "http://username:password@proxy.company.com:8080"
```

## 📚 Additional Resources

- [uv Documentation](https://docs.astral.sh/uv)
- [PyTorch Windows FAQ](https://pytorch.org/get-started/locally/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

---

**Need help?** Open an issue on [GitHub Issues](https://github.com/wedsamuel1230/rag-pipeline/issues) with:
- Your Windows version (`winver`)
- Python version (`python --version`)
- Error message (full traceback)
- Output of `uv pip list`
