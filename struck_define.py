import xlrd2
import json
import os
import sys
import google.generativeai as genai


# from flask import Flask, request, jsonify
import openai  # 确保你已经安装了 openai 库
import time
from typing import Any
import json
from openai import OpenAI
from datasets import load_dataset

def gemini_qa(prompt: str):
    max_attempts = 1000
    answer = None
    attempts = 0
    while answer is None and attempts < max_attempts:
        try:
            #设置代理 URL 和端口
            proxy_url = 'http://127.0.0.1'
            proxy_port = '7897'  # 请使用你自己的代理端口

            # 设置 http_proxy 和 https_proxy 环境变量
            os.environ['http_proxy'] = f'{proxy_url}:{proxy_port}'
            os.environ['https_proxy'] = f'{proxy_url}:{proxy_port}'

            # Configure your API key (best practice: use environment variables)
            genai.configure(api_key="your_key")  
            # Initialize the model
            model = genai.GenerativeModel(
                'gemini-2.0-flash-thinking-exp')  # or 'gemini-pro-vision' for images, or the model you are trying to use.

            # prompt = "Your prompt here"  # replace with your prompt.

            # Generate the content
            response = model.generate_content(prompt)


            # Access the generated text
            if response.candidates and response.candidates[0].content.parts:
                thinking = response.candidates[0].content.parts[0].text if len(
                    response.candidates[0].content.parts) > 0 else "Thinking part not found"
                answer = response.candidates[0].content.parts[1].text if len(
                    response.candidates[0].content.parts) > 1 else "Answer part not found"
                # print(thinking)
                # print(answer)
            else:
                print("No response candidates or content parts found.")

        except Exception as e:
            print(f"Exception: {str(e)}")
            time.sleep(60)
    return thinking#, answer

