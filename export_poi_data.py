"""
================================================================================
 怀集县空间地理要素数据采集与导出工具
 基于高德地图 Web服务 API 的全行业POI剥离
================================================================================
 实验目的: 采集怀集县全行业空间地理要素数据，构建网络GIS系统的数据库
 API密钥: 6656b79d228d2d201eb95900f3cdd0d1
 查询城市: 怀集县
 输出格式: JSON / CSV / GeoJSON
================================================================================
 使用方法:
   python export_poi_data.py              # 全量采集
   python export_poi_data.py --quick      # 快速采集（仅核心类别）
   python export_poi_data.py --export     # 从已有JSON导出CSV和GeoJSON
================================================================================
"""

import requests
import json
import time
import csv
import sys
import os
from datetime import datetime

# ============================================================================
# 配置参数
# ============================================================================
AMAP_KEY = "6656b79d228d2d201eb95900f3cdd0d1"  # 高德Web服务API密钥
CITY = "怀集县"
CITYCODE = "441224"  # 怀集县行政区划代码
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 输出文件路径
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "huaiji_pois_full.json")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "huaiji_pois_full.csv")
GEOJSON_OUTPUT = os.path.join(OUTPUT_DIR, "huaiji_pois_full.geojson")
STATS_OUTPUT = os.path.join(OUTPUT_DIR, "huaiji_pois_stats.json")

# ============================================================================
# 高德 POI 行业分类体系 (20个一级大类 + 旅游相关细分)
# ============================================================================
# 完整20个大类（用于学术报告展示）
ALL_BIG_CATEGORIES = {
    "01": "汽车服务",
    "02": "摩托车服务",
    "03": "餐饮服务",
    "04": "购物服务",
    "05": "生活服务",
    "06": "体育休闲",
    "07": "医疗保健",
    "08": "住宿服务",
    "09": "旅游景点",
    "10": "政府机构及社会团体",
    "11": "科教文化",
    "12": "商务住宅",
    "13": "农林牧渔",
    "14": "公司企业",
    "15": "交通设施",
    "16": "金融保险",
    "17": "地名地址",
    "18": "公共设施",
    "19": "道路附属",
    "20": "室内设施",
}

# 快速模式：只采集旅游相关的核心类别
QUICK_CATEGORIES = ["03", "04", "05", "06", "08", "09", "11"]

# 旅游细化分类（用于关键词搜索补充）
TOURISM_KEYWORDS = [
    "景区", "景点", "公园", "寺庙", "古镇", "温泉", "漂流",
    "农家乐", "采摘园", "农庄", "生态园", "民宿", "度假村",
    "特产", "美食", "餐厅", "酒店", "商场", "市场",
]


def fetch_pois_by_category(category_code, page=1):
    """
    通过高德 POI 搜索接口按行业大类采集数据
    API文档: https://lbs.amap.com/api/webservice/guide/api/search
    """
    url = (
        f"https://restapi.amap.com/v3/place/text"
        f"?types={category_code}0000"
        f"&city={CITY}"
        f"&citylimit=true"
        f"&output=json"
        f"&key={AMAP_KEY}"
        f"&page={page}"
        f"&offset=50"
    )
    try:
        resp = requests.get(url, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"   [错误] 请求失败: {e}")
        return None


def fetch_pois_by_keyword(keyword, page=1):
    """通过关键词搜索补充旅游相关POI"""
    url = (
        f"https://restapi.amap.com/v3/place/text"
        f"?keywords={keyword}"
        f"&city={CITY}"
        f"&citylimit=true"
        f"&output=json"
        f"&key={AMAP_KEY}"
        f"&page={page}"
        f"&offset=25"
    )
    try:
        resp = requests.get(url, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"   [错误] 关键词'{keyword}'请求失败: {e}")
        return None


def extract_poi_fields(poi):
    """从高德API返回的POI对象中提取标准化字段"""
    loc = poi.get("location", "0,0").split(",")
    return {
        "id": poi.get("id", ""),
        "名称": poi.get("name", ""),
        "大类": poi.get("type", "").split(";")[0] if poi.get("type") else "",
        "细类": poi.get("type", ""),
        "分类编码": poi.get("typecode", ""),
        "经度": float(loc[0]) if len(loc) == 2 else 0,
        "纬度": float(loc[1]) if len(loc) == 2 else 0,
        "地址": poi.get("address", "") or "暂无",
        "电话": poi.get("tel", "") or "",
        "评分": poi.get("biz_ext", {}).get("rating", "") if poi.get("biz_ext") else "",
        "营业时间": poi.get("biz_ext", {}).get("open_time", "") if poi.get("biz_ext") else "",
    }


