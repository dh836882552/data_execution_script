import xlrd2
import json

# 读取excel文件
workbook = xlrd2.open_workbook(f"D:\\softfile\\s1-main\\data\\test\\train\\test.xlsx")
output_directory = r"D:\softfile\s1-main\data\test\result"

upProtexts_mes_en = """
请根据以下DDL语句和用户问题将自然语言转换成SQL语句\n下面是数据创建表的DDL语句    

    {user_input1}

用户问题:
    {user_input}
    """
unProtexts = [upProtexts_mes_en]  # 假设只有一个模板

# 指定列索引
answer_column_index = 0
question_column_index = 1
table_column_index = 2

# 存储数据
existing_data = []

for idx, unProtext in enumerate(unProtexts):
    sheetname = workbook.sheet_by_index(idx)
    json_list = []

    for row_idx in range(1, sheetname.nrows):  # 从第1行开始，跳过表头
        # 获取答案
        answer = sheetname.cell_value(row_idx, answer_column_index)

        # 处理答案字段
        if "dsl" in answer:
            try:
                final_answer = answer.split('"dsl":')[1].split('"title"')[0].rstrip(',\n').strip()
            except IndexError:
                final_answer = ""  # 如果发生异常，设为默认值
        else:
            final_answer = answer

        # 获取问题和表格信息
        question = sheetname.cell_value(row_idx, question_column_index)
        table = sheetname.cell_value(row_idx, table_column_index)

        # 替换模板中的标签
        Protext = unProtext.replace("{user_input}", question)
        Protext = Protext.replace("{user_input1}", table)

        # 生成JSON数据
        if final_answer != "":
            json_data = {
                "instruction": Protext,
                "input": "",
                "output": final_answer
            }
            json_list.append(json_data)

    # 将结果添加到 existing_data 列表
    existing_data.extend(json_list)

# 将结果转换为 JSON 格式
json_data_str = json.dumps(existing_data, indent=4, ensure_ascii=False)

# 构建输出文件名
jsonSave = f"{output_directory}\\crm_output_sql.json"

# 保存为JSON文件
with open(jsonSave, 'w', encoding='utf-8') as json_file:
    json_file.write(json_data_str)

print(f"文件 {jsonSave} 保存成功！")
