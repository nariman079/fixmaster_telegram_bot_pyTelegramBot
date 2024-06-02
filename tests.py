from config.settings import s3, bucket_name

def test_upload_file():
    s3.upload_file(
                Filename='photos/file_3.jpg',
                Bucket=bucket_name,
                Key='photos/file_3.jpg'
            )

test_upload_file()