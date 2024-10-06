# R2-D2
Build Log for the loveable R2-D2.
![IMG_2630](https://github.com/user-attachments/assets/e467f149-7fe7-494c-9634-dbb1c33f6af6) | width 100 
from PIL import Image

def resize_image(input_path, output_path, size):
    """
    Resize an image to the specified size and save it to a new file.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the resized image.
        size (tuple): New size as (width, height).
    """
    with Image.open(input_path) as img:
        resized_img = img.resize(size)
        resized_img.save(output_path)
        print(f"Image resized and saved to {output_path}")

# Example usage:
resize_image('(https://github.com/user-attachments/assets/e467f149-7fe7-494c-9634-dbb1c33f6af6)', 'path_to_output_image.jpg', (800, 600))
