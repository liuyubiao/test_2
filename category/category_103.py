import os
import re

from util import *
from glob import glob
# from category_101 import get_EXP

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''

Brand_list_1 = [i.strip() for i in set(open("Labels/103_brand_list_1",encoding="utf-8").readlines())]
Brand_replace_dict_1 = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/103_brand_list_3", encoding="utf-8").readlines())}
productname_absort = ["配料","配科","料","吃"]
sub_class_list = ['鸡','鸭','鹅','鹌鹑','鸽子','鹑','鹤鹑']

# 通常来看需要20个非通用属性
LIMIT_NUM = 20


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

def get_productName(texts_list):
    pattern_pres = "[了的请或]|见\w*包装|含有"
    tmp_list = []
    high_priority_list = []
    pattern = "\w*[鸡鸭鹅鸟鹑]蛋$|\w*谷物蛋|\w*虫草蛋|\w*生蛋$|\w*洁净蛋$|\w*[粮鸡码窝家硒餐食藻地谷养鲜子量香心制虫柴]蛋"
    # pattern = "\w*[鸡鸭鹅鸟鹑]蛋$|\w*谷物蛋|\w*虫草蛋|\w*蛋"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                for i in productname_absort:
                    if i in p_res[0] and "了" not in p_res[0] and "的" not in p_res[0]:
                        p_res[0] = p_res[0].replace(i,"")
                if len(re.compile(pattern_pres).findall(p_res[0])) == 0 and len(re.compile("每\d+").findall(p_res[0])) == 0:
                    if len(p_res[0])>1 and p_res[0]!='对鸡蛋' and p_res[0]!='鸡蛋' and p_res[0]!='鲜蛋' and '配料' not in text:
                        tmp_list.append(p_res[0])
                        # if '品名' in text :
                        #     high_priority_list.append(p_res[0])

    if len(tmp_list) == 0:
        pattern = "\w*[鸡鸭鹅鸟鹑]蛋|\w*谷物蛋|\w*虫草蛋|\w*生蛋"
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if len(p_res) > 0:
                    for i in productname_absort:
                        if i in p_res[0]:
                            p_res[0] = p_res[0].replace(i, "")
                    if len(re.compile(pattern_pres).findall(p_res[0])) == 0:
                        if len(p_res[0]) > 1:
                            tmp_list.append(p_res[0])

    if len(tmp_list) > 0:
        tmp_list.sort(key=len, reverse=True)
        count = Counter(tmp_list).most_common(2)
        if len(count)==2:
            for p in tmp_list:
                if p in high_priority_list:
                    return p
            # 如果次数一样，再比较长度
            if count[1][1]==count[0][1] and len(count[1][0])>len(count[0][0]):
                return count[1][0]
            else:
                return count[0][0]
        else:
            return count[0][0]
        # print(product_name_tmp)

    return "不分"


