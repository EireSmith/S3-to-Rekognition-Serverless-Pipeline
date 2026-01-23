import boto3
import os
import sys
from PIL import Image
import add_user_data

#sample image to remove after testing 
user_jpg_var = "sample.jpg"

def check_image(user_image):
    # check the image format using pillow
    try:
        with Image.open(user_image) as img:
            if img.format in ['JPEG', 'JPG', 'PNG']:
                instance = ImageSendAWS(user_image)
                print("Image format is correct.")
                instance.user_image()
                return instance
            else:
                print("File is not an correct image format. Use `JPEG`, `JPG`, or `PNG`.")
                return None
    except IOError:
        print("ioerror: cannot open file.")
        return None


class ImageSendAWS():
    # I want the class to send two files; one image and one data file
    # detailing user info, time/date/-stamps, etc.

    # checking image is passed to class
    def __init__(self, file):
        self.file = file

    def user_image(self):
        isattached = self.file

        if isattached:
            print(f"passed: {self.file}")
        else:
            # no file attached
            print("No file attached to ImageSendAWS instance.")
            sys.exit(1)

    # credentials for AWS S3 bucket
    s3_client = boto3.client('s3')
    bucket_name = os.getenv("AWS_S3_BUCKET")


    def send_to_s3(self, file=None):
        # allow using the instance file when no file argument provided
        if file is None:
            file = getattr(self, 'file', None)

        if not file:
            print("No file path provided to send to s3.")
            return

        if not os.path.exists(file):
            print(f"File does not exist: {file}")
            return

        try:
            #extract file name from path
            object_name = os.path.basename(file)
            
            self.s3_client.upload_file(file, self.bucket_name, object_name)
            print(f"Successfully uploaded {file} to {self.bucket_name}")
        except Exception as e:
            print(f"Error uploading file: {e}")


#add user data to image file.

instance_metadata = add_user_data(user_jpg_var)
if instance_metadata:
    print("User data added successfully.")
else:
    print("Failed to add user data.")

# Validate the image and get an instance of ImageSendAWS if valid
instance = check_image(user_jpg_var)
if instance:
    # upload the same file validated before
    instance.send_to_s3()
else:
    print("Image validation failed. Skipping upload.")

