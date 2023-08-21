import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

Brand_list_1 = [i.strip() for i in set(open("Labels/323_brand_list",encoding="utf-8").readlines())]
Brand_list_3 = [i.strip() for i in set(open("Labels/323_brand_list_3",encoding="utf-8").readlines())]
Taste_list = [i.strip() for i in set(open("Labels/323_taste_list",encoding="utf-8").readlines())]

# 通常来看需要20个非通用属性
LIMIT_NUM = 20

class BigWordUtil():
    def __init__(self):
        self.pattern = "[\u4e00-\u9fa5]"

    def isNear(self,box,bbox):
        box_x_min = min([x[0] for x in box])

        box_x_max = max([x[0] for x in box])
        box_y_min = min([x[1] for x in box])
        box_y_max = max([x[1] for x in box])

        near_x = 1000
        near_y = 1000
        # for bbox in box_list:
        bbox_x_min = min([x[0] for x in bbox])
        bbox_x_max = max([x[0] for x in bbox])
        bbox_y_min = min([x[1] for x in bbox])
        bbox_y_max = max([x[1] for x in bbox])

        if box_x_max < bbox_x_min or box_x_min > bbox_x_max:
            tmp_x = min(abs(box_x_max - bbox_x_min), abs(box_x_min - bbox_x_max))
        else:
            tmp_x = 0
        if box_y_max < bbox_y_min or box_y_min > bbox_y_max:
            tmp_y = min(abs(box_y_max - bbox_y_min), abs(box_y_min - bbox_y_max))
        else:
            tmp_y = 0

        if tmp_x < near_x:
            near_x = tmp_x
        if tmp_y < near_y:
            near_y = tmp_y

        return near_x + near_y

    def process(self,dataoriginals):
        result_list = []
        max_size = 0
        min_size = 10000
        top_list = []
        bottom_list = []
        max_size_list = []
        min_size_list = []
        max_size_box_list = []
        for dataoriginal in dataoriginals:
            top = 10000
            bottom = 0
            tmp_max_size = 0
            tmp_min_size = 1000
            tmp_box = []
            for index, info in enumerate(dataoriginal):
                box = info["box"]
                size = min(abs(box[0][1] - box[3][1]), abs(box[0][0] - box[1][0]))
                dataoriginal[index]["size"] = size
                if size > max_size:
                    max_size = size
                if size < min_size:
                    min_size = size
                if box[0][1] < top:
                    top = box[0][1]
                if box[0][1] > bottom:
                    bottom = box[0][1]
                if size > tmp_max_size:
                    tmp_max_size = size
                    tmp_box = box
                if size < tmp_min_size:
                    tmp_min_size = size

            top_list.append(top)
            bottom_list.append(bottom)
            max_size_list.append(tmp_max_size)
            min_size_list.append(tmp_min_size)
            max_size_box_list.append(tmp_box)

        for index, dataoriginal in enumerate(dataoriginals):
            top = top_list[index]
            bottom = bottom_list[index]
            m_size = max_size_list[index]
            mm_size = min_size_list[index]
            m_box = max_size_box_list[index]

            height = bottom - top
            if float(m_size / mm_size) > 2.5 and m_size > 80:
                result_txt = []
                for info in dataoriginal:
                    if info["size"] > m_size * 0.7 or (info["size"] > m_size * 0.6 and self.isNear(info["box"], m_box) < info["size"] / 3):
                        if len(re.compile(self.pattern).findall(info["txt"])) == 0:
                            result_txt.append([info["txt"], info["box"][2][1] + info["box"][0][0]])
                result_txt = sorted(result_txt, key=lambda x: x[1])
                result_txt = [x[0] for x in result_txt]

                res_tmp = []
                if len(result_txt) > 0:
                    for i in result_txt:
                        flag = True
                        for j in result_txt:
                            if i == j:
                                continue
                            if i in j:
                                flag = False
                        if flag:
                            res_tmp.append(i)
                    result_list.append("".join(res_tmp))

        result_list = sorted(result_list, key=len)
        res = []
        if len(result_list) > 0:
            for index, i in enumerate(result_list):
                flag = True
                for j in result_list[index + 1:]:
                    if i in j:
                        flag = False
                if flag:
                    res.append(i)
        res = sorted(result_list, key=len, reverse=True)
        if len(res) == 0:
            return "不分"
        count = Counter(res).most_common(2)
        return count[0][0]

