from minio import Minio
from settings.config import settings

minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False
)

def upload_profile_picture(file, filename: str):
    bucket = settings.minio_bucket
    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
    minio_client.put_object(bucket, filename, file.file, length=-1, part_size=10*1024*1024)
    return f"http://{settings.minio_endpoint}/{bucket}/{filename}"