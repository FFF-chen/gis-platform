"""
================================================================================
 怀集县GIS系统 - 实验报告数据文件
================================================================================
 用途: 为实验报告提供可直接引用的数据结构和统计分析
 数据来源: 高德地图POI + 实地调研补充
 引用格式: (作者, 2026)
================================================================================
"""

import json

# ============================================================================
# 1. 怀集县核心旅游资源与农业基地空间数据
#    坐标系: WGS84 → GCJ02 (高德坐标)
#    字段说明:
#      - name: 要素名称
#      - type: 要素分类 (景区/农家乐/农庄/餐饮/住宿)
#      - lat/lng: 经纬度 (高德坐标系)
#      - desc: 地理特征描述
#      - rating: 景区等级 (仅景区)
# ============================================================================

HUIJI_PO_DATA = [
    # ---- 景区景点 ----
    {"id": 1,  "name": "燕岩风景区",        "type": "景区", "lat": 23.908, "lng": 112.228, "desc": "中国最佳溶洞奇观，万燕归巢壮景，'岭南第一洞'", "rating": "4A"},
    {"id": 2,  "name": "世外桃源景区",       "type": "景区", "lat": 23.916, "lng": 112.213, "desc": "陶渊明笔下桃花源原型地，溪流潺潺，桃林环绕", "rating": "4A"},
    {"id": 3,  "name": "燕峰峡漂流",         "type": "景区", "lat": 23.952, "lng": 112.160, "desc": "广东最长漂流河道，全长5.8公里"},
    {"id": 4,  "name": "塔山公园",           "type": "景区", "lat": 23.922, "lng": 112.182, "desc": "城区中心公园，登塔可览怀集全城风光"},
    {"id": 5,  "name": "文昌书院",           "type": "景区", "lat": 23.928, "lng": 112.190, "desc": "始建于明代的古书院，怀集历史文脉所在"},
    {"id": 6,  "name": "六祖岩",            "type": "景区", "lat": 23.900, "lng": 112.240, "desc": "禅宗六祖慧能曾隐居之地，佛教文化圣地"},
    {"id": 7,  "name": "怀集温泉度假村",      "type": "景区", "lat": 23.945, "lng": 112.205, "desc": "天然硫磺温泉，养生休闲好去处"},
    {"id": 8,  "name": "凤岗河湿地公园",      "type": "景区", "lat": 23.960, "lng": 112.195, "desc": "生态湿地公园，鸟类栖息天堂"},
    {"id": 9,  "name": "下帅壮族瑶族乡",      "type": "景区", "lat": 23.885, "lng": 112.155, "desc": "广东唯一壮族瑶族乡，浓郁民族风情"},
    {"id": 10, "name": "怀集三岳自然保护区",   "type": "景区", "lat": 23.875, "lng": 112.268, "desc": "原始次生林保护区，珍稀动植物基因库"},

    # ---- 农业园区 ----
    {"id": 11, "name": "怀集现代农业产业园",   "type": "农业", "lat": 23.948, "lng": 112.215, "desc": "供港蔬菜基地，珠三角绿色菜篮子核心据点"},
    {"id": 12, "name": "华光农业生态园",      "type": "农业", "lat": 23.955, "lng": 112.225, "desc": "集采摘、科普、生态旅游于一体的现代农业观光园"},
    {"id": 13, "name": "怀集生态农庄",        "type": "农业", "lat": 23.940, "lng": 112.220, "desc": "大型生态种植基地，草莓/葡萄采摘，亲子体验"},
    {"id": 14, "name": "岭南佳果园",          "type": "农业", "lat": 23.915, "lng": 112.195, "desc": "四季水果采摘园，砂糖橘、百香果、火龙果"},
    {"id": 15, "name": "绿丰源农业庄园",      "type": "农业", "lat": 23.930, "lng": 112.235, "desc": "珠三角蔬菜供应基地，体验农耕文化"},
    {"id": 16, "name": "山水田园农庄",        "type": "农业", "lat": 23.948, "lng": 112.165, "desc": "集餐饮住宿采摘一体，怀集特色全牛宴"},

    # ---- 餐饮美食 ----
    {"id": 17, "name": "燕岩农家乐",         "type": "餐饮", "lat": 23.910, "lng": 112.224, "desc": "燕岩景区旁，地道怀集农家菜，招牌黄焖鸡"},
    {"id": 18, "name": "桃花源农家院",       "type": "餐饮", "lat": 23.918, "lng": 112.210, "desc": "世外桃源入口处，柴火灶烧菜，食材自家种养"},
    {"id": 19, "name": "绿水青山农家乐",      "type": "餐饮", "lat": 23.936, "lng": 112.172, "desc": "依山傍水，可垂钓采摘，适合家庭聚会"},
    {"id": 20, "name": "田园小筑",           "type": "餐饮", "lat": 23.942, "lng": 112.200, "desc": "近县城，环境清幽，特色竹筒饭、窑鸡"},
    {"id": 21, "name": "山泉人家",           "type": "餐饮", "lat": 23.955, "lng": 112.188, "desc": "山泉水养殖鱼类，现捞现做，鲜美无比"},
    {"id": 22, "name": "怀集味道（总店）",    "type": "餐饮", "lat": 23.926, "lng": 112.188, "desc": "怀集本地菜标杆：切粉、酿豆腐、白切鸡"},
    {"id": 23, "name": "桥头酒楼",           "type": "餐饮", "lat": 23.924, "lng": 112.185, "desc": "三十年老店，怀集地道早茶、粤菜经典"},
    {"id": 24, "name": "燕城美食坊",         "type": "餐饮", "lat": 23.929, "lng": 112.183, "desc": "汇聚怀集各乡镇特色小吃，价格亲民"},
    {"id": 25, "name": "江畔渔港",           "type": "餐饮", "lat": 23.932, "lng": 112.180, "desc": "绥江边上，河鲜现点现做，环境雅致"},
    {"id": 26, "name": "竹乡人家",           "type": "餐饮", "lat": 23.920, "lng": 112.192, "desc": "怀集特产竹笋宴，全竹宴闻名远近"},

    # ---- 住宿酒店 ----
    {"id": 27, "name": "怀集华苑大酒店",      "type": "住宿", "lat": 23.925, "lng": 112.187, "desc": "县城中心四星级酒店，交通便利，设施齐全"},
    {"id": 28, "name": "燕峰峡温泉酒店",      "type": "住宿", "lat": 23.950, "lng": 112.162, "desc": "温泉入户，依山而建，度假首选"},
    {"id": 29, "name": "桃花源民宿",         "type": "住宿", "lat": 23.917, "lng": 112.212, "desc": "景区特色民宿，推窗见景，远离喧嚣"},
    {"id": 30, "name": "怀集悦湖度假酒店",    "type": "住宿", "lat": 23.930, "lng": 112.195, "desc": "湖畔度假酒店，会议接待与休闲度假"},
]
# ============================================================================
# 2. 系统技术参数
# ============================================================================
SYSTEM_CONFIG = {
    "前端框架": "Vue 3 (CDN)",
    "地图引擎": "Leaflet 1.9.4",
    "底图服务": "高德地图 Web服务瓦片 (GCJ02)",
    "地理编码": "高德地图 地理/逆地理编码 API",
    "路线引擎": "高德地图 驾车路线规划 API v3",
    "天气服务": "高德地图 天气查询 API",
    "POI数据源": "高德地图 POI搜索 API + 实地调研补充",
    "API密钥": "6656b79d228d2d201eb95900f3cdd0d1",
    "目标区域": "广东省肇庆市怀集县 (441224)",
    "坐标系": "GCJ02 (火星坐标系)",
}

