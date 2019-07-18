from PIL import  Image
class ImageConver:
    @classmethod
    def bmp(source,target,width=62,height=35):
        im = Image.open(source)
        imgs = im.convert("RGB")
        out = imgs.resize((width, height), Image.ANTIALIAS)
        out.save(target)


def test():
    list =["0cosco","1ccs","2lr","3abs","4dnv"]
    for cell in list:
        source = "/Users/micometer/Develop/quality_control/templates/%s.png"%cell
        target = "/Users/micometer/Develop/quality_control/templates/%s.bmp"%cell
        ImageConver.bmp(source,target)


if __name__ == "__main__":
    test()