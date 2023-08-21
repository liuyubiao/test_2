import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/507_brand_list",encoding="utf-8").readlines())]
Inside_list_1 = [i.strip() for i in set(open("Labels/507_inside_list_1",encoding="utf-8").readlines())]
Inside_list_2 = [i.strip() for i in set(open("Labels/507_inside_list_2",encoding="utf-8").readlines())]
Type_list_1 = [i.strip() for i in set(open("Labels/507_type_list_1",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/507_taste_list",encoding="utf-8").readlines())]
XiangXin_list = [i.strip() for i in set(open("Labels/507_xiangxin_list",encoding="utf-8").readlines())]
# 通常来看需要20个非通用属性
LIMIT_NUM = 20

def get_taste(texts_list,product_name):
    if "烧烤" in product_name:
        return "烧烤"

    pattern = "(\w+味)"
    result = get_info_list_by_list([[product_name,],], Taste_list)
    if len(result) > 2:
        result = result[:1]
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 :
            for p_r in p_res:
                if p_r not in ["口味","新口味"]:
                    Flag = True
                    for i in Taste_Abort_List:
                        if i in p_r:
                            Flag = False
                            break
                    if Flag:
                        result.append(p_r)

    if len(result) == 0:
        result = get_info_list_by_list_taste(texts_list,Taste_list)
        if len(result) > 0:
            result = result[:1]

    if len(result) == 0:
        return "不分"
    else:
        return "".join(result)

def get_brand(kvs_list):
    pattern = r'(生产商)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    return kv[k].replace("有限公司","").replace("有限责任公司","").replace("实业","")
    return "不分"

def get_productName_voting(kvs_list,texts_list):
    pattern_text = "[、，,。]|配料"
    pattern_pres = "[的市县免入再用将]|^\w?[固国囧圆][态体]|^椒粉$|^多用途|^[淋做浇]|[好原]料|水化|非发酵|^非?即食|属于|^本品|[使适]用|^\w?态复?合?调味料|真材实料|^味料|^\w调料|配比"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w{2,}调味?料|\w+[底撒卤酱炖煮]料|\w+辣酱|\w+蘸碟|\w+腌制料|\w+酸菜鱼|\w+烤鱼|\w+炒鸡酱|\w+卤肉包|\w+卤水|\w+烧烤料|\w+酸汤|\w*香辣小面|" \
                "\w+椒盐|\w+芝麻盐|\w+五香粉|\w*豉汁王|\w*肉味王|\w+拌面汁|\w+蚝油粉|\w{2,}蘸[水料]|\w*[炖卤]+[牛羊]*肉料|\w*涮肚料|\w+[炖酱]排骨|" \
                "\w+味鲜[宝寶]|\w+叻沙酱|\w*炖[\w\(\)]*[鱼鸡鸭牛羊][\w\(\)]*料|\w+板面|\w+辣椒面)($|\()"
    pattern_2 = "(\w*卤肉料?包|\w*烧烤料|\w*椒盐|\w*五香粉|\w*蚝油粉|\w*排骨王|\w*炖[鸡鱼鸭]料|\w*[炖酱]排骨|\w*芝麻盐|\w*叻沙酱|"
    for i in Type_list_1:
        pattern_2 += "\w*" + i + "|"
    pattern_2 = pattern_2[:-1] + ")($|\()"
    pattern_3 = pattern_1.replace("($|\()","")
    pattern_4 = "(\w+[料酱粉])($|\()"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]):
                    if len(re.compile("[,，、]").findall(kv[k])) > 0:
                        continue
                    if len(kv[k]) > 1 and len(re.compile("[料酱粉卤汁菜烧锅肉骨面汤鲜]").findall(kv[k])) > 0:
                        result_list.append(kv[k])
                    elif len(kv[k]) > 1:
                        result_list_tmp.append(kv[k])

    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["复合调味料"]:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0] and float(count[1][1]) > 1:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0 and p_res[0] not in ["复合调味料"]:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        if len(count) > 1 and count[0][0] in count[1][0]:
            return count[1][0]
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                p_res = p_res[0]
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        product_name = count[1][0]
    else:
        product_name = count[0][0]

    if len(re.compile("^[调卤汤]味?料$|^复合调味料$|^混合调味料$").findall(product_name)) > 0:
        product_name = productNameFormat(texts_list,product_name)

    return product_name

