import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix docstring comment and add photos field
old_header = "// ====== 怀集县全量POI数据（不依赖API）======"
new_header = "// ====== 怀集县全量POI数据（含图片）======"
text = text.replace(old_header, new_header)

# 2. Make sure ALL_POIS has photos:[] on each entry
text = text.replace(",desc:'中国最佳溶洞奇观", ",desc:'中国最佳溶洞奇观，万燕归巢壮景，被誉为岭南第一洞',photos:['https://aos-comment.amap.com/B02F602DPT/comment/20260316-4e6f83b7bba19d0d27c19cb9-Anu1P84koMb8ACIoT6uGp0.jpg']")
text = text.replace(",desc:'陶渊明笔下桃花源原型地", ",desc:'陶渊明笔下桃花源原型地，溪流潺潺，桃林环绕',photos:[]")

# Add photos:[] to all remaining desc entries that don't have it
# Use regex: desc:'...'}, -> desc:'...',photos:[]},
import re
def add_photos(m):
    s = m.group(0)
    if "photos:" not in s:
        s = s.replace("}',", ",photos:[]}',")
    return s

text = re.sub(r"desc:'[^']*'\},", add_photos, text)
text = re.sub(r'desc:"[^"]*"\},', add_photos, text)

# 3. Ensure loadAll uses photos field
text = text.replace("photos:p.photos||[]", "photos:p.photos||[]")

# 4. Check for remaining duplicates
while 'function loadPhotos(id,cb){cb([])}function loadPhotos' in text:
    text = text.replace('function loadPhotos(id,cb){cb([])}function loadPhotos', 'function loadPhotos')
    print('Removed duplicate loadPhotos')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done')
