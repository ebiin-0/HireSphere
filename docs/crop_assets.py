from PIL import Image

im = Image.open('django_backend/static/img/fig_41_1.jpeg')
w, h = im.size
print("Size of fig_41_1:", w, h)

# In fig_41_1 (1600 x 765):
# Right side image is approximately from x=850 to 1550, y=140 to 720
# Let's crop it and save as hero_people.jpg
hero = im.crop((870, 160, 1550, 715))
hero.save('django_backend/static/img/hero_people.jpg', quality=95)
print("Saved hero_people.jpg:", hero.size)

# Also let's extract the HireSphere logo icon from the top left
# In fig_41_1: top left is from x=120, y=30 to x=290, y=70
logo = im.crop((125, 30, 290, 70))
logo.save('django_backend/static/img/hiresphere_logo.jpg', quality=95)
print("Saved hiresphere_logo.jpg:", logo.size)

# Also let's crop the Alex Rivera avatar from fig_44_1 (1600 x 762):
im44 = Image.open('django_backend/static/img/fig_44_1.jpeg')
# In fig_44_1: top right navbar has Alex Rivera avatar around x=1360, y=30, size ~35x35
# And big profile picture on left card around x=330, y=190, size ~140x140
avatar_large = im44.crop((320, 195, 480, 355))
avatar_large.save('django_backend/static/img/alex_avatar.jpg', quality=95)
print("Saved alex_avatar.jpg:", avatar_large.size)