def get_info_list_by_list_323(texts_list,serchList):
    result = []
    for texts in texts_list:
        for text in texts:
            index = 0
            if len(re.compile("[前中后]调").findall(text)) > 0:
                break
            if len(re.compile("[,，、]").findall(text)) > 0:
                continue
            for t in serchList:
                if t in text:
                    if t not in result:
                        result.append(t)
                    index += 1
            if index > 1:
                result = mySorted(result,text)

    result_sorted = sorted(result,key=len)
    res = []
    if len(result_sorted) >0:
        for index,i in enumerate(result_sorted):
            flag = True
            for j in result_sorted[index+1:]:
                tmp_i = re.sub("味$","",i)
                if tmp_i in j:
                    flag = False
            if flag:
                res.append(i)
    res = sorted(res, key=result.index)
    return res

def get_taste(kvs_list,texts_list,product_name):
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "香调" in k and len(kv[k]) > 2 and len(kv[k]) < 8:
                    return kv[k]

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if "香型" in k and len(kv[k]) > 2 and len(kv[k]) < 8:
                    return kv[k]
    # res_list = []
    # t_1 = ""
    # t_2 = ""
    # t_3 = ""
    # for kvs in kvs_list:
    #     for kv in kvs:
    #         for k in kv.keys():
    #             if "前调" in k and len(kv[k]) > 2:
    #                 t_1 = kv[k]
    #             if "中调" in k and len(kv[k]) > 2:
    #                 t_2 = kv[k]
    #             if "后调" in k and len(kv[k]) > 2:
    #                 t_3 = kv[k]
    #
    # for t in [t_1,t_2,t_3]:
    #     if t != "":
    #         res_list.append(t)
    #
    # if len(res_list) > 0:
    #     return "，".join(res_list)

    if "花果香体" in product_name:
        return "花果香调"

    pattern = "[\u4e00-\u9fa5]{2,}香[调型]"
    pattern_abort = "其他"
    result = get_info_list_by_list([[product_name, ], ], Taste_list)
    if len(result) == 0:
        p_res = re.compile(pattern).findall(product_name)
        if len(p_res) > 0 and len(p_res[0]) > 3 and len(p_res[0]) < 7:
            result.append(p_res[0])
    if len(result) == 0:
        result = get_info_list_by_list_323(texts_list, Taste_list)

    if len(result) == 0:
        for texts in texts_list:
            for text in texts:
                p_res = re.compile(pattern).findall(text)
                if len(p_res) > 0 and len(re.compile(pattern_abort).findall(p_res[0])) == 0 and len(p_res[0]) > 3 and len(p_res[0]) < 7:
                    result.append(p_res[0])

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
    pattern_text = "[、，,]|香精香调"
    pattern_pres = "[的将]|^随身|没有|^\d|含义"
    result_list = []
    result_list_tmp = []
    pattern_1 = "(\w+香[体水]喷雾|[^留淡\W]{2,}[淡留]?香[水精]|\w{2,}香[膏氛]|\w+古龙水|\w*香水油)($|\()"
    pattern_2 = "(\w{2,}小样[板版]?|\w{2,}套[盒装]|\w{2,}试用装|\w{2,}喷雾)($|\()"
    pattern_3 = "\w+香[体水]喷雾|[\u4e00-\u9fa5]*香[水膏]|[\u4e00-\u9fa5]*古龙水"

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称","名"]) and len(re.compile("[\u4e00-\u9fa5]").findall(kv[k])) > 0:
                    if len(kv[k]) > 1 and len(kv[k]) > 1 and len(re.compile(pattern_pres).findall(kv[k])) == 0 and len(re.compile(pattern_text).findall(kv[k])) == 0:
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
            p_res = get_info_by_pattern(text, pattern_1)
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
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) == 0:
        return product_name_tmp
    count = Counter(result_list).most_common(2)
    if len(count) > 1 and count[0][0] in count[1][0]:
        return count[1][0]
    return count[0][0]

def cal_iou(boundary_1,boundary_2):
    insec_x1 = max(boundary_1[0],boundary_2[0])
    insec_x2 = min(boundary_1[1],boundary_2[1])

    # union = max(boundary_1[1],boundary_2[1]) - min(boundary_1[0],boundary_2[0])
    union = min(boundary_2[1] - boundary_2[0],boundary_1[1] - boundary_1[0])
    insec = insec_x2 - insec_x1 if insec_x2>insec_x1 else 0
    if union <= 0 :
        return 0
    return float(insec/union)

