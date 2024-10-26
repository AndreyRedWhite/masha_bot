import boto3
from botocore.client import Config
from dotenv import load_dotenv
import os

# Загрузка переменных из .env
load_dotenv()

# Инициализация клиента S3 для MinIO
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("MINIO_ENDPOINT"),
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    config=Config(signature_version='s3v4')
)

# Загрузка файла в бакет
bucket_name = os.getenv("MINIO_BUCKET_NAME")
file_path = "/Users/Andrey.Vorontsov/Documents/archive.zip"  # Замените на реальный путь к файлу
object_name = "archive.zip"  # Имя файла в бакете

try:
    s3.upload_file(file_path, bucket_name, object_name)
    print(f"Файл {file_path} успешно загружен в бакет {bucket_name}")
except Exception as e:
    print(f"Ошибка загрузки файла: {e}")
