import os
from fastapi import UploadFile, HTTPException
from typing import List

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "pdf", "docx"}
MAX_FILE_SIZE_MB = 10

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_upload_file(file: UploadFile):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")
    file.file.seek(0, os.SEEK_END)
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File too large.")
