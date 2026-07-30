"""
六十四卦全量数据生成脚本（权威表格验证版）
数据源：八宫六十四卦全图
"""
import json
from typing import List, Dict

# ========== 基础映射 ==========
GUA_CODE = {
    '111': '乾', '110': '兑', '101': '离', '100': '震',
    '011': '巽', '010': '坎', '001': '艮', '000': '坤'
}
GUA_WUXING = {
    '乾': '金', '兑': '金', '离': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土'
}
NAJIA_TABLE = {
    '乾': {'inner': '子', 'outer': '午', 'order': '顺'},
    '坎': {'inner': '寅', 'outer': '申', 'order': '顺'},
    '震': {'inner': '子', 'outer': '午', 'order': '顺'},
    '艮': {'inner': '辰', 'outer': '戌', 'order': '顺'},
    '坤': {'inner': '未', 'outer': '丑', 'order': '逆'},
    '巽': {'inner': '丑', 'outer': '未', 'order': '逆'},
    '离': {'inner': '卯', 'outer': '酉', 'order': '逆'},
    '兑': {'inner': '巳', 'outer': '亥', 'order': '逆'}
}
DIZHI_ORDER = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
DIZHI_WUXING = {
    '寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金',
    '亥':'水','子':'水','辰':'土','戌':'土','丑':'土','未':'土'
}
SHI_YING_MAP = {1:4, 2:5, 3:6, 4:1, 5:2, 6:3}

# ========== 权威八宫六十四卦列表 ==========
GONG_GUA_LIST = [
    # 1. 乾宫 (金)
    ('乾','乾',6,'乾为天'), ('乾','巽',1,'天风姤'), ('乾','艮',2,'天山遁'), ('乾','坤',3,'天地否'),
    ('巽','坤',4,'风地观'), ('艮','坤',5,'山地剥'), ('离','坤',4,'火地晋'), ('离','乾',3,'火天大有'),
    # 2. 兑宫 (金)
    ('兑','兑',6,'兑为泽'), ('兑','坎',1,'泽水困'), ('兑','坤',2,'泽地萃'), ('兑','艮',3,'泽山咸'),
    ('坎','艮',4,'水山蹇'), ('坤','艮',5,'地山谦'), ('震','艮',4,'雷山小过'), ('震','兑',3,'雷泽归妹'),
    # 3. 离宫 (火)
    ('离','离',6,'离为火'), ('离','艮',1,'火山旅'), ('离','巽',2,'火风鼎'), ('离','坎',3,'火水未济'),
    ('艮','坎',4,'山水蒙'), ('巽','坎',5,'风水涣'), ('乾','坎',4,'天水讼'), ('乾','离',3,'天火同人'),
    # 4. 震宫 (木)
    ('震','震',6,'震为雷'), ('震','坤',1,'雷地豫'), ('震','坎',2,'雷水解'), ('震','巽',3,'雷风恒'),
    ('坤','巽',4,'地风升'), ('坎','巽',5,'水风井'), ('兑','巽',4,'泽风大过'), ('兑','震',3,'泽雷随'),
    # 5. 巽宫 (木)
    ('巽','巽',6,'巽为风'), ('巽','乾',1,'风天小畜'), ('巽','离',2,'风火家人'), ('巽','震',3,'风雷益'),
    ('乾','震',4,'天雷无妄'), ('离','震',5,'火雷噬嗑'), ('艮','震',4,'山雷颐'), ('艮','巽',3,'山风蛊'),
    # 6. 坎宫 (水)
    ('坎','坎',6,'坎为水'), ('坎','兑',1,'水泽节'), ('坎','震',2,'水雷屯'), ('坎','离',3,'水火既济'),
    ('兑','离',4,'泽火革'), ('震','离',5,'雷火丰'), ('坤','离',4,'地火明夷'), ('坤','坎',3,'地水师'),
    # 7. 艮宫 (土)
    ('艮','艮',6,'艮为山'), ('艮','离',1,'山火贲'), ('艮','乾',2,'山天大畜'), ('艮','兑',3,'山泽损'),
    ('离','兑',4,'火泽睽'), ('乾','兑',5,'天泽履'), ('巽','兑',4,'风泽中孚'), ('巽','艮',3,'风山渐'),
    # 8. 坤宫 (土)
    ('坤','坤',6,'坤为地'), ('坤','震',1,'地雷复'), ('坤','兑',2,'地泽临'), ('坤','乾',3,'地天泰'),
    ('震','乾',4,'雷天大壮'), ('兑','乾',5,'泽天夬'), ('坎','乾',4,'水天需'), ('坎','坤',3,'水地比'),
]

