import os
import re

from util import *
from glob import glob

# from category_101 import get_EXP,get_EXP_store
from utilCapacity import get_capacity
LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/121_brand_list_1",encoding="utf-8").readlines())]
Brand_replace_dict_1 = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/121_brand_list_3", encoding="utf-8").readlines())}

Taste_list = [i.strip() for i in set(open("Labels/121_taste_list",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/121_type_list",encoding="utf-8").readlines())]

type_pleasure_list=['台湾风味']
absor_taste = [i  for i in Brand_list_1 if "味" in i]
absor_taste.extend(["味之","以味"])

def get_store(texts_list):
    key_1 = ["常温","室温","阴凉"]
    key_2 = ["冷藏","零下"]

    for texts in texts_list:
        for text in texts:
            for k in key_1:
                if k in text:
                    return "常温"

    for texts in texts_list:
        for text in texts:
            for k in key_2:
                if k in text:
                    return "冷藏"

    return "常温"

def get_Nutrition(kvs_list):
    protein = "不分"
    fat = "不分"
    protein_key = "营养成分表-蛋白质-NVR"
    # protein_key1 = "营养成分表-蛋白质"
    fat_key = "营养成分表-脂肪"
    p_1 = re.compile(r'(\d+\.?\d*)\s?(G|g|克)')
    p_2 = re.compile(r'(\d+\.?\d*)\s?\%')
    for kvs in kvs_list:
        for kv in kvs:
            if protein_key in kv.keys():
                p_res_2 = p_2.findall(kv[protein_key])
                if len(p_res_2) > 0:
                    protein = p_res_2[0]
            if fat_key in kv.keys():
                p_res_1 = p_1.findall(kv[fat_key])
                if len(p_res_1) > 0:
                    if float(p_res_1[0][0]) > 100:
                        fat = str(float(p_res_1[0][0]) / 10.0)
                    else:
                        fat = p_res_1[0][0]
    return protein,fat

def get_taste_bak(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list_taste([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0:
            Flag = True
            for i in Taste_Abort_List:
                if i in p_res[0]:
                    Flag = False
                    break
            if Flag:
                result.append(p_res[0])

    if len(result) == 0:
        pattern = "(\w+味)\)?$"
        for texts in texts_list:
            for text in texts:
                Flag = False
                for absort in absor_taste:
                    if absort in text:
                        Flag = True
                        break
                if Flag:
                    continue
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    tmp_taste = p_res[-1]
                    if len(re.compile("\d").findall(tmp_taste)) > 0:
                        continue

                    tmp_flag = True
                    for i in Taste_Abort_List:
                        if i in tmp_taste:
                            tmp_flag = False
                    if tmp_taste == "新口味": tmp_flag = False
                    if tmp_flag:
                        if len(tmp_taste) == 2:
                            if tmp_taste == "原味" or tmp_taste == "橙味" or tmp_taste == "橘味" or tmp_taste == "奶味" or tmp_taste == "咸味":
                                return tmp_taste
                        elif len(tmp_taste) < 7:
                            return tmp_taste

    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list, Taste_list)
    if len(result) > 0:
        result = list(set(result))
        return "".join(result)
    return "不分"

def get_taste(texts_list,product_name):
    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and p_res[0] not in Taste_Abort_List_pres:
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
        return "".join(result)

def get_type(texts_list,productname):
    result_type = "不分"
    result_type_1 = "不分"
    result_type_2 = "不分"
    #类型2-西式:其中西式是根据全称判断，含西式的都给西式
    pattern_xisi = '西式|培根'
    #类型2-休闲
    pattern_xiuxian='台湾风味\w*|小香肠\w*|肉花肠|椰果烤\w*|香脆\w*|脆\w*肠|甜玉米\w*肠|菠萝热狗肠|好劲道|香辣\w*肠|韩式烧烤|脆骨\w*肠|岭南风味|原味\w*肠|' \
                    '\w*肠.*\w*原味.*|台式\w*肠|劲火腿|烤鱼\w*香肠|蒜你酷|小酷仔|Q奇幻|甭逗|川透力|马克波罗火腿|DHA金品肉肠|肉枣\w*肠|时尚|烤肠\w*|\w*扣肉|\w*儿童肠|牛筋\w*肠'

    result_type = get_info_item_by_list(texts_list,Type_list)
    if result_type == "不分" or result_type=="香肠":
        pattern = "\w+肠"
        p_res = get_info_by_pattern(productname, pattern)
        if len(p_res) > 0:
            if "台式"  in productname or "台湾"  in productname:
                result_type = "台湾香肠"
            else:
                result_type = "香肠"

    if result_type == "不分":
        pattern = "(烤)\w*(肉)"
        p_res = get_info_by_pattern(productname, pattern)
        if len(p_res) > 0:
            result_type = "烤肉"

    if result_type in ["不分","酱肉","卤肉"]:
        pattern = "卤|酱"
        p_res = get_info_by_pattern(productname, pattern)
        if len(p_res) > 0:
            result_type = "酱肉/卤肉"

    if result_type == "不分":
        pattern = "凤爪|鸡爪|鸡翅|泡翅|扣肉|鸡尖|翅尖"
        p_res = get_info_by_pattern(productname, pattern)
        if len(p_res) > 0:
            result_type = "休闲肉制品"

    if result_type == "不分":
        pattern = "(鸡|鸭|鱼|猪|牛|羊|鹅|蹄|鹌鹑|肘子|三文治|肉)"
        p_res = get_info_by_pattern(productname, pattern)
        if len(p_res) > 0:
            result_type = "中式肉其它"

    if result_type in ["火腿肠","火腿","方腿","圆腿","切片火腿","金华火腿"]:
        if '切片' in productname and result_type=="火腿":
            result_type ="切片火腿"
        elif result_type == "火腿":
            result_type="中式肠"
        result_type_1 = "火腿"
    elif result_type in ["台湾香肠","香肠","红肠","烤肠","热狗肠"]:
        if  result_type=='香肠' or result_type=="红肠":
            result_type='中式肠'
        result_type_1 = "香肠"
    elif result_type in ["烤肉","熏肉","酱肉/卤肉","中式肉其它","休闲肉制品","午餐肉","丸","里脊"]:
        if result_type=='丸':
            result_type='肉丸'
        result_type_1 = "中式肉"
    elif result_type in ["培根"]:
        result_type_1 = "培根"
    else:
        result_type_1 = "不分"

    p_res = get_info_by_pattern(productname, pattern_xisi)
    if len(p_res) > 0:
        result_type_2='西式'
    p_res = get_info_by_pattern(productname, pattern_xiuxian)
    if len(p_res) > 0:
        result_type_2 = '休闲'
    else:
        result_type_2 = '不分'
    return result_type,result_type_1,result_type_2

def get_series(texts_list):
    result = get_info_item_by_list(texts_list, ["跑酷兄弟","清伊坊","脆脆王","泡面拍档"])
    return result

def get_productName_voting(texts_list,kvs_list):
    abort_list=['g']
    result_list = []
    pattern_1 = "(\w+火腿|\w+[烤香粉鱼肉红枣蒜腊]肠|\w+[肉鱼]罐头|\w+猪蹄|\w+牛腱子|\w+鸡丝|\w+鸡翅|\w+凤爪|\w+[香卷][肘时]|\w+大鹅|\w+肘子肉|\w+猪[时肘]|\w+牛腱|\w+肉筋肠|\w+牛肉|\w+肉肘|\w*羊肝|\w*三文治|" \
                "\w+猪骨|\w+翅尖|\w+猪口条|\w+泡翅|\w+猪头肉|\w+水鸭|\w+扒鸡|\w+牛筋肠|\w+鸡胸丸|\w+椒鸡|\w+鸭脖|\w+板鸭|\w+烤肉肚|\w+辣鸡尖|\w+松花肠|" \
                "\w+鹿肉|\w+醉鸡|\w+鸡腿|\w*午餐肉|\w+培根|\w+宫格|\w+肉枣|\w*酱排骨|\w*鳕鱼棒|\w+蒸肉)($|\()"
    pattern_2 = "(\w+火腿肠|\w+火腿|\w*里脊王|\w+宏腿|w+[烤香粉鱼肉红枣蒜]肠|\w+猪蹄|\w+猪耳|\w+牛腱子|\w+鸡丝|\w+香蹄|\w+肉罐头|\w+肘子肉|\w+肘子|\w+凤爪|" \
                "\w*牛蹄筋|\w*辣子鸡|\w+鸭肉排|\w+风爪|\w+[牛羊]蝎子|\w+胸肉丸|\w+盐焗鸡|\w+鸡肉条|\w+鸭翅|\w+肉丸|\w+板鸭|" \
                "\w*蛋卷|\w*酱鸭|\w+[香卷][时肘]|\w+午餐肉|\w+水鸭|\w*烧鸡|\w*式卤肉|\w+鱼肠|\w+鸡爪|\w+酱牛肉|\w+鸭肉排|\w+松花肠|\w+培根|\w+礼[包盒]$)"
    pattern_3 = "(\w+肉|\w+肠|\w+鸡|\w+鸭)$"

    pattern_res = "[的是用不]|^就?吃|每1"
    result_list_pre=[]
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(kv[k]) > 1 :
                        kv[k] = re.sub("^\w?\W+", "", kv[k])
                        if len(re.compile("[肠鸡鸭猪肘蹄牛羊翅腿肉鱼]").findall(kv[k])) > 0:
                            result_list.append(kv[k])

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_res).findall(p_res[0])) == 0 and len(p_res[0])>=2:
                    flag = True
                    for it in result_list:
                        if p_res[0] in it and p_res[0]!=it :
                            flag = False
                            break
                    if flag :
                        flag = True
                        for it in abort_list:
                            if it in p_res[0]:
                                flag = False
                                break
                        if flag:
                            result_list.append(p_res[0])
                    continue

    if len(result_list) > 0:
        result_list_pre.sort(key=len, reverse=True)
        for it in result_list_pre:
            for itt in result_list:
                if it in itt:
                    return it
        result_list.sort(key=len,reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0:
                    flag = True
                    for it in abort_list:
                        if it in p_res[0]:
                            flag = False
                            break
                    if flag:
                        result_list.append(p_res[0])

    if len(result_list) > 0:
        result_list_pre.sort(key=len, reverse=True)
        for it in result_list_pre:
            for itt in result_list:
                if it in itt:
                    return it
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_res).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])
                    continue

    if len(result_list) == 0:
        return "不分"
    result_list.sort(key=len, reverse=True)
    count = Counter(result_list).most_common(2)
    return count[0][0]

def get_ingredients(kvs_list,texts_list):

    result = []
    abandon_list = ['鱼肉粉','鸡肉粉','猪油','猪酒','鸡精','鸡蛋','鱼露','柠楼酸鸡','虾蜡','牛可','羊料','食鱼','鸡菜','鳕鱼味','鱼类','鸡配','鱼烤']
    # serchList = ["猪","牛肉","羊肉","鸡肉","鸭肉","驴肉","鱼肉","虾"]
    serchList = ["肘子肉","猪蹄","猪腿","猪肉","牛肉","羊肉",'鸡爪',"鸡胸肉","白条鸡","鸡肉","鸭肉","驴肉","鱼肉",'鹅肉','猪头肉']

    pattern1 = r'\w+料表|配科表|配料'
    p = re.compile(pattern1)
    res = []
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    kvalue = kv[k]
                    for t in serchList:
                        if t in kvalue and t not in res :
                            res.append(t)

    if len(res) == 0:
        res = get_info_list_by_list(texts_list,serchList)
    for r in res:
        if ("猪" in r or "肘子" in r):
            if "猪肉" not in result:
                result.append("猪肉")
        elif "鸡" in r:
            if "鸡肉" not in result:
                result.append("鸡肉")
        else:
            if r not in result:
                result.append(r)
    result = sorted(result,key=serchList.index)
    return result

def get_EXP_new(dataprocessed,datasorted):
    store = get_EXP_store(dataprocessed, datasorted)
    store = re.sub("^-", "零下", store)
    store = re.sub("[度C]?以下", "度以下", store)
    store = re.sub("带温", "常温", store)
    store = re.sub("C", "度", store)
    store = re.sub("下", "度", store)
    store = re.sub("不分", "", store)
    EXP = get_EXP(dataprocessed, datasorted)
    EXP = EXP.replace('(真空包装不漏气)', '').replace('(常温)', '').replace('(充气包装不破损)', '').replace('(发货前为冷冻保存)', '').replace(
        '注意', '').replace('下', ''). \
        replace('一', '').replace('常福', '常温').replace('订', '').replace('常遇', '常温').replace('C', '度').replace('冷意', '冷藏'). \
        replace('贮存', '').replace('保存', '').replace('食用方法别开朋合', '').replace('受委托单位莱', '').replace('阴凉', '常温')
    pattern = "^\d+个月$"
    p_res = get_info_by_pattern(EXP, pattern)
    if len(p_res) > 0:
        EXP = '常温' + EXP
    else:
        pattern = "^\d+天$"
        p_res = get_info_by_pattern(EXP, pattern)
        if len(p_res) > 0:
            # EXP = '常温' + EXP
            if len(store) > 0:
                store = store.replace('-', '至')
                store = store.replace('阴凉', '常温').replace('冷藏', '常温')
                EXP = store + EXP
            else:
                EXP = '常温' + EXP
        else:
            pattern = '\d+-\d+天'
            ls1 = get_info_by_pattern(EXP, pattern)
            if len(ls1) > 0:
                t = ''
                for it in ls1:
                    d1 = it.replace('天', '').split('-')[0]
                    d2 = it.replace('天', '').split('-')[1]
                    if len(d2) == 3:
                        txt = d1 + '至' + d2[0:1] + '度' + d2[1:] + '天'
                        t += txt + '，'
                    elif len(d2) >= 4:
                        txt = d1 + '至' + d2[0:2] + '度' + d2[2:] + '天'
                        t += txt + '，'
                t = t[0:-1]
                if len(ls1) == 1:
                    # 1-475天，常温30天
                    if str(EXP).index(ls1[0]) == 0:
                        EXP = t + EXP.replace(ls1[0], '')
                    else:
                        EXP = EXP.replace(ls1[0], '') + t
                elif len(ls1) == 2:
                    # 0-10180天10-2560天常温45天
                    EXP = t + EXP.split(ls1[1])[1]
            else:
                if '常温' not in EXP:
                    EXP = '常温' + EXP

    return EXP

# 属于哪种肉类
def get_category(ingredients,product_name):
    # key_list = ["猪肉", "牛肉","羊肉","鸡肉", "鸭肉","鱼肉"]
    key_list = ["猪","牛","羊","鸡","鸭","鱼"]
    other = ""
    tmp_ingredients = "不分"
    if '凤爪' in product_name or '翅尖' in product_name:
        tmp_ingredients = '鸡肉'
    elif '肘子' in product_name or '扣肉' in product_name or '里脊' in product_name or (
            '五花' in product_name and '肉' in product_name):
        tmp_ingredients = '猪肉'

    #从名称全称中判断
    category_index=-1
    if tmp_ingredients == '不分':
        for k in key_list:
            if k in product_name:
                tmp_ingredients = k+ '肉'
                break

    #从配料中判断
    if tmp_ingredients == "不分":
        for k in key_list:
            if tmp_ingredients == "不分":
                for t in ingredients:
                    if k in t or k + '肉' in t:
                        tmp_ingredients = k + '肉'
                        break

    if tmp_ingredients!='不分':
        tmp_ingredients=tmp_ingredients+'类'

    if tmp_ingredients=='不分':
        otherList = ["驴", "鹿", "兔", "虾", "蟹", "马", "牡蛎", "扇贝", "鹅"]
        for k in otherList:
            if k in product_name and "玉兔" not in product_name:
                other = '其它'
                flag = True
                for t in ingredients:
                    if k in t:
                        flag = False
                        break
                if flag:
                    ingredients.append(k)
        if other == "":
            for k in otherList:
                if k + "肉" in ingredients:
                    other = '其它'

        if len(other)>0:
            tmp_ingredients=other

    return tmp_ingredients,"，".join(ingredients)

def get_EXP(kvs_list,texts_list):

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return kv[k]

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if kv[k] in ["12","18"]:
                        return kv[k] + "个月"

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+个月|零下\d+以?下?\d+个月|-\d+以?下?\d+个月"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)


    pattern = r'(\D+[12]年|^[12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text and '挂果期' not in text:
                return p_res[0]

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
            if d_res>800:
                return '不分'
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
            if d_res>800:
                return '不分'
            return str(d_res) + "天"

    return "不分"

def get_EXP_store(kvs_list,texts_list):
    pattern = r'(储存|贮藏|贮存|保存|贴存|购存|存|冷藏)'
    p = re.compile(pattern)
    degree=''
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                p_res1 = p.findall(kv[k])
                if len(p_res) > 0 or len(p_res1):
                    p_res = re.compile("-?\d{1,2}[-至]\d{1,2}[度C]?以?下?|零下\d+以?下?").findall(kv[k])
                    if len(p_res) > 0:
                        if len(re.compile("\d$").findall(p_res[0])) > 0:
                            if '-' in p_res[0]:
                                ts = p_res[0].split('-')
                                if int(ts[1])>30:
                                    return ts[0]+'-'+ts[1][0]+'度'
                                else:
                                    return p_res[0] + "度"
                            else:
                                return p_res[0] + "度"
                        else:
                            return p_res[0]

    pattern = r'(-?\d{1,2}[-至]\d{1,2}[度C]|零下\d{1,2}[度C]?以?下?|-18以?下?|0-4|2-8)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and '日期' not in text:
                if len(re.compile("\d$").findall(p_res[0])) > 0 :
                    return p_res[0] + "度"
                else:
                    return p_res[0]


    pattern = r'(冷藏|冷冻)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if '常温' in text:
                    return '常温'
                else:
                    return p_res[0]

    pattern = r'常温|阴凉|带温|冷藏'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def category_rule_121(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    product_replace_dict_1 = {'子子':'千子','肉零肠':'肉枣肠','熏煮肠':'蒜香肠','需板鸭':'酱板鸭','韩鸭':'鹌鹑','旦县':'旦旦','挂子':'辣子','熏煮肠':'蒜香肠','盆水':'盐水','易':'肠',
                              '肉膜头':'肉罐头','风爪':'凤爪','甜香':'酱香','干餐肉':'午餐肉','里背':'里脊','王米':'玉米','幕香':'蒜香'}
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    store = "不分"
    protein = "不分"
    fat = "不分"
    type = "不分"
    type_1 = "不分"
    type_2 = "不分"
    taste = "不分"
    ingredients = "不分"
    series = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    dataprocessed.sort(key= lambda c : (len(c),len(str(c))), reverse=True)
    datasorted.sort(key=len)
    brand_1 = get_keyValue(dataprocessed, ["品牌名称"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["光顺","a1","FKO","ZEK","亮泽","华宝","NBR","京味","全家","美好","品先","百年诚信","keep","柴火香","好感觉","无穷","葵花"],[])

    for key in Brand_replace_dict_1.keys():
        brand_1 = re.sub(key, Brand_replace_dict_1.get(key), brand_1)

    if product_name == "不分":
        product_name = get_productName_voting(datasorted,dataprocessed)
    for key in product_replace_dict_1.keys():
        product_name = re.sub(key, product_replace_dict_1.get(key), product_name)
    product_name = re.sub("低蛋", "低脂", product_name)
    product_name = re.sub("猪时", "猪肘", product_name)
    product_name = re.sub("香时", "香肘", product_name)
    product_name = re.sub("鹅鸭", "鹌鹑", product_name)
    product_name = re.sub("香接", "香辣", product_name)
    product_name = re.sub("特国", "德国", product_name)
    product_name = re.sub("黑板", "黑椒", product_name)
    product_name = re.sub("叫化鸡", "叫花鸡", product_name)
    product_name = re.sub("雪鱼", "鳕鱼", product_name)
    product_name = re.sub("黄蒜", "皇蒜", product_name)
    product_name = re.sub("黑素", "黑猪", product_name)
    product_name = re.sub("涤海", "深海", product_name)
    product_name = re.sub("特肠", "蒜肠", product_name)
    product_name = re.sub("牛您", "牛肉", product_name)
    product_name = re.sub("紫蒸", "紫燕", product_name)
    product_name = re.sub("玉香", "五香", product_name)
    product_name = re.sub("·", "", product_name)

    product_name = re.sub("品名", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if EXP == "不分":
        EXP = get_EXP_new(dataprocessed,datasorted)


    if capcity_1=='不分':
        capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐支", 0)
    capcity_1 = capcity_1.replace('元', '克')
    if type == "不分":
        # type, type_1, type_2 = get_type(datasorted, product_name)
        list1=[[product_name]]
        type,type_1,type_2 = get_type(list1,product_name)


    if protein == "不分":
        protein,fat = get_Nutrition(dataprocessed)
        fat=fat.replace('.0','')
        protein=protein.replace('.0','')
        if protein!='不分':
            try:
                fv = float(protein)
                if fv>100:
                    protein=str(int(fv/10))
            except Exception as ex:
                pass

    if ingredients == "不分":
        ingredients = get_ingredients(dataprocessed,datasorted)

    if series == "不分":
        series = get_series(datasorted)
    store1='不分'
    if store1 == "不分":
        store1 = get_store(datasorted)

    if taste == "不分":
        taste = get_taste(datasorted,product_name)
        taste =taste.replace('减蛋','咸蛋')
    if "西式" in product_name:
        type_2 = "西式"

    type = type if type != "红肠" else "香肠"

    tmp_ingredients,ingredients=get_category(ingredients, product_name)
    if len(ingredients)==0:
        ingredients='不分'

    # 存储方式
    result_dict['info1'] = store1
    # 类型
    result_dict['info2'] = type
    # 哪种肉类
    result_dict['info3'] = tmp_ingredients
    # 口味
    result_dict['info4'] = taste
    # 保质期
    result_dict['info5'] = EXP
    # 配料
    result_dict['info6'] = ingredients
    # 子类
    result_dict['info7'] = type_1
    # 系列
    result_dict['info8'] = series
    # 类型2
    result_dict['info9'] = type_2
    # 蛋白质含量
    result_dict['info10'] = protein
    # 脂肪含量
    result_dict['info11'] = fat
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    for k in result_dict.keys():
        result_dict[k] = re.sub("[,，：:]", "", result_dict[k])
    result_dict['info6'] = ingredients
    real_use_num = 11
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\121-香肠火腿肠培根中式肉'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        product = "3042238"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_121(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)