def fetch_all_pois(categories, quick_mode=False):
    """
    全量采集：遍历指定大类，翻页直到数据为空
    返回去重后的POI列表
    """
    all_data = []
    seen_ids = set()

    category_source = QUICK_CATEGORIES if quick_mode else list(categories.keys())

    print(f"{'='*60}")
    print(f"  怀集县空间地理要素全量采集")
    print(f"  目标城市: {CITY} (区划代码: {CITYCODE})")
    print(f"  采集模式: {'快速（核心类别）' if quick_mode else '全量（20大类）'}")
    print(f"  目标类别数: {len(category_source)}")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    for code in category_source:
        cat_name = categories.get(code, code)
        page = 1
        cat_count = 0

        print(f"[采集] 大类 {code} - {cat_name} ...")

        while True:
            result = fetch_pois_by_category(code, page)

            if not result or result.get("status") != "1":
                if result:
                    print(f"   [中断] {result.get('info', '未知错误')}")
                break

            pois = result.get("pois", [])
            if not pois:
                break

            for poi in pois:
                pid = poi.get("id")
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    all_data.append(extract_poi_fields(poi))
                    cat_count += 1

            total = result.get("count", "?")
            print(f"   第{page}页 | 已采集 {cat_count} 条 | 该类总量约 {total}")
            page += 1
            time.sleep(0.08)  # 温和采集，避免触发限流

        print(f"   ✓ {cat_name} 采集完成 (累计总数据: {len(all_data)} 条)\n")

    # 补充旅游关键词搜索
    if not quick_mode:
        print("[补充] 旅游关键词深度搜索...")
        kw_count = 0
        for kw in TOURISM_KEYWORDS:
            result = fetch_pois_by_keyword(kw)
            if result and result.get("status") == "1":
                for poi in result.get("pois", []):
                    pid = poi.get("id")
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        all_data.append(extract_poi_fields(poi))
                        kw_count += 1
            time.sleep(0.05)
        print(f"   ✓ 关键词补充采集完成 (+{kw_count} 条)\n")

    print(f"{'='*60}")
    print(f"  采集完成！总计去重数据: {len(all_data)} 条")
    print(f"  结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    return all_data


def export_json(data, filepath):
    """导出为标准JSON格式"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[导出] JSON -> {filepath} ({len(data)} 条记录)")


def export_csv(data, filepath):
    """导出为CSV格式（可用Excel打开）"""
    if not data:
        return
    fieldnames = ["名称", "大类", "细类", "分类编码", "经度", "纬度", "地址", "电话", "评分", "营业时间"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            row = {k: item.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"[导出] CSV -> {filepath} ({len(data)} 条记录)")


def export_geojson(data, filepath):
    """导出为GeoJSON标准空间数据格式"""
    features = []
    for item in data:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item.get("经度", 0), item.get("纬度", 0)]
            },
            "properties": {
                "name": item.get("名称", ""),
                "category": item.get("大类", ""),
                "typecode": item.get("分类编码", ""),
                "address": item.get("地址", ""),
                "tel": item.get("电话", ""),
                "rating": item.get("评分", ""),
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "city": CITY,
            "citycode": CITYCODE,
            "source": "高德地图 Web服务 API",
            "count": len(features),
            "export_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"[导出] GeoJSON -> {filepath} ({len(features)} 个地理要素)")


def generate_statistics(data):
    """生成数据统计报告"""
    stats = {
        "采集时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "目标城市": CITY,
        "总POI数": len(data),
        "大类分布": {},
        "坐标范围": {
            "最小经度": min((d.get("经度", 180) for d in data), default=0),
            "最大经度": max((d.get("经度", -180) for d in data), default=0),
            "最小纬度": min((d.get("纬度", 90) for d in data), default=0),
            "最大纬度": max((d.get("纬度", -90) for d in data), default=0),
        },
        "有评分POI数": sum(1 for d in data if d.get("评分")),
        "有电话POI数": sum(1 for d in data if d.get("电话")),
    }

    for item in data:
        cat = item.get("大类", "未分类")
        stats["大类分布"][cat] = stats["大类分布"].get(cat, 0) + 1

    # 按数量排序
    stats["大类分布"] = dict(sorted(stats["大类分布"].items(), key=lambda x: -x[1]))

    with open(STATS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n[统计报告]")
    print(f"  总POI数量: {stats['总POI数']}")
    print(f"  大类数量: {len(stats['大类分布'])}")
    print(f"  坐标范围: ({stats['坐标范围']['最小经度']:.4f}, {stats['坐标范围']['最小纬度']:.4f}) -> ({stats['坐标范围']['最大经度']:.4f}, {stats['坐标范围']['最大纬度']:.4f})")
    print(f"  大类TOP5:")
    for i, (cat, count) in enumerate(list(stats['大类分布'].items())[:5]):
        print(f"    {i+1}. {cat}: {count} 条")
    print(f"  统计已保存至: {STATS_OUTPUT}")

    return stats


def main():
    quick_mode = "--quick" in sys.argv
    export_only = "--export" in sys.argv

    if export_only:
        # 仅从已有JSON导出CSV和GeoJSON
        if os.path.exists(JSON_OUTPUT):
            print(f"[读取] {JSON_OUTPUT}")
            with open(JSON_OUTPUT, "r", encoding="utf-8") as f:
                data = json.load(f)
            export_csv(data, CSV_OUTPUT)
            export_geojson(data, GEOJSON_OUTPUT)
            generate_statistics(data)
        else:
            print(f"[错误] 未找到JSON文件: {JSON_OUTPUT}")
            print("  请先运行 python export_poi_data.py 采集数据")
        return

    # 采集数据
    all_pois = fetch_all_pois(ALL_BIG_CATEGORIES, quick_mode=quick_mode)

    if not all_pois:
        print("[警告] 未采集到任何数据！请检查API密钥和网络连接。")
        return

    # 导出所有格式
    export_json(all_pois, JSON_OUTPUT)
    export_csv(all_pois, CSV_OUTPUT)
    export_geojson(all_pois, GEOJSON_OUTPUT)
    stats = generate_statistics(all_pois)

    print(f"\n{'='*60}")
    print(f"  全部导出完成！")
    print(f"  JSON:      {JSON_OUTPUT}")
    print(f"  CSV:       {CSV_OUTPUT}")
    print(f"  GeoJSON:   {GEOJSON_OUTPUT}")
    print(f"  统计报告:  {STATS_OUTPUT}")
    print(f"{'='*60}")

    return all_pois, stats


if __name__ == "__main__":
    main()
