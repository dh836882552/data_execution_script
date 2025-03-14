import pymysql
import pandas as pd
import openpyxl

# MySQL 连接信息（请修改）
MYSQL_CONFIG = {
    "host": "localhost",   # MySQL 服务器地址
    "port": 3306,          # 端口号
    "user": "root",        # 用户名
    "password": "1234",    # 密码
    "database": "test01"   # 测试数据库
}

# 读取 Excel 文件
excel_path = r"D:\softfile\s1-main\data\test\train\data\filtered_dataset_all.xlsx"  # 你的 Excel 文件路径
df = pd.read_excel(excel_path)

# 确保列名匹配
context_col = "context"  # 建表语句列
answer_col = "answer"    # 查询语句列

# 连接 MySQL
conn = pymysql.connect(
    host=MYSQL_CONFIG["host"],
    port=MYSQL_CONFIG["port"],
    user=MYSQL_CONFIG["user"],
    password=MYSQL_CONFIG["password"],
    database=MYSQL_CONFIG["database"],
    autocommit=True
)
cursor = conn.cursor()

# 记录执行结果
results = []

for index, row in df.iterrows():
    print(f"正在处理第 {index + 1} 行数据...")

    # 清空数据库中的表，避免影响后续测试
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # 关闭外键约束
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # 重新开启外键约束

    create_table_sql = row[context_col]
    query_sql = row[answer_col]

    try:
        # 逐条执行建表语句
        create_table_statements = create_table_sql.split(';')
        for statement in create_table_statements:
            statement = statement.strip()  # 去除可能的多余空格
            if statement:
                print(f"执行建表语句: {statement}")  # 打印正在执行的建表语句
                cursor.execute(statement)  # 执行每个建表语句

        # 执行查询语句
        print(f"执行查询语句: {query_sql}")  # 打印正在执行的查询语句
        cursor.execute(query_sql)

        # 记录成功的执行结果
        results.append({"Index": index, "Status": "Success", "Error": ""})
        print(f"第 {index + 1} 行数据执行成功!")

    except Exception as e:
        # 记录失败的执行结果
        results.append({"Index": index, "Status": "Failed", "Error": str(e)})
        print(f"第 {index + 1} 行数据执行失败，错误信息: {str(e)}")

# 关闭连接
cursor.close()
conn.close()

# 保存结果到 Excel（仅为日志记录）
result_df = pd.DataFrame(results)
result_df.to_excel("results.xlsx", index=False)

# 筛选原始数据中对应 Status 为 Success 的行
df["Status"] = ["Success" if res["Status"] == "Success" else "Failed" for res in results]

# 筛选出 Status 为 Success 的数据
success_df = df[df['Status'] == 'Success']

# 将筛选后的结果保存为 filtered_result.xlsx 文件
success_df.to_excel("filtered_result.xlsx", index=False)

print("筛选后的成功数据已保存至 filtered_result.xlsx")
