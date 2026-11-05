from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGB", (1080, 1350))
draw = ImageDraw.Draw(img)

kecil = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
besar = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 84)

teks = "harga rumah"
print(len(teks))                        # 11 (jumlah karakter, selalu sama)
print(draw.textlength(teks, font=kecil))  # lebar kecil, misalnya sekitar 150
print(draw.textlength(teks, font=besar))  # lebar besar, misalnya sekitar 420
print(draw.textlength("iiiiiiiiii", font=kecil))  # sempit
print(draw.textlength("mmmmmmmmmm", font=kecil))  # jauh lebih lebar, padahal sama-sama 10 huruf
