import os
import sys
import google.generativeai as genai
import openai  # 确保你已经安装了 openai 库
import time
from openai import OpenAI

import pymysql
import pandas as pd
import openpyxl

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

    # 读取 Excel 文件
    excel_path = r"C:\Users\18368\AppData\Roaming\JetBrains\PyCharmCE2023.1\light-edit\data\gpdb.xlsx"  # 你的 Excel 文件路径
    df = pd.read_excel(excel_path)

    # 确保列名匹配
    context_col = "table"  # 建表语句列
    sql_answer_col = "生成SQL"  # 查询语句列
    dsl_answer_col = "映射DSL"  # 查询语句列
    question_col = "提问问题"  # 问题语句列

    table = context_col
    question = question_col
    sql_answer = sql_answer_col
    dsl_answer = dsl_answer_col

    prompt = (
        "请根据这条数据提问问题，针对表结构定义，检查生成的mysql语句和DSL语句是否全部正确（检测逻辑和语法错误）: 正确返回1，错误返回0"
        "约束：只需回复0或1，无需赘述  ")

    # 用来存储每一行的返回结果
    results = []

    # 遍历所有行并调用 deepseek_chat
    for index, row in df.iterrows():
        print(f"正在处理第 {index + 1} 行数据...")

        # 从每一行提取数据来构建 all_prompts
        all_prompts = f"{row[table]},{row[question]},{row[sql_answer]}，{row[dsl_answer]};{prompt}"

        # 调用 Deepseek API
        # result = deepseek_chat(all_prompts)
        result = gemini_qa(all_prompts)
        print(f"返回结果: {result}")

        # 清理结果并将 result 添加到 results 列表中，转换为 "Success" 或 "Failed"
        if "1" in result:  # 去除多余的空格并判断
            results.append("Success")
        else:
            results.append("Failed")

    # 将结果存储到 df 中
    df["Status"] = results

    # 保存结果到 Excel（仅为日志记录）
    df.to_excel("results.xlsx", index=False)

    # 筛选出 Status 为 Success 的数据
    success_df = df[df['Status'] == 'Success']

    # 将筛选后的结果保存为 filtered_result.xlsx 文件
    success_df.to_excel("gpdb_check_result.xlsx", index=False)

    print("筛选后的成功数据已保存至 gpdb_check_result.xlsx")
