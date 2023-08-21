import os
import re
import json

from util import *
from glob import glob
from category_101 import get_EXP
from utilCapacity import get_capacity

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/232_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/232_brand_list_2",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/232_taste_list",encoding="utf-8").readlines())]

absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.append("味之")

Spacial_productname = []

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    Taste_list_PLUS = Taste_list.copy()
    for taste in Taste_list:
        if "味" not in taste:
            Taste_list_PLUS.append(taste + "味")
    result = get_info_list_by_list_taste([[product_name, ], ], Taste_list_PLUS)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in ["口味", "新口味","风味","酸仔乳乳味","一杯宝草薯甘遇风味","果粒型风味","酸奶味风味"]:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                result.append(p_res[0])

    if len(result) == 0:
        return get_taste_normal(texts_list, Taste_list)
    else:
        # result = list(set(result))
        return ",".join(result)

def get_store(texts_list):
    '''
    规则：
    1.常温：包装上注明在“阴凉干燥处存放”、“常温”、或者是储藏温度为大于10度的
    2.冷藏：包装上注明“冷藏”或储藏温度在0-10度之间。“冷藏后口味更佳”、“开启后需冷藏”或者是“宜冷藏不宜冷冻”类似字样标注的产品都不属于冷藏。
    3.冷冻：包装上明确注明了“冷冻”或者是贮存条件在零下的。
    4.常温，冷藏：包装上同时出现了常温或冷藏字样
    5.常温，冷冻：包装上同时出现了常温或冷冻字样
    6.冷藏，冷冻：包装上同时出现了冷藏或冷冻字样
    :param texts_list:
    :return:
    '''
    result_changwen = []
    result_lengcang = []
    result_lengdong = []

    pattern = "阴凉处?|常温|室温|干燥处?|阴凉干燥|避免[日阳]光"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_changwen.append("常温")

    pattern = "冷藏"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile("口感|冷藏[后口饮条风喝至并锁最瓦井]|开?[启信封瓶风盖]后?|宜冷藏不宜冷冻|[口风]?味道?更佳?|低温高压|[需宜]密?封?冷藏").findall(text)) == 0:
                result_lengcang.append("冷藏")

    pattern = "冷冻|零下"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile("高温及冷冻|不?[宜宣]冷冻").findall(text)) == 0:
                result_lengdong.append("冷冻")

    if len(result_changwen) > 0 and len(result_lengcang) > 0:
        count = Counter(result_changwen).most_common(2)
        changwen = count[0][0]
        count = Counter(result_lengcang).most_common(2)
        lengcang = count[0][0]
        return changwen + "," + lengcang
    elif len(result_lengcang) > 0 and len(result_lengdong) > 0:
        count = Counter(result_lengcang).most_common(2)
        changwen = count[0][0]
        count = Counter(result_lengdong).most_common(2)
        lengdong = count[0][0]
        return changwen + "," + lengdong
    elif len(result_lengcang) > 0 and len(result_lengdong) > 0:
        count = Counter(result_lengcang).most_common(2)
        lengcang = count[0][0]
        count = Counter(result_lengdong).most_common(2)
        lengdong = count[0][0]
        return lengcang + "," + lengdong
    elif len(result_changwen) > 0:
        count = Counter(result_changwen).most_common(2)
        changwen = count[0][0]
        return changwen
    elif len(result_lengcang) > 0:
        count = Counter(result_lengcang).most_common(2)
        lengcang = count[0][0]
        return lengcang
    elif len(result_lengdong) > 0:
        count = Counter(result_lengdong).most_common(2)
        lengdong = count[0][0]
        return lengdong

    return "常温"

def get_inside(texts_list):
    '''
    含有物规则：包装上有果粒、果肉字样，或者是肉眼能看到饮品中含有果肉、果粒，或者是配料里有椰果字样
    '''
    pattern_1 = "果肉"
    pattern_2 = "果粒"
    pattern_3 = "椰果|椰肉"

    pattern = "果肉|果粒|椰果|椰肉"
    for texts in texts_list:
        for text in texts:
            if "成分" in text or "沉淀" in text or "其为" in text or "果肉成" in text or "果肉分层" in text:
                break
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if p_res[0] in pattern_1:
                    return "肉"
                elif p_res[0] in pattern_2:
                    return "粒"
                elif p_res[0] in pattern_3:
                    return "肉"

    return "不分"

