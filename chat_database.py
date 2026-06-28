import sqlite3

conn = sqlite3.connect("customer_service.db")

conn.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_question TEXT NOT NULL,
        agent_reply TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 插入一条测试记录
conn.execute(
    "INSERT INTO chat_logs (user_question, agent_reply) VALUES (?, ?)",
    ("我想退货，怎么操作？", "您好，退货流程是：提交申请→商家审核→寄回商品→确认退款。")
)

conn.commit()
print("✅ 数据已插入！")
conn.close()