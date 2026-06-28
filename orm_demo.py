from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, Session, relationship

# 1. 创建数据库引擎（连接SQLite文件）
engine = create_engine("sqlite:///customer_service.db", echo=True)

# 2. 创建基类
Base = declarative_base()

# 3. 定义Customer表（对应你已有的customers表）
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    # 建立与ChatLog的关系
    chat_logs = relationship("ChatLog", back_populates="customer")

# 4. 定义ChatLog表（对应你已有的chat_logs表）
class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True)
    user_question = Column(Text, nullable=False)
    agent_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    customer_id = Column(Integer, ForeignKey("customers.id"))
    # 建立与Customer的关系
    customer = relationship("Customer", back_populates="chat_logs")

# 5. 创建会话
session = Session(engine)

# 6. 查询：每个客户问了多少问题
print("=== 每个客户的提问数量 ===")
results = (
    session.query(Customer.name, func.count(ChatLog.id))
    .join(ChatLog, Customer.id == ChatLog.customer_id)
    .group_by(Customer.name)
    .order_by(func.count(ChatLog.id).desc())
    .all()
)

for name, count in results:
    print(f"{name} 问过 {count} 个问题")

# 7. 查询：客户张三的所有问题
print("\n=== 张三的所有问题 ===")
zhang = session.query(Customer).filter(Customer.name == "张三").first()
if zhang:
    for log in zhang.chat_logs:
        print(f"[{log.created_at}] {log.user_question}")

# 8. 新增一个客户和一条聊天记录
print("\n=== 新增客户王五 ===")
new_customer = Customer(name="王五", phone="13700003333")
session.add(new_customer)
session.commit()

new_log = ChatLog(
    user_question="物流三天没更新了怎么办",
    agent_reply="您好，物流问题建议您...",
    customer_id=new_customer.id
)
session.add(new_log)
session.commit()
print(f"✅ 已新增客户王五，并添加了一条聊天记录")

session.close()