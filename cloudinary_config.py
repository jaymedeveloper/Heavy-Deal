import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="dt6rrmzxw",
    api_key="989313237337689",
    api_secret="2AqUHd82DY4T5q0CPzIHwBi0b6I",
    secure=True
)

def upload_image(file, folder="heavydeals"):
    try:
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder,
            allowed_formats=["jpg", "png", "jpeg", "webp"]
        )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"Upload error: {e}")
        return None