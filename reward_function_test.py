# import pandas as pd
#
# # 读取 JSON 文件
# df = pd.read_json("train.json")
#
# # 转换为 Parquet 格式
# df.to_parquet("train.parquet", engine="pyarrow", index=False)
#
# print("JSON 已成功转换为 Parquet！")

# 上传huggingface
# from huggingface_hub import HfApi
#
# # 你的 Hugging Face Token（确保是 Write 权限）
# HF_TOKEN = "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"
#
# api = HfApi()
#
# # 使用 Token 认证
# api.upload_file(
#     path_or_fileobj="test.parquet",
#     path_in_repo="test.parquet",
#     repo_id="explore01/sqltest",
#     repo_type="dataset",
#     token=HF_TOKEN  # 这里手动提供 Token
# )

import re
import mysql.connector  # 使用 mysql-connector-python 连接 MySQL 数据库



# 格式奖励：检查是否符合 <think>...</think><answer>...</answer> 格式
def r1v_format_reward(predict_str: str) -> float:
    pattern = re.compile(r"<think>.*?</think>\s*<answer>.*?</answer>", re.DOTALL)
    format_match = re.fullmatch(pattern, predict_str)
    return 1.0 if format_match else 0.0





# SQL 语法检查奖励：通过 sqlparse 库检查 SQL 是否符合语法
def sql_syntax_check_reward(predict_str: str) -> float:
    try:
        # 使用 sqlparse 来解析 SQL 语句
        import sqlparse
        parsed = sqlparse.parse(predict_str)
        # 如果能成功解析，就返回 1.0 奖励
        if parsed:
            return 1.0
    except Exception as e:
        print(f"SQL Syntax Error: {e}")
    return 0.0


# SQL 执行奖励：执行 SQL 语句，判断是否成功
def sql_execution_reward(predict_str: str) -> float:
    try:
        # 创建数据库连接
        db_connection = mysql.connector.connect(
            host="localhost",  # 数据库主机地址
            user="root",  # 数据库用户名
            password="1234",  # 数据库密码
            database="test01"  # 数据库名
        )

        cursor = db_connection.cursor()
        cursor.execute(predict_str)
        db_connection.commit()  # 提交事务
        db_connection.close()  # 关闭连接

        return 1.0  # 执行成功，给予奖励
    except mysql.connector.Error as e:
        print(f"SQL Execution Error: {e}")
        return 0.0


# 综合奖励：包括格式奖励、准确性奖励、SQL 语法检查奖励、SQL 执行奖励
def r1v_compute_score(predict_str: str, ground_truth: str) -> float:
    return (
            0.2 * r1v_format_reward(predict_str) +
            0.15 * sql_syntax_check_reward(predict_str) +
            0.15 * sql_execution_reward(predict_str))



if __name__ == "__main__":
    # 使用示例
    predict_str = "<think>...</think><answer>SELECT * FROM users WHERE id = 1</answer>"
    ground_truth = "SELECT * FROM users WHERE id = 1"

    # 计算最终的奖励得分
    score = r1v_compute_score(predict_str, ground_truth)
    print(f"Final Reward Score: {score}")