def get_Capacity(kvs_list,texts_list):
    pattern = r'(净含量?|净重|[Nn][Ee][Tt][Ww]|规格)'
    p = re.compile(pattern)
    kvg = "不分"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if kvg == "不分":
                    p_res = p.findall(k)
                    if len(p_res) > 0:
                        pattern_2 = r'\d+\.?\d*[千Kk]?[Gg克]'
                        p_2 = re.compile(pattern_2)
                        p_res_2 = p_2.findall(kv[k])
                        if len(p_res_2) > 0:
                            kvg = p_res_2[0]
    # p_1 = re.compile(r'(^|[^0-9a-zA-Z])(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)([^0-9a-zA-Z]|$)')
    p_1 = re.compile(r'(|[^0-9a-zA-Z])(\d+\.?\d*)\s?(Kg|G|g|kg|KG|克|千克)([^0-9a-zA-Z]|)')
    p_2 = re.compile(r'(\d+)[\s]?([个双]$|枚)')
    tmp_list_1 = []
    tmp_list_2 = []
    text_str_all=''
    for texts in texts_list:
        text_str_all += "".join(texts)
    for texts in texts_list:
        tmp_1 = []
        tmp_2 = []

        for text in texts:
            p_res_1 = p_1.findall(text)
            # print(1)
            p_res_2 = p_2.findall(text)
            if len(p_res_1) > 0:
                if float(p_res_1[0][1]) > 10000:
                    continue
                if "克(g)" in text or "克(9)" in text or "每" in text or "J/100" in text or "g/100" in text or "营养" in text:
                    continue
                if p_res_1[0][1][0] == "0":
                    continue
                temp = p_res_1[0][1] + p_res_1[0][2]
                temp=temp.lower()
                if 'kg' in temp:
                    temp=str(float(temp.replace('kg',''))*1000).replace('.0','')+'克'
                elif 'k' in temp:
                    temp = str(float(temp.replace('k', '')) * 1000).replace('.0', '') + '克'
                elif '千克' in temp:
                    temp = str(float(temp.replace('千克', '')) * 1000).replace('.0', '') + '克'
                #鸡蛋小于20克，排除，错误数据
                if float(temp.replace('克','').replace('g','').replace('G',''))<20 and '鸡蛋' in text_str_all:
                    continue
                temp=temp.replace('克', '').replace('g', '').replace('G', '')
                temp = float(temp)
                if temp >= 100000:
                    temp = int(temp / 100)
                elif temp>=10000:
                    temp = int(temp / 10)

                # if temp>5000 or temp<20:
                #     continue

                temp=str(temp).replace('.0','') + '克'
                tmp_1.append(temp)
                # tmp_1.append(p_res_1[0][1] + p_res_1[0][2])
            if len(p_res_2) > 0 and "每" not in text:
                if int(p_res_2[0][0]) > 3:
                    tmp_2.append(str(int(p_res_2[0][0]))+"枚")
        if len(tmp_1)>0:
            tmp_list_1.extend(tmp_1)
        if len(tmp_2)>0:
            tmp_list_2.extend(tmp_2)
    unit_result = []
    capacity_result = []
    if len(tmp_list_2) >0:
        unit_result.append("枚")
        capacity_result.append(tmp_list_2[0])
    else:
        pattern_0 = "^[个枚]$"
        num = "不分"
        for texts in texts_list:
            for index, text in enumerate(texts):
                if num == "不分":
                    p_res_0 = get_info_by_pattern(text, pattern_0)
                    total_len = len(texts)
                    if len(p_res_0) > 0:
                        for i in [-2, -1, 1, 2]:
                            if index + i >= 0 and index + i < total_len:
                                p_res_tmp = re.compile("^\d{1,2}$").findall(texts[index + i])
                                if len(p_res_tmp) > 0:
                                    num = p_res_tmp[0]
                                    break

        if num != "不分":
            unit_result.append("枚")
            capacity_result.append(p_res_tmp[0] + "枚")

    if kvg != "不分":
        kvg = kvg.lower()
        if 'kg' in kvg:
            kvg = str(float(kvg.replace('kg', '')) * 1000).replace('.0', '') + '克'
        elif 'k' in kvg:
            kvg = str(float(kvg.replace('k', '')) * 1000).replace('.0', '') + '克'
        elif '千克' in kvg:
            kvg = str(float(kvg.replace('千克', '')) * 1000).replace('.0', '') + '克'

        unit_result.append("克")
        temp = int(kvg.replace('克','').replace('g','').replace('G',''))
        if temp>=100000:
            kvg=str(int(temp/100))+'克'
        elif temp >= 10000:
            kvg = str(int(temp / 10)) + '克'

        capacity_result.append(kvg)
    elif len(tmp_list_1) > 0:
        count = Counter(tmp_list_1).most_common(2)
        unit_result.append("克")
        capacity_result.append(count[0][0])
    unit = "，".join(unit_result)
    unit = unit if unit != "" else "不分"
    if len(capacity_result) == 2:
        capacity = "/".join(capacity_result)
    elif len(capacity_result) == 1:
        capacity = capacity_result[0]
    else:
        capacity = "不分"
    return capacity,unit