def get_English(dataoriginals):
    pattern = "([\w\s]+)[:】]+([a-zA-Z\s]+)$"
    for index, dataoriginal in enumerate(dataoriginals):
        for info in dataoriginal:
            txt = info["txt"]
            p_res = get_info_by_pattern(txt,pattern)
            if len(p_res) > 0:
                p_res = p_res[0]
                if "品名" in p_res[0] or "name" in p_res[0] or "英文名" in p_res[0] or p_res[0] in ["名称","名"]:
                    if len(p_res[1]) > 8:
                        return p_res[1]

    pattern = "[A-Z\s]*PARFUM$|[A-Z\s]*PERFUMES?$|[A-Z\s]*TOILETTE$|[A-Z\s]*FRAGRANCE$|[A-Z\s]*SPRAY$|[A-Z\s]*COLOGNE$"
    res_list = []
    for dataoriginal in dataoriginals:
        tmp_list = []
        for index, info in enumerate(dataoriginal):
            txt = info["txt"]
            if len(re.compile("[\u4e00-\u9fa5\)\(]").findall(txt)) > 0 or len(re.compile("-(PARFUM|PERFUMES?|TOILETTE|SPRAY)",re.IGNORECASE).findall(txt)) > 0:
                continue
            p_res = get_info_by_pattern(txt,pattern)
            if len(p_res) > 0:
                box = info["box"]
                tmp_str = txt
                y = (box[1][1] + box[2][1])/2
                h = box[2][1] - box[1][1]
                w = box[1][0] - box[0][0]
                x0 = box[0][0]
                x1 = box[1][0]
                if h > w:
                    continue

                for i in range(index):
                    box_tmp = dataoriginal[index - i - 1]["box"]
                    txt_tmp = dataoriginal[index - i - 1]["txt"]

                    if len(re.compile("[^a-zA-Z\.\']").findall(txt_tmp)) > 0:
                        continue
                    y_tmp = (box_tmp[1][1] + box_tmp[2][1]) / 2
                    h_tmp = box_tmp[2][1] - box_tmp[1][1]
                    w_tmp = box_tmp[1][0] - box_tmp[0][0]
                    x_tmp0 = box_tmp[0][0]
                    x_tmp1 = box_tmp[1][0]
                    if h_tmp > w_tmp:
                        continue
                    iou = cal_iou([x0,x1],[x_tmp0,x_tmp1])
                    if abs(y - y_tmp) < h / 5. and abs(x0 - x_tmp1) < h:
                        tmp_str = txt_tmp + " " + tmp_str
                    elif abs(y - y_tmp) < h * 2 and iou > 0.8:
                        tmp_str = txt_tmp + " " + tmp_str
                    elif abs(y - y_tmp) >= 2 * h and abs(y - y_tmp) < 4 * h:
                        tmp_list.append(tmp_str)
                        y = (box_tmp[1][1] + box_tmp[2][1]) / 2
                        h = box_tmp[2][1] - box_tmp[1][1]
                        x = box_tmp[0][0]
                        tmp_str = txt_tmp

                if len(tmp_list) == 0:
                    tmp_list.append(tmp_str)

        if len(tmp_list) > 0:
            name_len = min(2,len(tmp_list))
            name_list = sorted(tmp_list[:name_len],key=len,reverse=True)
            res_list.append(name_list[0])

    if len(res_list) > 0:
        count = Counter(res_list).most_common(1)
        return count[0][0]

    pattern = "([A-Z\s\.·]*EAU\s?DE\s?)(PARFUM|PERFUMES?|TOILETTE|SPRAY)([A-Z\s\.·]*)"
    for dataoriginal in dataoriginals:
        for index, info in enumerate(dataoriginal):
            txt = info["txt"]
            p_res = re.compile(pattern,re.IGNORECASE).findall(txt)
            if len(p_res) >0:
                p_res = p_res[0]
                if len(p_res[-1]) < 4:
                    p_res = p_res[:-1]
                res_list.append(" ".join(p_res))

    if len(res_list) > 0:
        count = Counter(res_list).most_common(1)
        return count[0][0]

    pattern = "([A-Z\s\.·]*EAU[\s#]?DE[\s#]?)(PARFUM|PERFUMES?|TOILETTE)([A-Z\s\.·]*)($|#)"
    for dataoriginal in dataoriginals:
        txt_list = [i["txt"] for i in dataoriginal]
        txt = "#".join(txt_list)
        p_res = re.compile(pattern,re.IGNORECASE).findall(txt)
        if len(p_res) >0:
            p_res = p_res[0]
            res_txt = " ".join(p_res[:-1])
            res_txt = re.sub("[\s#]+"," ",res_txt)
            res_list.append(res_txt)

    if len(res_list) > 0:
        count = Counter(res_list).most_common(1)
        return count[0][0]

    return "不分"