def get_juicecontent(kvs_list,texts_list):
    '''
    果汁含量规则：
    1.按包装上注明的果汁含量如实抄录，没有果汁含量的给不分
    2.有关果汁含量的信息都要抄录，如果包装上没有果汁含量，配料表里某种水果的含量**%，也要抄录
    3.多种水果的含量需计算总和后抄录
    4.单一果肉、椰肉，椰果含量无需抄录，芦荟、奇亚籽含量无需抄录
    5.椰奶和椰汁水类产品包装上和配料表里的椰子水含量也需要抄果汁含量里
    '''
    pattern_absort = "奇?亚?籽|芦荟|蛋白|乳粉"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "含量" in k and "%" in kv[k] and "固" not in k and "质" not in k and "净含量" not in k and "肉" not in k and "蛋白" not in k:
                    separator = '%'
                    result_S = kv[k].split(separator, 1)[0] + separator
                    return result_S

    pattern = "[汁|计]总?含量"
    for texts in texts_list:
        for index,text in enumerate(texts):
            p_res_1 = get_info_by_pattern(text, pattern)
            total_len = len(texts)
            if len(p_res_1) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                for i in [-2,-1,1,2]:
                    if index + i >=0 and index + i <total_len:
                        p_res_tmp = re.compile("^\d+\.?\d*%$").findall(texts[index + i])
                        if len(p_res_tmp) > 0:
                            return texts[index + i]

    pattern = "含量\W?(\d+\.?\d*%)"
    for texts in texts_list:
        for text in texts :
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "固" not in text and "质" not in text and "肉" not in text and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    pattern = "[汁|计]总?(添加|含)量\w?\W?(\d+\.?\d*)%?"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                p_res = p_res[0]
                return p_res[1] + "%"

    pattern = "(\d+%)\w+[汁|计]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    pattern = "[汁|计](\d+%)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    pattern = "[汁|计](\d+%)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    pattern = "^100%$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    pattern = "[汁|计]\((\W?\d+%)\)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and len(re.compile(pattern_absort).findall(text)) == 0:
                return p_res[0]

    return "不分"