def get_gong(idx: int) -> str:
    return GONG_GUA_LIST[(idx // 8) * 8][0]

def liuqin(yao_wuxing: str, gong_wuxing: str) -> str:
    if yao_wuxing == gong_wuxing: return '兄弟'
    if (gong_wuxing, yao_wuxing) in [('木','火'),('火','土'),('土','金'),('金','水'),('水','木')]: return '子孙'
    if (gong_wuxing, yao_wuxing) in [('木','土'),('火','金'),('土','水'),('金','木'),('水','火')]: return '妻财'
    if (yao_wuxing, gong_wuxing) in [('木','火'),('火','土'),('土','金'),('金','水'),('水','木')]: return '父母'
    return '官鬼'

def na_dizhi(shang: str, xia: str) -> List[str]:
    inner = NAJIA_TABLE[xia]
    outer = NAJIA_TABLE[shang]
    def get_three(start: str, order: str) -> List[str]:
        idx = DIZHI_ORDER.index(start)
        step = 2 if order == '顺' else -2
        return [DIZHI_ORDER[(idx + i * step) % 12] for i in range(3)]
    return get_three(inner['inner'], inner['order']) + get_three(outer['outer'], outer['order'])

def get_yinyang(shang: str, xia: str) -> List[int]:
    xia_code = next(k for k,v in GUA_CODE.items() if v == xia)
    shang_code = next(k for k,v in GUA_CODE.items() if v == shang)
    return [int(c) for c in xia_code + shang_code]

def generate_all() -> Dict:
    data = {}
    for idx, (shang, xia, shi, name) in enumerate(GONG_GUA_LIST):
        gong = get_gong(idx)
        gwx = GUA_WUXING[gong]
        ying = SHI_YING_MAP[shi]
        dizhi = na_dizhi(shang, xia)
        yinyang = get_yinyang(shang, xia)
        yao_list = []
        for i in range(6):
            ywx = DIZHI_WUXING[dizhi[i]]
            yao_list.append({
                "pos": i+1,
                "yin_yang": yinyang[i],
                "dizhi": dizhi[i],
                "liuqin": liuqin(ywx, gwx)
            })
        data[str(idx+1)] = {
            "name": name, "gong": gong, "shi": shi, "ying": ying,
            "yao_list": yao_list
        }
    return data

def validate_gua_list():
    print("正在验证八宫六十四卦列表...")
    errors = []
    seen_names = set()
    seen_yinyang = {}

    for idx, (shang, xia, shi, name) in enumerate(GONG_GUA_LIST):
        if name in seen_names:
            errors.append(f"第{idx+1}卦：卦名'{name}'重复")
        seen_names.add(name)

        if shi not in range(1,7):
            errors.append(f"第{idx+1}卦{name}：世爻{shi}无效")

        yinyang = get_yinyang(shang, xia)
        yinyang_str = ''.join(str(y) for y in yinyang)
        if yinyang_str in seen_yinyang:
            errors.append(f"第{idx+1}卦{name}：阴阳序列{yinyang_str}与第{seen_yinyang[yinyang_str]}卦重复")
        else:
            seen_yinyang[yinyang_str] = idx+1

        if shang == xia and shi != 6:
            errors.append(f"第{idx+1}卦{name}：纯卦世爻应为6，实际为{shi}")

        if idx < 8:
            print(f"  第{idx+1:2d}卦 {name:8}：阴阳序列 {yinyang_str}")

    if errors:
        print(f"\n发现 {len(errors)} 个错误：")
        for err in errors[:15]:
            print(f"  ❌ {err}")
        return False
    else:
        print(f"\n✅ 验证通过！共{len(GONG_GUA_LIST)}卦，阴阳序列全部唯一。")
        return True

if __name__ == '__main__':
    if not validate_gua_list():
        print("\n请修正列表后重试。")
        exit(1)

    result = generate_all()

    print("\n测试关键卦的阴阳序列：")
    test_names = ['山天大畜','雷水解','风雷益','山风蛊','山水蒙','泽天夬','水地比','雷山小过','雷泽归妹']
    for name in test_names:
        for k,v in result.items():
            if v['name'] == name:
                yinyang_str = ''.join(str(y['yin_yang']) for y in v['yao_list'])
                print(f"  {name}：{yinyang_str}")
                break

    with open('64gua_full.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n✅ 文件已生成：64gua_full.json")