if __name__ == "__main__":

    # 读取excel文件
    workbook = xlrd2.open_workbook(f"D:\\softfile\\s1-main\\data\\test\\train\\data\\crm_out_example.xlsx")
    # 指定保存目录
    output_directory = r"D:\softfile\s1-main\data\test\result"

    upProtexts_mes_en = """
    请根据用户选择的数据库和该库的部分可用表结构定义来回答用户问题.
        数据库名:
          test
        表结构定义:
          {user_input1}
        表关系: 
          {user_input2}
    用户问题:
        {user_input}

    请一步步思考并按照以下格式回复：
        {
            "sql": "SQL Query to run"
        }
        """
    # 定义unProtext的值，假设你会提供三个unProtext
    unProtexts = [
        upProtexts_mes_en
    ]

    # 指定回答字段列
    answer_column_index = 0

    # 指定问题字段列
    question_column_index = 1

    # 指定表结构定义
    table_column_index = 2

    mapping = ['bank']

    # 遍历sheet索引
    existing_data = []
    for idx, unProtext in enumerate(unProtexts):
        # 获取sheet
        sheetname = workbook.sheet_by_index(idx)

        # 定义一个存储json的列表
        json_list = []
        # 遍历工作表的每一行
        for row_idx in range(0, sheetname.nrows):
            if row_idx == 0:
                continue
            # 获取“答案”字段的值
            answer = sheetname.cell_value(row_idx, answer_column_index)


            # 处理答案字段
            if "dsl" in answer:
                try:
                    final_answer = answer.split('"dsl":')[1].split('"title"')[0].rstrip(',\n').strip()
                except IndexError:
                    final_answer = ""  # 如果发生异常，设为默认值
            else:
                final_answer = answer

            question = sheetname.cell_value(row_idx, question_column_index)
            table = sheetname.cell_value(row_idx, table_column_index)

            question1 = (
                "请将上述建表语句分别以下边表关系格式描述:"
                "示例：['Table:customers\n Comment:客户表\n Fields:(customer_type:(客户类型) \n customer_id:(客户ID) \n customer_name:(客户姓名) \n phone_number:(客户电话) \n email:(客户邮箱) \n address:(客户地址) \n created_at:(创建时间) \n updated_at:(更新时间))', 'Table:customer_addresses\n Comment:客户地址表\n Fields:(customer_id:(客户ID) \n province:(省份) \n city:(城市) \n detail_address:(详细地址) \n created_at:(创建时间) \n address_id:(地址ID) \n district:(区县) \n updated_at:(更新时间))', 'Table:customer_orders\n Comment:客户订单表\n Fields:(customer_id:(客户ID) \n customer_order_id:(客户订单ID) \n order_id:(订单ID) \n order_status:(订单状态) \n updated_at:(更新时间) \n created_at:(订单创建时间) \n completed_at:(订单完成时间))', 'Table:customer_points\n Comment:客户积分表\n Fields:(customer_id:(客户ID) \n points_id:(积分记录ID) \n points_type:(积分类型) \n points_time:(积分时间) \n points_change:(积分变化))', 'Table:customer_contacts\n Comment:客户联系人表\n Fields:(updated_at:(更新时间) \n customer_id:(客户ID) \n contact_email:(联系人邮箱) \n contact_id:(联系人ID) \n created_at:(创建时间) \n contact_name:(联系人姓名) \n contact_phone:(联系人电话))', 'Table:orders\n Comment:订单信息\n Fields:(customer_id:(客户ID) \n cancelled_at:(订单取消时间) \n total_amount:(订单总金额) \n order_id:(订单ID) \n order_status:(订单状态) \n created_at:(订单创建时间) \n completed_at:(订单完成时间) \n paid_at:(订单支付时间))', 'Table:product_suppliers\n Comment:商品供应商表\n Fields:(updated_at:(更新时间) \n contact_email:(联系人邮箱) \n supplier_name:(供应商名称) \n supplier_id:(供应商ID) \n created_at:(创建时间) \n contact_name:(联系人姓名) \n contact_phone:(联系人电话) \n address:(供应商地址))', 'Table:order_items\n Comment:订单子表\n Fields:(order_item_id:(订单子表ID) \n product_id:(商品ID) \n discount:(商品折扣) \n order_id:(订单ID) \n unit_price:(商品单价) \n quantity:(商品数量) \n total_price:(商品总价))', 'Table:order_status_logs\n Comment:订单状态日志表\n Fields:(log_id:(日志ID) \n status_type:(状态变更类型) \n order_id:(订单ID) \n status_time:(状态变更时间) \n remarks:(备注))', 'Table:order_payments\n Comment:订单支付表\n Fields:(payment_method:(支付方式) \n payment_amount:(支付金额) \n order_id:(订单ID) \n payment_status:(支付状态) \n payment_time:(支付时间) \n payment_id:(支付ID))', 'Table:product_inventory\n Comment:商品库存表\n Fields:(inventory_id:(库存ID) \n product_id:(商品ID) \n warehouse_id:(仓库ID) \n quantity:(库存数量) \n supplier_id:(供应商ID) \n last_shipped:(最后发货时间) \n created_at:(创建时间) \n last_received:(最后收货时间) \n updated_at:(更新时间))', 'Table:products\n Comment:商品表\n Fields:(product_id:(商品ID) \n product_name:(商品名称) \n price:(商品价格) \n supplier_id:(供应商ID) \n created_at:(创建时间) \n category_id:(商品分类) \n updated_at:(更新时间) \n description:(商品描述) \n stock:(商品库存))', 'Table:product_categories\n Comment:商品分类表\n Fields:(description:(分类描述) \n category_name:(分类名称) \n cre ated_at:(创建时间) \n category_id:(分类ID) \n updated_at:(更新时间) \n parent_id:(父分类ID))']")
            all_prompts1 = table + question1
            result1 = gemini_qa(all_prompts1)

            question2 = (
                "请将上述建表语句分别以下边表结构定义描述:"
                "示例：['customer_points.customer_id -> customers.customer_id ', 'order_payments.order_id -> orders.order_id ', 'customer_addresses.customer_id -> customers.customer_id ', 'customer_contacts.customer_id -> customers.customer_id ', 'customer_orders.order_id -> orders.order_id ', 'order_status_logs.order_id -> orders.order_id ', 'orders.customer_id -> customers.customer_id ', 'product_inventory.supplier_id -> product_suppliers.supplier_id ', 'products.supplier_id -> product_suppliers.supplier_id ', 'order_items.order_id -> orders.order_id ', 'order_items.product_id -> products.product_id ', 'product_inventory.product_id -> products.product_id ', 'customer_orders.customer_id -> customers.customer_id ']")
            all_prompts2 = table + question2
            result2 = gemini_qa(all_prompts2)

            # 替换unProtext中的{user_input}
            Protext = unProtext.replace("{user_input}", question)
            Protext = Protext.replace("{user_input1}", result1)  # 替换第二个标签
            Protext = Protext.replace("{user_input2}", result2)  # 替换第二个标签

            final_answer = json.dumps({"sql": final_answer}, ensure_ascii=False)
            # 创建一个字典，将“答案”字段的值映射到JSON的"output"字段
            if final_answer != "":
                json_data = {
                    "instruction": Protext,
                    "input": "",
                    "output": final_answer
                }
                json_list.append(json_data)
        existing_data.extend(json_list)
    print(existing_data)
    json_data_str = json.dumps(existing_data, indent=4, ensure_ascii=False)

    # 构建文件名
    jsonSave = f"{output_directory}\\crm_out_sql.json"

    with open(jsonSave, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data_str)

    print(f"文件 {jsonSave} 保存成功！")