def get_EXP_bak(EXP):
    EXP = EXP.replace('下', '').replace('(建议冷藏)', '').replace('保存', '').replace('正常赔存条件', '').replace('/忙存条',
                                                                                                     '').replace('饨温',
                                                                                                                 ''). \
        replace('C', '度').replace('c', '度').replace('冷藏', '').replace('冷载', '').replace('购存', '').replace('微温',
                                                                                                          '常温').replace(
        '贮藏', '').replace('保质', '').replace('含临', ''). \
        replace(',', '，').replace('以', '度').replace('k', '度').replace('(宠议)', '')
    if str(EXP).endswith('/'):
        EXP = EXP[0:len(EXP) - 1]

    pattern = '\d+-\d+天'
    ls1 = get_info_by_pattern(EXP, pattern)
    if len(ls1) > 0:
        t = ''
        for it in ls1:
            d1 = it.replace('天', '').split('-')[0]
            d2 = it.replace('天', '').split('-')[1]
            if len(d2) == 3:
                txt = d1 + '-' + d2[0:1] + '度' + d2[1:] + '天'
                t += txt + '，'
            elif len(d2) >= 4:
                txt = d1 + '-' + d2[0:2] + '度' + d2[2:] + '天'
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
    ##################################
    pattern = '\d{4,6}天'
    # 常温30天,01045天
    # 常温30天,09180天
    ls1 = get_info_by_pattern(EXP, pattern)
    if len(ls1) > 0:
        t = ''
        for it in ls1:
            it = it.replace('天', '')
            if it[1] == '1' or it[1] == '2':
                txt = it[0] + '-' + it[1:3] + '度' + it[3:] + '天'
            else:
                txt = it[0] + '-' + it[1:2] + '度' + it[2:] + '天'
            t += txt + '，'

        t = t[0:-1]
        if len(ls1) == 1:
            # 常温30天,01045天
            if str(EXP).index(ls1[0]) == 0:
                EXP = t + EXP.replace(ls1[0], '')
            else:
                EXP = EXP.replace(ls1[0], '') + t

    ###################################
    pattern = '\d{2,3}月\d+天'
    # 49月35天,10-3月50天
    ls1 = get_info_by_pattern(EXP, pattern)
    if len(ls1) > 0:
        t = ''
        for it in ls1:
            it1 = it.split('月')[0]
            if int(it1) > 12:
                txt = it1[0] + '-' + it1[1] + '月' + it.split('月')[1]
                t += txt + '，'
        t = t[0:-1]
        if len(ls1) == 1:
            # 49月35天,10-3月50天
            if str(EXP).index(ls1[0]) == 0:
                EXP = t + EXP.replace(ls1[0], '')
            else:
                EXP = EXP.replace(ls1[0], '') + t

    #############################################
    if '常温' not in EXP:
        pattern = '^\d+天$'
        p_res = get_info_by_pattern(EXP, pattern)
        if len(p_res) > 0:
            EXP = '常温' + EXP
        else:
            pattern = '^\d+天'
            p_res = get_info_by_pattern(EXP, pattern)
            if len(p_res) > 0:
                EXP = '常温' + EXP
    return EXP

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
        print(1)
        for kv in kvs:
            print(1)
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
#提取子类
def get_subclass(product_name,texts_list):
    '''
    提取子类
    提取依据：103蛋类定义文档及人为标注Excel测试数据
    提取思路：103蛋类定义文档只明确定义 新增子类细分：鸡/鸭/鹅/鹌鹑/鸽子/其它，按全称或配料表判定
    :param product_name:商品名称全称
    :param texts_list:文本列表
    :return:
    '''
    result = '不分'
    for sub_class in sub_class_list:
        if sub_class in product_name:
            result = sub_class
            break
    for texts in texts_list:
        for text in texts:
            for sub_class in sub_class_list:
                if sub_class in text:
                    result = sub_class
                    break
        if result!='不分':
            break
    result = result.replace('鹤鹑','鹌鹑')
    if result == '鹑':
        result ='鹌鹑'

    if result == "不分":
        result = "鸡"

    return result

def get_package_103(base64strs):
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

    if shape == "网兜":
        return "网兜"
    if shape == "篮":
        return "篮（有把手）"
    if shape == "筐":
        return "筐（无把手）"

    if material == "纸":
        material = "纸"
    else:
        material = "塑料"

    if shape in ["盒", "托盘"] and material != "塑料":
        shape = "盒"
    else:
        shape = "格"

    return material + shape

def category_rule_103(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    product_replace_dict_1={'谷帆':'谷物','鹤鹑':'鹌鹑','样青龄菜':'样青龄菜','鲜鸭':'鲜鹌','地鸡蛋':'物鸡蛋','行物':'谷物','西硒':'富硒',
                            '多味':'乡味','元小老':'元小吉','造青为':'德青源','积食':'粮食','样胃':'梓青','鲜蛋多':'鲜疍多'}
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    unit = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # brand_1 = get_keyValue(dataprocessed, ["商标"])
    brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["谷物鲜","正大","国文","农家","菜篮子"], [])
    # if brand_1 == "不分":
    #     brand_1 = get_brand(dataprocessed)

    for key in Brand_replace_dict_1.keys():
        brand_1 = re.sub(key, Brand_replace_dict_1.get(key), brand_1)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName(datasorted)

    product_name = re.sub("媽鹑","鹌鹑",product_name)
    product_name = re.sub("^鹑", "鹌鹑", product_name)
    product_name = re.sub("羊鸡蛋", "鲜鸡蛋", product_name)

    pattern = '\d+枚'
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res)>0:
        ts = product_name.split(p_res[0])
        for t in ts:
            if len(t)>0:
                product_name = t
    for key in product_replace_dict_1.keys():
        product_name = re.sub(key, product_replace_dict_1.get(key), product_name)
    for key in Brand_replace_dict_1.keys():
        product_name = re.sub(key, Brand_replace_dict_1.get(key), product_name)

    subclass = get_subclass(product_name, datasorted)

    if EXP == "不分":
        EXP = get_EXP(dataprocessed,datasorted)
        get_EXP_bak(EXP)
    if capcity_1 == "不分":
        capcity_1,unit = get_Capacity(dataprocessed,datasorted)

    package = get_package_103(base64strs)

    result_dict['info1'] = package
    result_dict['info2'] = EXP
    result_dict['info3'] = unit
    result_dict['info4'] = subclass
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    real_use_num = 4
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\103-蛋类'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3036537"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_103(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)