
def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def img_pixelMatchesColor(img, coord, rgb, tolerence=0):
    x = 0
    for i in rgb:
        if img.getpixel(coord)[x] < rgb[x] - tolerence or img.getpixel(coord)[x] > rgb[x] + tolerence:
            return False
        x = x + 1
    return True