def get_suger(texts_list):
    '''
        1）不含蔗糖：包装上有“0蔗糖”、“不含蔗糖”、“无蔗糖”、“蔗糖为零”、“不添加蔗糖”字样；
        2）不含糖：包装上有“0糖”、“零糖”、“不含糖”、“糖分是0”、“无糖”、“Zero sugar”、“No sugar”、“Free of sugar”、“Sugar free”、“Unsweetened”字样；
        3）不添加糖：包装上有“0添加糖”、“0添加蔗糖”、“不或无(添)加食糖”、“不或无(添)加糖”、“不或无(添)加白(砂)糖”、“不或无(添)加蔗糖”、“无加糖”、“No Added Sugar”字样
        4）低糖：产品名称或包装上注明描述低糖的字样，或名称中有描述含糖量低的字样，如“少甜”、“微糖”、“超微糖”；
        5）木糖醇：产品名称或包装上注明描述木糖醇的字样；
        6）低聚糖：产品名称或包装上注明描述低聚糖的字样；
        7）不含蔗糖，木糖醇：包装上有“木糖醇”字样且不含蔗糖
        8）不含糖，木糖醇：包装上有“木糖醇”字样且不含糖
        9）不添加糖，木糖醇：包装上有“木糖醇”字样且不添加糖
        10）其他：包装上有“不添加糖精”、“冰糖”、“白砂糖”字样，或者是未注明
        :param texts_list:
        :return:
        '''
    result_zhesugar = []
    result_nosugar = []
    result_addsugar = []
    result_merge = []

    pattern = "0蔗糖|不含蔗糖|无蔗糖|蔗糖为零|零蔗糖|不添加蔗糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不含蔗糖"
                result_zhesugar.append("不含蔗糖")

    pattern = "[0O口零无]糖|不含糖|Zerosugar|Nosugar|Freeofsugar|ugarfree|Unsweetened|OSUGAR|ZEROSUGAR"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不含糖"
                result_nosugar.append("不含糖")

    pattern = "0添加糖|0添加蔗糖|[不无]添?加食糖|[不无]添?加糖|[不无]添?加白砂?糖|[不无]添?加蔗糖|无加糖|NoAddedSugar"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "不添加糖"
                result_addsugar.append("不添加糖")

    pattern = "木糖醇"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                # return "木糖醇"
                result_merge.append("木糖醇")

    '''
    规则【根据规则表顺序进行判断，但组合内容的判断优先级最高：
    1.优先处理组合内容：“不含蔗糖，木糖醇”、“不含糖，木糖醇”、“不添加糖，木糖醇”---------将不含蔗糖、不含糖、不添加糖的结果放在不同的list表中，分别与木糖醇搭配，如两者均有结果-返回
    2.其次处理单个内容：“不含蔗糖”、“不含糖”、“不添加糖”--------分别判断不同的list表中是否有值，如有值-返回
    3.其他内容顺序依次往下
    '''
    # 【不含蔗糖,木糖醇】组合判断规则
    if len(result_zhesugar) > 0 and len(result_merge) > 0:
        count = Counter(result_zhesugar).most_common(2)
        zhesugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if zhesugar == "不含蔗糖" and mumerge == "木糖醇":
            return zhesugar + "," + mumerge

    # 【不含糖,木糖醇】组合判断规则
    if len(result_nosugar) > 0 and len(result_merge) > 0:
        count = Counter(result_nosugar).most_common(2)
        nosugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if nosugar == "不含糖" and mumerge == "木糖醇":
            return nosugar + "," + mumerge

    # 【不添加糖,木糖醇】组合判断规则
    if len(result_addsugar) > 0 and len(result_merge) > 0:
        count = Counter(result_addsugar).most_common(2)
        addsugar = count[0][0]
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        if addsugar == "不添加糖" and mumerge == "木糖醇":
            return addsugar + "," + mumerge

    # 【不含蔗糖】单个内容判断
    if len(result_zhesugar) > 0:
        count = Counter(result_zhesugar).most_common(2)
        zhesugar = count[0][0]
        return zhesugar

    # 【不含糖】单个内容判断
    if len(result_nosugar) > 0:
        count = Counter(result_nosugar).most_common(2)
        nosugar = count[0][0]
        return nosugar

    # 【不添加糖】单个内容判断
    if len(result_addsugar) > 0:
        count = Counter(result_addsugar).most_common(2)
        addsugar = count[0][0]
        return addsugar

    ##【木糖醇】单个内容判断
    if len(result_merge) > 0:
        count = Counter(result_merge).most_common(2)
        mumerge = count[0][0]
        return mumerge

    pattern = "少甜|微糖|超微糖|低糖|低[蔗燕]糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "低糖"

    pattern = "低聚糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "不添加糖精|冰糖|白砂糖"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "其他"

    return "其他"

def get_type(texts_list):
    '''
    子类型规则：
    1.NFC：包装上出现"NFC"、"非浓缩复原"、"非浓缩还原"、"100%冷压榨"、"100%鲜榨"字样或者是">=99%的椰子水"
    2.棒冰饮料：包装上出现“棒棒冰”、“碎碎冰”、“脆脆冰”，“**冰”字样
    3.椰奶：包装上注明“椰汁”、“椰子汁”、“椰奶”、“椰子奶”的产品归为“椰奶”，“椰子水”不是椰奶
    4.酸梅膏：包装上出现“酸梅膏”、“乌梅膏”字样
    5.秋梨膏：包装上出现“秋梨”字样
    6.酸梅汤：包装上出现“酸梅汤”、“乌梅汤”字样
    7.枣汁：包装上出现“枣”字样
    8.其他：包装上没有出现上面描述的
    :param texts_list:
    :return:
    '''
    pattern = "(NFC|非浓缩复原|非浓缩还原|100%冷压榨|100%鲜榨|99%椰子水)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "NFC"

    pattern = "棒棒冰|碎碎冰|脆脆冰"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "棒冰饮料"

    pattern = "(乌梅膏|酸梅膏)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "酸梅膏"

    pattern = "椰子?[汁奶]|椰子"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "椰奶"

    pattern = "秋梨|梨膏"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "秋梨膏"

    pattern = "(酸梅汤|乌梅汤)"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return "酸梅汤"

    pattern = "枣"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "地址" not in text and "产地" not in text:
                return "枣汁"

    return "不分"

