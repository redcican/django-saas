import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def generate_image_code(width=140, height=40, char_length=5, font_file='kumo.ttf', font_size=28):
    """use pillow to generate image code

    Args:
        width (int, optional): the width of image. Defaults to 120.
        height (int, optional): the height of image. Defaults to 30.
        char_length (int, optional): the length of verfiy code. Defaults to 5.
        font_file (str, optional): font for char to show on image. Defaults to 'kumo.ttf'.
        font_size (int, optional): font size. Defaults to 28.
    """
    
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')
    
    def rndChar():
        """generate random char"""
        return chr(random.randint(65, 90))
    
    def rndColor():
        """generate random color"""
        return (random.randint(0, 255), random.randint(10, 255), random.randint(64, 255))
    
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rndChar()
        code.append(char)
        h=random.randint(0,4)
        draw.text((i * width / char_length, h), char, font=font, fill=rndColor())
        
    # draw dots
    for i in range(30):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=rndColor())
        
    # draw circles
    for i in range(30):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=rndColor())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rndColor())
        
    # draw lines
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=rndColor())
        
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, ''.join(code)