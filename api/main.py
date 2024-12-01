from fastapi import FastAPI, File, UploadFile, HTTPException
import zipfile
import tempfile
import os
import subprocess
from typing import List, Dict

app = FastAPI()


@app.post("/scan-zip/")
async def scan_notebooks_in_zip(file: UploadFile = File(...)):
    """
    API to scan a ZIP file containing Jupyter notebooks using nbdefense.

    Args:
        file (UploadFile): The uploaded ZIP file containing .ipynb files.

    Returns:
        dict: Scan results for each notebook.
    """
    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a ZIP file."
        )

    # Save the uploaded ZIP file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        tmp_zip.write(await file.read())
        zip_file_path = tmp_zip.name

    try:
        # Extract the ZIP file
        extracted_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid ZIP file.")

        # Scan all extracted .ipynb files
        scan_results: List[Dict[str, str]] = []
        for root, _, files in os.walk(extracted_dir):
            for file_name in files:
                if file_name.endswith(".ipynb"):
                    file_path = os.path.join(root, file_name)
                    try:
                        # Run nbdefense scan on the file
                        result = subprocess.run(
                            ["nbdefense", file_path],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        scan_results.append({"file": file_name, "output": result.stdout})
                    except subprocess.CalledProcessError as e:
                        scan_results.append({"file": file_name, "error": e.stderr})

        return {"message": "Scan completed", "results": scan_results}

    finally:
        # Cleanup temporary files and directory
        os.remove(zip_file_path)
        for root, dirs, files in os.walk(extracted_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))