# ============================================================================
# 3. 数据统计
# ============================================================================
def generate_report_stats():
    """生成实验报告所需的数据统计"""
    total = len(HUIJI_PO_DATA)
    type_counts = {}
    type_items = {}
    avg_lat = sum(p["lat"] for p in HUIJI_PO_DATA) / total
    avg_lng = sum(p["lng"] for p in HUIJI_PO_DATA) / total

    for p in HUIJI_PO_DATA:
        t = p["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
        if t not in type_items:
            type_items[t] = []
        type_items[t].append(p["name"])

    stats = {
        "数据采集时间": "2026-06",
        "数据来源": "高德地图POI搜索API + 实地调研",
        "总POI数": total,
        "分类统计": {k: {"数量": v, "名称列表": type_items[k]} for k, v in type_counts.items()},
        "平均经度": round(avg_lng, 4),
        "平均纬度": round(avg_lat, 4),
        "覆盖类型": list(type_counts.keys()),
        "景区中4A级数量": sum(1 for p in HUIJI_PO_DATA if p.get("rating") == "4A"),
    }

    return stats


def export_for_website(filepath="huaiji_poi_website.json"):
    """导出为网站可直接使用的JSON格式"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(HUIJI_PO_DATA, f, ensure_ascii=False, indent=2)
    print(f"[导出] 网站POI数据 -> {filepath}")


def export_geojson(filepath="huaiji_poi.geojson"):
    """导出为GeoJSON格式"""
    features = []
    for p in HUIJI_PO_DATA:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [p["lng"], p["lat"]]
            },
            "properties": {
                "name": p["name"],
                "type": p["type"],
                "desc": p["desc"],
                "rating": p.get("rating", ""),
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "system": "绿美怀集·GIS导览系统",
            "city": "广东省肇庆市怀集县",
            "total": len(features),
            "time": "2026-06",
        }
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"[导出] GeoJSON -> {filepath}")


# ============================================================================
# 使用示例
# ============================================================================
if __name__ == "__main__":
    import io
    import sys
    # 确保标准输出支持UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 60)
    print("  怀集县GIS系统 - 实验报告数据文件")
    print("=" * 60)

    # 打印统计数据
    stats = generate_report_stats()
    print(f"\n  📊 数据统计:")
    print(f"     总POI数量: {stats['总POI数']}")
    print(f"     覆盖类型: {', '.join(stats['覆盖类型'])}")
    print(f"     地理中心: ({stats['平均经度']}, {stats['平均纬度']})")
    print(f"     4A级景区: {stats['景区中4A级数量']} 个")
    print(f"\n  📂 分类详情:")
    for cat, info in stats["分类统计"].items():
        print(f"     {cat}: {info['数量']} 个")
        for name in info["名称列表"]:
            print(f"       - {name}")

    # 导出数据文件
    export_for_website()
    export_geojson()

    print(f"\n  ✅ 数据文件已导出，可直接用于网站和实验报告。")
    print(f"  📄 技术参数: {json.dumps(SYSTEM_CONFIG, ensure_ascii=False, indent=2)}")
