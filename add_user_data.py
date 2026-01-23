from PIL import Image

metadata_file = "user_data.txt"
def add_user_data(image_file, metadata_file=metadata_file):
    try:
        with Image.open(image_file) as img:
            if img.format in ['JPEG', 'JPG', 'PNG', 'TIFF']:
                print("Image format is correct.")
                return True
            else:
                print("File is not an correct image format. Use `JPEG`, `JPG`, or `PNG`.")
                return False
    except IOError:
        print("ioerror: cannot open file.")
        return False
