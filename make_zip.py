import zipfile
import os

zip_name = "Warehouse-Inventory-and-Procurement-Backend.zip"
exclude_dirs = {"__pycache__", ".pytest_cache", ".git", "venv", ".idea", ".vscode"}
exclude_files = {zip_name, "make_zip.py"}

with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files or file.endswith(".pyc"):
                continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, ".")
            zipf.write(file_path, arcname)

print(f"Created {zip_name} successfully ({os.path.getsize(zip_name)} bytes)")
