
# # 设置 OpenAI API 密钥
# openai.api_key = 'your_key'
#
# # 使用新 API（1.0.0 版本后）
# response = openai.completions.create(
#   model="gpt-3.5-turbo",  # 或者其他模型名
#   prompt="Your prompt here",
#   max_tokens=64,
#   temperature=0.7
# )
# print(response.choices[0].text)  # 打印返回的文本内容


# # 请将 "<deepseek api key>" 替换为您的DeepSeek API Key
# client = OpenAI(api_key="<your_key>", base_url="https://api.deepseek.com")
# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False  # 非流式输出，如果需要流式输出，设置为True
# )
# print(response.choices[0].message.content)


import os
import sys
import google.generativeai as genai


# from flask import Flask, request, jsonify
import openai  # 确保你已经安装了 openai 库
import time
from typing import Any
import json
from openai import OpenAI
# from datasets import load_dataset


# 从环境变量中读取 API 密钥
#deepseek_api_key = "your_key"
deepseek_api_key = "your_key"


def deepseek_chat(message):
    print("Starting deepseek")
    client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
    response_message = ""

    # 调用 OpenAI API 模拟 Deepseek 的聊天接口
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 使用适当的模型名称
            messages=[
                {"role": "system", "content": "你是SQL工程师"},
                {"role": "user", "content": message},
            ],
            stream=False
        )

        # 打印生成的内容
        #print(response)  # 打印整个响应对象

        # 通过对象属性访问返回的内容
        if response.choices and len(response.choices) > 0:
            response_message = response.choices[0].message.content
        else:
            response_message = "没有返回消息"

    except openai.OpenAIError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return response_message


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
    #file_path="D:\softfile\s1-main\data\train\DSL.txt"
    # # 读取文件中的问题
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     questions = file.readlines()

    # # 去除每个问题的空白字符
    # questions = [question.strip() for question in questions]
    # table = "建表语句：SELECT DISTINCT T1.creation FROM department AS T1 JOIN management AS T2 ON T1.department_id = T2.department_id JOIN head AS T3 ON T2.head_id = T3.head_id WHERE T3.born_state = 'Alabama'"
    # # 将 system_prompt 作为列表第一个元素
    #
    #
    # question=(
    #           "请将上述建表语句分别以下边表结构定义，表关系格式描述:"
    #           "示例：表结构定义:['Table:customers\n Comment:客户表\n Fields:(customer_type:(客户类型) \n customer_id:(客户ID) \n customer_name:(客户姓名) \n phone_number:(客户电话) \n email:(客户邮箱) \n address:(客户地址) \n created_at:(创建时间) \n updated_at:(更新时间))', 'Table:customer_addresses\n Comment:客户地址表\n Fields:(customer_id:(客户ID) \n province:(省份) \n city:(城市) \n detail_address:(详细地址) \n created_at:(创建时间) \n address_id:(地址ID) \n district:(区县) \n updated_at:(更新时间))', 'Table:customer_orders\n Comment:客户订单表\n Fields:(customer_id:(客户ID) \n customer_order_id:(客户订单ID) \n order_id:(订单ID) \n order_status:(订单状态) \n updated_at:(更新时间) \n created_at:(订单创建时间) \n completed_at:(订单完成时间))', 'Table:customer_points\n Comment:客户积分表\n Fields:(customer_id:(客户ID) \n points_id:(积分记录ID) \n points_type:(积分类型) \n points_time:(积分时间) \n points_change:(积分变化))', 'Table:customer_contacts\n Comment:客户联系人表\n Fields:(updated_at:(更新时间) \n customer_id:(客户ID) \n contact_email:(联系人邮箱) \n contact_id:(联系人ID) \n created_at:(创建时间) \n contact_name:(联系人姓名) \n contact_phone:(联系人电话))', 'Table:orders\n Comment:订单信息\n Fields:(customer_id:(客户ID) \n cancelled_at:(订单取消时间) \n total_amount:(订单总金额) \n order_id:(订单ID) \n order_status:(订单状态) \n created_at:(订单创建时间) \n completed_at:(订单完成时间) \n paid_at:(订单支付时间))', 'Table:product_suppliers\n Comment:商品供应商表\n Fields:(updated_at:(更新时间) \n contact_email:(联系人邮箱) \n supplier_name:(供应商名称) \n supplier_id:(供应商ID) \n created_at:(创建时间) \n contact_name:(联系人姓名) \n contact_phone:(联系人电话) \n address:(供应商地址))', 'Table:order_items\n Comment:订单子表\n Fields:(order_item_id:(订单子表ID) \n product_id:(商品ID) \n discount:(商品折扣) \n order_id:(订单ID) \n unit_price:(商品单价) \n quantity:(商品数量) \n total_price:(商品总价))', 'Table:order_status_logs\n Comment:订单状态日志表\n Fields:(log_id:(日志ID) \n status_type:(状态变更类型) \n order_id:(订单ID) \n status_time:(状态变更时间) \n remarks:(备注))', 'Table:order_payments\n Comment:订单支付表\n Fields:(payment_method:(支付方式) \n payment_amount:(支付金额) \n order_id:(订单ID) \n payment_status:(支付状态) \n payment_time:(支付时间) \n payment_id:(支付ID))', 'Table:product_inventory\n Comment:商品库存表\n Fields:(inventory_id:(库存ID) \n product_id:(商品ID) \n warehouse_id:(仓库ID) \n quantity:(库存数量) \n supplier_id:(供应商ID) \n last_shipped:(最后发货时间) \n created_at:(创建时间) \n last_received:(最后收货时间) \n updated_at:(更新时间))', 'Table:products\n Comment:商品表\n Fields:(product_id:(商品ID) \n product_name:(商品名称) \n price:(商品价格) \n supplier_id:(供应商ID) \n created_at:(创建时间) \n category_id:(商品分类) \n updated_at:(更新时间) \n description:(商品描述) \n stock:(商品库存))', 'Table:product_categories\n Comment:商品分类表\n Fields:(description:(分类描述) \n category_name:(分类名称) \n cre ated_at:(创建时间) \n category_id:(分类ID) \n updated_at:(更新时间) \n parent_id:(父分类ID))']"
    #           "示例：表关系:['customer_points.customer_id -> customers.customer_id ', 'order_payments.order_id -> orders.order_id ', 'customer_addresses.customer_id -> customers.customer_id ', 'customer_contacts.customer_id -> customers.customer_id ', 'customer_orders.order_id -> orders.order_id ', 'order_status_logs.order_id -> orders.order_id ', 'orders.customer_id -> customers.customer_id ', 'product_inventory.supplier_id -> product_suppliers.supplier_id ', 'products.supplier_id -> product_suppliers.supplier_id ', 'order_items.order_id -> orders.order_id ', 'order_items.product_id -> products.product_id ', 'product_inventory.product_id -> products.product_id ', 'customer_orders.customer_id -> customers.customer_id ']")
    # all_prompts = table + question
    table = "CREATE TABLE farm_competition (Theme VARCHAR(255), YEAR VARCHAR(255));"
    question = "What are the themes of farm competitions sorted by year in ascending order?"
    answer = "SELECT Theme FROM farm_competition ORDER BY YEAR"

    prompt = (
        "请问这条数据question针对建表语句，生成的sql是否正确（只检测逻辑错误）: 正确返回1，错误返回0"
        "约束：只需回复0或1，无需赘述  ")
    all_prompts = table + "," + question + "," + answer + ";" + prompt
    #result = deepseek_chat(all_prompts)
    result = gemini_qa(all_prompts)
    print(result)