def get_productName(kvs_list,texts_list):
    pattern_absort = "^[汁看贵服子吧指无印森其恒蔬种麦上市美严维锅中澳内含威风产Q态浓人兰饮]|[其当源十酒品]饮料|^[柔果桃橙原]汁$|^植携|内含|^泉州|^厦门|^芜州|^北京|^\d+[毫mM][升lL]"
    pattern0 = "(\w*富硒|\w*芒果汁|\w*椰艺星|\w*柿子汁|\w*柿子醋酸角汁|\w*椰子?汁|\w*枇杷秋梨膏|\w*双柚汁|\w*鲜橙多|\w*小天梨汤|\w*枇杷炖梨|\w*生椰拿铁|\w*高悦满满|\w*元江特产|\w*小吊梨汤|\w*冰糖雪梨|\w*冰杨梅|\w*锋芒毕露" \
               "|\w*海南萃榨|\w*野生蓝莓原汁|\w*NFC蓝莓|\w*芭乐甘露|\w*杨枝甘露|\w*黄棘甘露|\w*小青柠|\w*积极麦力|\w*喝果蔬|\w*沙棘复合饮|\w*沙棘原浆|\w*野山楂|\w*益生元小西梅|\w*玉米汁|\w*弗朗果|\w*慢煮山楂|\w*珍果珍肉|\w*厚椰乳|\w*山楂抱抱|\w*甄料|\w*一勺梨膏" \
               "|\w*津梨|\w*提一桶|\w*蓝莓|\w*生椰芒芒|\w*猕猴桃|\w*一杯宝|\w*野生沙棘|\w*酸仔乳|\w*一勺梨膏|\w*番石榴汁|\w*鲜椰汁|\w*柚子茶)$"
    pattern1 = "(\w{2,}[果桃橙]汁|\w{2,}汁?饮[料品]|\w{2,}酸梅汤|\w{2,}秋?梨膏|\w{2,}椰子?[汁奶乳]|\w{2,}酸梅膏|\w{2,}玉竹膏|\w{2,}刺梨饮|\w{2,}果蔬汁)$"
    pattern2 = "(\w{2,}[果桃橙]汁|\w{2,}汁?饮[料品]|\w*酸梅汤|\w*秋?梨膏|\w*椰子?[汁奶乳]|\w*酸梅膏|\w*玉竹膏|\w*刺梨饮|\w*果蔬汁)"
    pattern3 = "(\d+%\w*汁|\d+%\w*椰子水|\w*椰子水|\w+[汤汁膏]|\w*刺梨原[液汁]|\w*有机沙棘原浆|\w+梨饮)$"
    pattern4 = "(\d+%\w*汁|\d+%\w*椰子水|\w*刺梨原[液汁]|\w*有机沙棘原浆|\w+梨饮)"

    result_list = []
    result_list_front = []
    result_list_tmp = []

    pattern_tmp = "汁?饮[料品]|梨膏|椰子?汁"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern0)
            if len(p_res) > 0 and p_res[0] not in result_list and len(p_res[0]) > 1:
                result_list_front.append(p_res[0])

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern1)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、·，,]").findall(p_res[0])) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0] :
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern2)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、·，,]").findall(p_res[0])) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0]:
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in [ "名称","名"]):
                    if len(kv[k]) > 1 and len(re.compile("[委托单位|生产|企业|·]").findall(kv[k])) ==0 and len(re.compile(pattern_tmp).findall(kv[k])) > 0:
                        result_list.append(kv[k])
                    else:
                        result_list_tmp.append(kv[k])

        if len(result_list_tmp) == 0:
            product_name_tmp = "不分"
        else:
            count = Counter(result_list_tmp).most_common(2)
            product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern3)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、·，,]").findall(p_res[0])) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0]:
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern4)
            if len(p_res) > 0:
                if "的" not in p_res[0] and len(re.compile("[、·，,]").findall(p_res[0])) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list_front) > 0:
        count_front = Counter(result_list_front).most_common(2)
        if len(result_list) > 0:
            count = Counter(result_list).most_common(2)
            if count_front[0][0] in count[0][0]:
                return count[0][0]
            else:
                return count_front[0][0] + count[0][0]

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return product_name_tmp

