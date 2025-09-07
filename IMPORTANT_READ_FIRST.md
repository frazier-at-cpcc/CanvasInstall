# ⚠️ IMPORTANT: Which File to Run

## ✅ USE THIS FILE
```bash
sudo python3 install_canvas.py
```

## ❌ DO NOT USE
```bash
sudo python3 canvas_installer.py  # This is the old monolithic version
```

---

## Quick Start

1. **Run the correct installer**:
   ```bash
   sudo python3 install_canvas.py
   ```

2. **The installer will automatically**:
   - Install required dependencies (Rich library)
   - Handle Ubuntu 22.04 compatibility issues
   - Guide you through the installation process

---

## If You See Import Errors

If you see errors like `cannot import name 'TaskProgressColumn'`, you're likely running the wrong file. 

**Solution**: Use `install_canvas.py` instead of `canvas_installer.py`

---

## File Structure

- **`install_canvas.py`** ← **RUN THIS** (New modular installer)  
- **`canvas_installer.py`** ← Don't use (Legacy monolithic version)
- **`canvas_installer/`** ← Modular installer package (used by install_canvas.py)

---

The new modular installer (`install_canvas.py`) handles all compatibility issues with Ubuntu 22.04's Rich library version automatically.