def get_type(texts_list):
    key_list = ["淡香精","淡香水","香体膏","浓香水","浓香氛","古龙"]
    res_list = []
    for texts in texts_list:
        if "EDP" in texts:
            res_list.append("EDP")
        elif "EDT" in texts:
            res_list.append("EDT")
        for text in texts:
            if len(re.compile("eaudeparfum",re.IGNORECASE).findall(text)) > 0:
                res_list.append("EDP")
            if len(re.compile("eaudetoilette",re.IGNORECASE).findall(text)) > 0:
                res_list.append("EDT")
            if len(re.compile("cologne",re.IGNORECASE).findall(text)) > 0:
                res_list.append("古龙")
            for k in key_list:
                if k in text:
                    res_list.append(k)

    if len(res_list) > 0:
        count = Counter(res_list).most_common(2)
        res = count[0][0]
        if res in ["淡香精","EDP","浓香水","浓香氛"]:
            return "淡香精EDP"
        elif res in ["淡香水","EDT"]:
            return "淡香水EDT"
        elif res in ["香体膏"]:
            return "香体膏"
        elif res in ["古龙"]:
            return "古龙COLOGNE"
    else:
        return "香水"


def get_people(texts_list):
    for texts in texts_list:
        for text in texts:
            if "男士" in text or "先生" in text:
                return "男士"

    return "不分"

def get_package_323(base64strs):
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
        return "玻璃瓶（泵装）"

    result_material = package_filter(result_material,["纸"])
    if len(result_material) == 0:
        material = "纸"
    else:
        material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if "玻璃底" in result_material:
        material = "玻璃"
    elif "塑料底" in result_material:
        material = "塑料"


    if "瓶" in "".join(result_shape):
        shape = "瓶"
        if "滴管瓶" in result_shape or "喷雾瓶" in result_shape:
            shape = "瓶（泵装）"
        if material not in ["玻璃","塑料"]:
            if "塑料" in result_material and "玻璃" not in result_material:
                material = "塑料"
            else:
                material = "玻璃"

        return material + shape
    elif "玻璃" in "".join(result_material):
        return "玻璃瓶（泵装）"
    elif shape in ["格","托盘","盒"]:
        shape = "盒"

    if material == "金属":
        material = "铁"

    return material + shape

def category_rule_323(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    type_1 = "不分"
    state = "不分"
    English = "不分"
    taste = "不分"
    package = "不分"
    people = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], Brand_list_3, [])
    if brand_1 == "不分":
        brand_tmp = get_brand(dataprocessed)

    brand_1 = re.sub("BVLCARI", "BVLGARI", brand_1)
    brand_1 = re.sub("narcisorodriguez", "纳西索narciso rodriguez", brand_1 ,re.IGNORECASE)

    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "g|克|ml|毫[升开元]|mL|ML", "瓶包袋罐", 1, min_num=1)

    capcity_2 = re.sub("毫[开元]", "毫升", capcity_2)
    capcity_1 = re.sub("毫[开元]", "毫升", capcity_1)

    product_name = get_productName_voting(dataprocessed, datasorted)

    product_name = re.sub("沙本", "沙龙", product_name)
    product_name = re.sub("家引", "索引", product_name)
    product_name = re.sub("广野", "旷野", product_name)
    product_name = re.sub("書膏", "香膏", product_name)

    product_name = re.sub("\([^\)]+$", "", product_name)
    product_name = re.sub("[0-9A-Za-z]+$", "", product_name)
    product_name = re.sub("^\w?\W+", "", product_name)
    product_name = re.sub("[^\)\w]$", "", product_name)

    if "克" in capcity_1 or "g" in capcity_1 or "G" in capcity_1:
        state = "固体"
    else:
        state = "液体"

    type_1 = get_type(datasorted)
    taste = get_taste(dataprocessed, datasorted, product_name)
    people = get_people([[product_name, ], ])
    English = get_English(dataoriginal)
    if len(re.compile("^EAU", re.IGNORECASE).findall(English)) > 0:
        English = re.sub("EAU\s?DE\s?", "EAU DE ", English, re.IGNORECASE)
    else:
        English = re.sub("\s?EAU\s?DE\s?", " EAU DE ", English, re.IGNORECASE)

    taste = re.sub("^\W", "", taste)

    package = get_package_323(base64strs)
    zz_flag = get_info_list_by_list(datasorted, ["走珠", "滚珠"])
    if len(zz_flag) > 0:
        if "塑料" in package:
            package = "塑料瓶（走珠）"
        else:
            package = "玻璃瓶（走珠）"

    result_dict['info1'] = type_1
    result_dict['info2'] = state
    result_dict['info3'] = English
    result_dict['info4'] = taste
    result_dict['info5'] = package
    result_dict['info6'] = people
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
    pass