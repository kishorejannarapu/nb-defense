import os
import zipfile
import requests


def zip_ipynb_files(directory, output_zip):
    """
    Create a ZIP file containing all *.ipynb files in the directory.

    Args:
        directory (str): The root directory to search for .ipynb files.
        output_zip (str): The output ZIP file path.
    """
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".ipynb"):
                    # Preserve relative path
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    zipf.write(file_path, arcname=relative_path)
    print(f"Created ZIP file: {output_zip}")


def send_zip_to_api(zip_path, api_url):
    """
    Send the ZIP file to the API.

    Args:
        zip_path (str): Path to the ZIP file.
        api_url (str): URL of the API endpoint.
    """
    with open(zip_path, "rb") as zip_file:
        files = {"file": (os.path.basename(zip_path), zip_file, "application/zip")}
        response = requests.post(api_url, files=files)

    if response.status_code == 200:
        print("API Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    # Directory containing the *.ipynb files
    directory_to_scan = "./"
    # Output ZIP file path
    output_zip_file = "./notebooks.zip"
    # API URL
    api_url = "http://127.0.0.1:8000/scan-notebook/"

    # Step 1: Create ZIP
    zip_ipynb_files(directory_to_scan, output_zip_file)

    # Step 2: Send ZIP to API
    # send_zip_to_api(output_zip_file, api_url)