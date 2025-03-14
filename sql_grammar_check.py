import os
import sqlparse
from datasets import load_dataset
import pandas as pd

def is_sql_valid(sql_text: str) -> bool:
    """
    利用 sqlparse 对 SQL 语句进行最基本的语法解析，
    如果能成功解析并返回非空语法树，就视为语法上大概率没问题。
    """
    sql_text = sql_text.strip()
    if not sql_text:
        return False
    try:
        parsed_stmts = sqlparse.parse(sql_text)
        # 只要解析结果非空，就认为语句基本合法
        return len(parsed_stmts) > 0
    except Exception:
        return False

def contains_join(example):
    """
    初步筛选：question、answer、context 任意列是否包含"join" (不区分大小写)。
    """
    question_lower = example["question"].lower() if example["question"] else ""
    answer_lower = example["answer"].lower() if example["answer"] else ""
    context_lower = example["context"].lower() if example["context"] else ""
    return ("join" in question_lower) or ("join" in answer_lower) or ("join" in context_lower)

def contains_no_join(example):
    """
    初步筛选：question、answer、context 任意列是否不包含"join" (不区分大小写)。
    """
    question_lower = example["question"].lower() if example["question"] else ""
    answer_lower = example["answer"].lower() if example["answer"] else ""
    context_lower = example["context"].lower() if example["context"] else ""
    return not (("join" in question_lower) or ("join" in answer_lower) or ("join" in context_lower))


def sql_syntax_check(example):
    """
    对已包含join的语句再进行 SQL 语法检测。
    这里只检 answer 列是否能被 sqlparse 正常解析。
    """
    sql_candidate = example["answer"] or ""
    return is_sql_valid(sql_candidate)

if __name__ == "__main__":

    # 1. 加载数据集
    dataset = load_dataset("b-mc2/sql-create-context", split="train")

    # # 2. 第一步：根据“join”关键词初步过滤
    # filtered_dataset = dataset.filter(contains_join)
    # print("初步筛选后数据量:", len(filtered_dataset))

    # 2. 第一步：根据“join”关键词初步过滤（筛选没有“join”的数据）
    filtered_dataset = dataset.filter(contains_no_join)
    print("初步筛选后数据量:", len(filtered_dataset))

    # 3. 第二步：对 answer 列进行 SQL 语法过滤
    # final_dataset = filtered_dataset.filter(sql_syntax_check)
    final_dataset = filtered_dataset.filter(sql_syntax_check)

    # 4. 可选：只保留 question、answer、context
    final_dataset = final_dataset.remove_columns(
        [col for col in final_dataset.column_names if col not in ("question", "answer", "context")]
    )

    # 5. 查看结果
    print("最终保留数据量:", len(final_dataset))
    # print(final_dataset[:1])  # 打印一个示例

    # ============ 将数据保存为 xlsx 和 parquet ==============
    # 将 HuggingFace Dataset 转换为 pandas DataFrame
    df = final_dataset.to_pandas()

    # # 保存为 xlsx 文件
    # df.to_excel("filtered_dataset_all.xlsx", index=False)

    # 保存为 xlsx 文件
    df.to_excel("filtered_dataset_all_no_join.xlsx", index=False)

    # 保存为 parquet 文件
    # df.to_parquet("filtered_dataset.parquet", index=False)

    print("已将处理后的数据分别保存为 filtered_dataset.xlsx 和 filtered_dataset.parquet 文件。")