def get_EXP(kvs_list,texts_list):
    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+[个個]?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        separator = '月'
                        result_S = kv[k].rsplit(separator, 1)[0] + separator
                        return result_S

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if kv[k] in ["12","18"]:
                        separator = '月'
                        result_S = kv[k].split(separator, 1)[0] + separator
                        return result_S + "个月"

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+[个個]月|零下\d+以?下?\d+[个個]月|-\d+以?下?\d+[个個]月"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)

    pattern = r'(\D+[12]年|^[12]年|\d+[个個]月|[一-十]+[个個]月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text:
                # return p_res[0]
                return ",".join(p_res)

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                date_list.append(re.sub("\D","",p_res[0]))

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y%m%d")
        except:
            date_list.remove(ddate)

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >=2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1:
            return str(d_res) + "天"

    pattern = r'20[12]\d年[01]?\d月[0123]?\d日?'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    date_list.append(p_res[0] + "日")
                else:
                    date_list.append(p_res[0])

    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y年%m月%d日")
        except:
            date_list.remove(ddate)

    date_list = list(set(date_list))
    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1:
            return str(d_res) + "天"

    return "不分"

def get_keyValue_232(kvs_list,keys):
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if "汤" not in kv[k] and "汁" not in kv[k] and "饮料" not in kv[k] and "膏" not in kv[k] and "饮品" not in kv[k] and "奶" not in kv[k]:
                        continue
                    if key in k and len(k) < 6:
                        return kv[k]
    return "不分"

def get_package_232_unit(base64strs):
    '''
        规则：塑料瓶、玻璃瓶、砖形包装、屋形包装(新鲜屋)、听装、袋装、铝瓶、杯装、纸罐、利乐钻、有盖利乐钻、其它
        :param base64strs:
        :return:
    '''
    url = url_classify + ':5040/yourget_opn_classify'

    task = MyThread(get_url_result, args=(base64strs, url,))
    task.start()
    # 获取执行结果
    result = task.get_result()
    result = package_filter(result,["编织袋","覆膜袋","无纺布袋"])
    result_no_box = package_filter(result,["纸盒"])
    if len(result_no_box) > 0:
        result = result_no_box

    if len(result) == 0:
        return "不分"
    if "玻璃底" in result:
        return "玻璃瓶"

    res = Counter(result).most_common(1)[0][0]
    if res == "塑料底" or ("塑料" not in res and "塑料底" in result):
        res = "塑料瓶"

    res = re.sub("保鲜盒|有盖保鲜盒","砖形包装",res)
    res = re.sub("保鲜屋|有盖保鲜屋", "屋形包装(新鲜屋）", res)
    res = re.sub("塑料袋|吸嘴袋装", "袋装", res)
    res = re.sub("塑料杯|纸杯", "杯装", res)
    res = re.sub("铁瓶", "铝瓶", res)
    res = re.sub("利乐峰", "利乐钻", res)

    if "有盖" in "".join(result) and res in ["利乐钻"]:
        res = "有盖" + res

    return res

