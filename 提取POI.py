import requests
import json
import time

# 1. 填入你已经激活的【Web服务】凭证
AMAP_KEY = "6656b79d228d2d201eb95900f3cdd0d1"  #
CITY = "怀集县"
OUTPUT_FILE = "E:\学习\网络GIS\网站构建\my-gis-site\huaiji_all_kinds_of_pois.json"

# 2. 高德官方定义的 20 个核心行业大类编码前缀
# 01汽车 02摩托 03餐饮 04购物 05生活 06体育 07医疗 08住宿 09旅游 10国家机构
# 11文物 12商务住宅 13政府 14教育 15交通 16金融 17公司 18地名 19公共设施 20室内
BIG_CATEGORIES = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"
]

all_collected_data = []
seen_poi_ids = set()  # 用于自动给重复的数据去重

print(f"🚀 开始全量剥离【{CITY}】全行业空间地理要素...")

for category in BIG_CATEGORIES:
    page = 1
    print(f"📂 正在深度抓取行业大类：{category}0000 ...")
    
    while True:
        # 拼装高德标准接口URL，通过 types 指定大类，citylimit 限制死在怀集县境内
        url = f"https://restapi.amap.com/v3/place/text?types={category}0000&city={CITY}&citylimit=true&output=json&key={AMAP_KEY}&page={page}&offset=50"
        
        try:
            response = requests.get(url, timeout=10)
            res_json = response.json()
            
            if res_json.get("status") == "1":
                pois = res_json.get("pois", [])
                
                # 如果这一页没有数据返回了，说明这个行业大类在怀集全境已经被抽干了
                if not pois:
                    break
                
                # 遍历抓到的数据，清洗提取我们需要的核心字段
                for poi in pois:
                    p_id = poi.get("id")
                    if p_id not in seen_poi_ids:
                        seen_poi_ids.add(p_id)
                        
                        # 拆分高德的 "lng,lat" 字符串
                        loc = poi.get("location", "0,0").split(",")
                        
                        all_collected_data.append({
                            "名称": poi.get("name"),
                            "行业大类": poi.get("type"),
                            "分类编码": poi.get("typecode"),
                            "经度": float(loc[0]),
                            "纬度": float(loc[1]),
                            "详细地址": poi.get("address") if poi.get("address") else "暂无"
                        })
                
                print(f"   -> 已成功加载第 {page} 页，目前累计获取去重数据：{len(all_collected_data)} 条")
                page += 1
                time.sleep(0.1)  # 稍微歇 0.1 秒，温柔抓取，防止被高德封锁
            else:
                print(f"   ⚠️ 大类 {category}0000 抓取中断，高德提示: {res_json.get('info')}")
                break
                
        except Exception as e:
            print(f"   ❌ 抓取过程中网络遇到碰壁: {e}")
            break

# 3. 把捞上来的全量池保存为标准的 JSON 空间数据集
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_collected_data, f, ensure_ascii=False, indent=4)

print(f"\n🎉 降维打击完成！怀集全要素数据已全部存入本地文件：{OUTPUT_FILE}")
print(f"📊 最终总共帮你捞出了 {len(all_collected_data)} 条涵盖各行各业的精准地理要素！")