def productNameFormat(texts_list,product_name):
    res_name_list = []
    for texts in texts_list:
        if product_name in texts:
            pre_str = ""
            i_num = 0
            for index,text in enumerate(texts):
                if index > 10 or i_num > 1:
                    break
                if text == product_name:
                    res_name_list.append(pre_str + product_name)
                if len(re.compile("[,，、配料]|含量|^[a-zA-Z\W\d]+$").findall(text)) == 0:
                    pre_str = text
                else:
                    i_num += 1

    if len(res_name_list) > 0:
        count = Counter(res_name_list).most_common(2)
        return count[0][0]
    return product_name

def productName_bak(texts_list,product_name):
    if product_name in ["黑胡椒","白胡椒","花椒","辣椒",]:
        for texts in texts_list:
            if "粉" in texts or "椒粉" in texts :
                return product_name + "粉"
    elif product_name in ["孜然"]:
        for texts in texts_list:
            if "粉" in texts or "然粉" in texts :
                return product_name + "粉"

    return product_name

def get_brand_list_test(texts_list):
    brand_1_list = []
    brand_2 = []
    for texts in texts_list:
        for text in texts:
            for b1 in Brand_list_1:
                if b1.upper() in text or b1.title() in text:
                    brand_1_list.append(b1)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    if len(brand_1_list) == 0:
        brand_1 = "不分"
    else:
        brand_1_list.sort(key=len,reverse=True)
        count = Counter(brand_1_list).most_common(6)
        brand_1 = ",".join([i[0] for i in count])
    return brand_1,brand_2

def get_inside_1(texts_list):
    result = []
    for texts in texts_list:
        for i,text in enumerate(texts):
            index = 0
            if "入" in text or "或" in text or "适量" in text or "将" in text or "即可" in text or "加" in text:
                if i < 5:
                    continue
                else:
                    break
            for t in Inside_list_1:
                if len(t) > 1:
                    if t in text:
                        if t not in result:
                            result.append(t)
                        index += 1
                else:
                    if t in re.split("[^%\-0-9a-zA-Z\u4e00-\u9fa5\\/]", text):
                        if t not in result:
                            result.append(t)
                        index += 1
            if index > 1:
                result = mySorted(result, text)
    result_sorted = sorted(result, key=len)
    res = []
    if len(result_sorted) > 0:
        for index, i in enumerate(result_sorted):
            flag = True
            for j in result_sorted[index + 1:]:
                if i in j:
                    flag = False
            if flag:
                res.append(i)
    res = sorted(res, key=result.index)

    if len(res) > 0:
        if "食盐" in res and "食用盐" in res:
            res.remove("食盐")
        if "碘盐" in res and "食用盐" in res:
            res.remove("碘盐")
        return "，".join(res)
    return "否"

def get_inside_2(texts_list):
    res = get_info_list_by_list(texts_list,Inside_list_2)
    if len(res) > 0:
        return "，".join(res)
    return "不分"

def get_type(product_name,texts_list,inside_1):
    if len(re.compile("[鸡鸭鱼菜]|香锅").findall(product_name)) > 0:
        if len(re.compile("炖\(?卤\)?").findall(product_name)) == 0:
            return "菜谱式调料"

    pattern = "五香\w*粉|咖喱|椒盐"
    if len(re.compile(pattern).findall(product_name)) > 0:
        return "混合香辛料"

    pattern = ""
    for i in Type_list_1:
        pattern += i + "|"
    pattern = pattern[:-1]
    if len(re.compile(pattern).findall(product_name)) > 0 and "盐" not in inside_1:
        return "单一香辛料"

    xiangxin_res = get_info_list_by_list(texts_list, XiangXin_list)
    if len(xiangxin_res) > 1 and "盐" not in inside_1 and "糖" not in  inside_1 and "精" not in inside_1:
        return "混合香辛料"

    if "料" in product_name or "酱" in product_name:
        return "菜谱式调料"

    res = get_info_list_by_list(texts_list,["酸菜包","萝卜包","主料包"])
    if len(res) > 0:
        return "菜包式调料"

    return "菜谱式调料"

