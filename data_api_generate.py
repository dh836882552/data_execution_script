import os
import time
import google.generativeai as genai
import openai
from datasets import load_dataset, Dataset
from openai import OpenAI

from data.utils.io_utils import question_hash, jdump, jload
import logging
from glob import glob
from functools import partial
from tqdm import tqdm

# 从环境变量中读取 API 密钥
genai.configure(api_key="your_key")  # 更换为正确的 API 密钥


def gemini_qa(prompts):
    # 这里假设 prompts 是一个 list，每个元素是一段要发送给大模型的文本
    max_attempts = 1000
    answer = None
    attempts = 0
    thinking = None

    while answer is None and attempts < max_attempts:
        try:
            # 设置代理 URL 和端口
            proxy_url = 'http://127.0.0.1'
            proxy_port = '7897'  # 请使用你自己的代理端口

            # 设置 http_proxy 和 https_proxy 环境变量
            os.environ['http_proxy'] = f'{proxy_url}:{proxy_port}'
            os.environ['https_proxy'] = f'{proxy_url}:{proxy_port}'

            # 在这里插入一条「系统提示」或「指导性上下文」:
            system_prompt = (
                "检查该数据文本中，分析每行question, answer, context所对应的sql语句，问题和建表语句是否正确？"

            )

            # 将 system_prompt 作为列表第一个元素
            all_prompts = [system_prompt] + prompts

            # 初始化 Gemini 大模型
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')

            # 使用合并后的列表来生成
            response = model.generate_content("\n".join(all_prompts))

            # 提取 thinking 和 answer
            if response.candidates and response.candidates[0].content.parts:
                thinking = (
                    response.candidates[0].content.parts[0].text
                    if len(response.candidates[0].content.parts) > 0
                    else "Thinking part not found"
                )
                answer = (
                    response.candidates[0].content.parts[1].text
                    if len(response.candidates[0].content.parts) > 1
                    else "Answer part not found"
                )
                print("Thinking:", thinking)
                print("Answer:", answer)
            else:
                print("No response candidates or content parts found.")

        except Exception as e:
            print(f"Exception: {str(e)}")
            import time
            time.sleep(60)
            attempts += 1

    return thinking, answer


def process_file_questions(file_path):
    # 1. 读取问题列表
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = file.readlines()

    # 2. 去除空白
    questions = [question.strip() for question in questions if question.strip()]

    # 3. 使用 gemini_qa 生成回答
    thinking, answer = gemini_qa(questions)

    # 4. 写回结果文件
    import os
    result_folder = "result"
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    result_file = os.path.join(result_folder, os.path.basename(file_path))
    with open(result_file, 'w', encoding='utf-8') as result:
        result.write(f"Thinking:\n{thinking}\n")
        result.write(f"\nAnswer:\n{answer}\n")


if __name__ == "__main__":
    import os
    directory = "D:\\softfile\\s1-main\\data\\train"
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory, filename)
            process_file_questions(file_path)


# if __name__ == "__main__":
#
#     file_path = "D:\\softfile\\s1-main\\data\\train\\ai_agent_zj.txt"  # 请替换为您文件的路径
#     process_file_questions(file_path)