def category_rule_232(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    taste = "不分"
    inside = "不分"
    juice_content = "不分"
    package = "不分"
    suger = "不分"
    store = "不分"
    type = "不分"
    EXP = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    #品牌
    brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted,Brand_list_1,[],["RIO","239","KIWI", "Vita","VITA","EIVI","天刺力",
                                                                      "citric","susa","QOO","肉多多","智力多","崂山","LIZE",
                                                                      "崂山啤酒"],[])

    brand_1 = re.sub("云萱朵人","云萱朵儿",brand_1)
    brand_1 = re.sub("果盟柱桂气","果盟桂气",brand_1)
    brand_1 = re.sub("田野説","田野说",brand_1)
    brand_1 = re.sub("台榔","台椰",brand_1)
    brand_1 = re.sub("赞思奇","费恩奇",brand_1)
    brand_1 = re.sub("楹荐儿","榅桲儿",brand_1)
    brand_1 = re.sub("睡济康","膳济康",brand_1)
    brand_1 = re.sub("姝美金燕","妹美金燕",brand_1)
    brand_1 = re.sub("拿马", "盒马", brand_1)
    brand_1 = re.sub("小天'", "小夭", brand_1)
    brand_1 = re.sub("崂山啤酒'", "崂山", brand_1)
    brand_1 = re.sub("JUMEX'", "果美乐JUMEX", brand_1,re.IGNORECASE)

    #商品全称
    #product_name = get_keyValue_232(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName(dataprocessed,datasorted)

    product_name = re.sub("椰艺星","椰芝星",product_name)
    product_name = re.sub("游猴桃", "猕猴桃", product_name)
    product_name = re.sub("混台", "混合", product_name)
    product_name = re.sub("批[把杷]", "枇杷", product_name)
    product_name = re.sub("秋架奢", "秋梨膏", product_name)
    product_name = re.sub("小天梨汤", "小夭梨汤", product_name)
    product_name = re.sub("沙[辣鞋]", "沙棘", product_name)
    product_name = re.sub("高悦满满", "喜悦满满", product_name)
    product_name = re.sub("粉榨纯梨", "枇杷炖梨", product_name)
    product_name = re.sub("黄棘", "黄桃", product_name)
    product_name = re.sub("橙计", "橙汁", product_name)
    product_name = re.sub("杜杷", "枇杷", product_name)
    product_name = re.sub("柳果", "椰果", product_name)

    # 重容量
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "ml|毫[升元开]|mL|L|[升元开]|ML", "袋盒桶罐瓶", 1)
    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    #子类型
    type = get_type([[product_name,],])
    if type == "不分" :
        type = get_type(datasorted)

    #储藏方式
    store = get_store(datasorted)
    #糖份
    suger = get_suger(datasorted)
    #保质期
    EXP = get_EXP(dataprocessed,datasorted)
    #含有物
    inside = get_inside(datasorted)
    #果汁含量
    juice_content = get_juicecontent(dataprocessed,datasorted)
    if juice_content not in ["不分","100","100%"]:
        juice_content = ">=" + juice_content
    #口味
    taste = get_taste(datasorted,product_name)

    # 包装
    # image_list = ["/data/zhangxuan/images/43-product-images" + i.split("ShangPin")[-1].replace("\\", "/") for i in
    #               base64strs]
    # package = get_package_232_unit(image_list)

    package = get_package_232_unit(base64strs)

    product_name = re.sub("柳汁", "椰汁", product_name)
    product_name = re.sub("复台", "复合", product_name)
    product_name = re.sub("巢汁", "果汁", product_name)
    product_name = re.sub("蒙莓", "草莓", product_name)
    product_name = re.sub("[^葡]萄", "葡萄", product_name)
    product_name = re.sub("娜子", "椰子", product_name)
    product_name = re.sub("榔于", "椰子", product_name)

    product_name = re.sub("^\w*品名称?", "", product_name)
    product_name = re.sub("^[吃用]", "", product_name)

    if type == "不分":type = "其他"
    if type == "其他" and "椰" in product_name:
        type = "椰奶"

    result_dict['info1'] = taste
    result_dict['info2'] = inside
    result_dict['info3'] = juice_content
    result_dict['info4'] = package
    result_dict['info5'] = suger
    result_dict['info6'] = store
    result_dict['info7'] = type
    result_dict['info8'] = EXP
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\232-果汁饮料'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3036633"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_232(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)