def get_state(texts_list,product_name):
    if "粉" in product_name or "面" in product_name or "撒料" in product_name or "蘸料" in product_name or "蘸碟" in product_name or "烧烤" in product_name:
        return "粉状"

    if "酱" in product_name or "汁" in product_name or "卤水" in product_name:
        return "液体"

    res = []
    for texts in texts_list:
        for text in texts:
            if "入" in text or "或" in text :
                break
            for t in ["饮用水","植物油","酱油"]:
                if t in text:
                    if t not in res:
                        res.append(t)
    if len(res) > 0:
        return "液体"

    res = get_info_list_by_list(texts_list, ["撒料", "蘸料", "蘸碟", "烧烤"])
    if len(res) > 0:
        return "粉状"

    return "整粒"

def get_package_507(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if material == "金属":
        return "金属盒(罐)"

    if "塑料底" in result_material or "塑料" in material:
        material = "塑料"
    elif "玻璃底" in result_material:
        material = "玻璃"

    if "袋" in shape:
        shape = "袋"
    elif "瓶" in shape or "桶" in shape:
        shape = "瓶"
    elif "罐" in shape:
        shape = "罐"

    if shape in ["格", "盒", "罐", "杯", "筒", "托盘", "碗"]:
        if material == "塑料":
            shape = "盒（罐）"
        else:
            shape = "盒"

    return material + shape

def category_rule_507(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    inside_1 = "不分"
    inside_2 = "不分"
    type = "不分"
    taste = "不分"
    state = "不分"
    package = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["人民","杨安镇","奥尔","A1","DAK","美味佳","味地道",
                                                                         "国民","阿香","太和","惠民","天味","乌江","双香",
                                                                         "别忘了","Ole","DECHANG","张家","延味","佳味浓"], [])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("汁?正好口福","汴正好口福",brand_1)
    brand_1 = re.sub("桂陵路牌?", "真喜焕", brand_1)
    brand_1 = re.sub("个上农", "禾上农", brand_1)
    brand_1 = re.sub("郑州大裕调味食品", "王老胖", brand_1)
    brand_1 = re.sub("FUCHS","福克斯",brand_1,re.IGNORECASE)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐瓶", 0)

    # datasorted = TextFormat(datasorted)
    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("铝醋", "糖醋", product_name)
    product_name = re.sub("改然", "孜然", product_name)
    product_name = re.sub("迷选香", "迷迭香", product_name)
    product_name = re.sub("千辣椒", "干辣椒", product_name)
    product_name = re.sub("腩[料科]", "撒料", product_name)
    product_name = re.sub("香烧", "香辣", product_name)
    product_name = re.sub("[随髓]水", "蘸水", product_name)
    product_name = re.sub("[随髓]料", "蘸料", product_name)
    product_name = re.sub("[亮]料", "烹料", product_name)
    product_name = re.sub("住料", "佐料", product_name)
    product_name = re.sub("生美", "生姜", product_name)
    product_name = re.sub("板子", "栀子", product_name)
    product_name = re.sub("麻[椒叔]", "麻椒", product_name)
    product_name = re.sub("六肉", "大肉", product_name)

    product_name = re.sub("^品?名?称", "", product_name)
    product_name = re.sub("^\w?[^\w\(\)]+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if product_name in ["黑胡椒", "白胡椒", "花椒", "辣椒", "孜然"]:
        product_name = productName_bak(datasorted, product_name)
    # if product_name in ["复合调味料","混合调味料"]:
    #     product_name = productNameFormat(datasorted,product_name)

    inside_1 = get_inside_1(datasorted)
    inside_1 = re.sub("碘盐","食用盐",inside_1)
    inside_2 = get_inside_2(datasorted)
    type = get_type(product_name,datasorted,inside_1)
    if type == "单一香辛料":
        inside_2 = "不分"
    taste = get_taste(datasorted, product_name)
    state = get_state(datasorted,product_name)
    package = get_package_507(base64strs)

    result_dict['info1'] = inside_1
    result_dict['info2'] = inside_2
    result_dict['info3'] = type
    result_dict['info4'] = taste
    result_dict['info5'] = state
    result_dict['info6'] = package
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict['brand_tmp'] = brand_tmp

    real_use_num = 6
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = []
    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_2\149-速冻食品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3039104"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_507(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)