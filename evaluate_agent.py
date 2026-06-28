import requests
import json
import time
from datetime import datetime

# ==================== 配置 ====================
# 你的API地址（本地或服务器IP）
API_URL = "http://127.0.0.1:8000/chat"

# 测试用例：问题 + 预期关键词（回答中应包含的关键词）
test_cases = [
    # 类别一：知识库能覆盖的问题
    {
        "id": "业务-退货流程",
        "question": "我想退货，怎么操作？",
        "expected_keywords": ["退货", "申请", "审核"]
    },
    {
        "id": "业务-物流时效",
        "question": "物流多久不更新可以联系客服？",
        "expected_keywords": ["48小时", "物流"]
    },
    {
        "id": "业务-支付方式",
        "question": "你们支持哪些支付方式？",
        "expected_keywords": ["微信", "支付宝", "银行卡"]
    },
    # 类别二：知识库覆盖不了的问题
    {
        "id": "盲区-货到付款",
        "question": "你们支持货到付款吗？",
        "expected_keywords": ["不支持", "在线支付"]
    },
    {
        "id": "盲区-京东卡",
        "question": "可以用京东卡支付吗？",
        "expected_keywords": ["不支持", "在线支付"]
    },
    {
        "id": "盲区-春节发货",
        "question": "春节发货吗？",
        "expected_keywords": []  # 只需不报错即可
    },
    # 类别三：闲聊/非业务问题
    {
        "id": "闲聊-问候",
        "question": "你好",
        "expected_keywords": ["你好", "欢迎"]
    },
    {
        "id": "闲聊-天气",
        "question": "今天天气怎么样",
        "expected_keywords": ["客服", "业务"]  # 表明它理解了这不是业务问题
    },
    {
        "id": "闲聊-感谢",
        "question": "谢谢你的帮助",
        "expected_keywords": ["不客气", "欢迎"]
    },
]

def evaluate():
    results = []
    passed = 0
    total = len(test_cases)
    
    print(f"🧪 开始评估：共 {total} 个测试用例\n")
    start_time = time.time()
    
    for case in test_cases:
        try:
            # 发送请求
            response = requests.post(
                API_URL,
                json={"message": case["question"]},
                timeout=30
            )
            reply = response.json().get("reply", "")
            
            # 判断是否通过：所有预期关键词都出现在回复中
            keywords_found = all(kw in reply for kw in case["expected_keywords"])
            
            # 特殊处理：如果预期关键词为空，只要不报错就算通过
            if not case["expected_keywords"]:
                keywords_found = True
            
            status = "✅" if keywords_found else "❌"
            if keywords_found:
                passed += 1
            
            results.append({
                "id": case["id"],
                "question": case["question"],
                "reply": reply[:200] + "..." if len(reply) > 200 else reply,
                "expected_keywords": case["expected_keywords"],
                "passed": keywords_found
            })
            
            print(f"{status} [{case['id']}] {case['question']}")
            if not keywords_found:
                print(f"   预期关键词: {case['expected_keywords']}")
                print(f"   实际回复: {reply[:100]}...")
            
        except Exception as e:
            results.append({
                "id": case["id"],
                "question": case["question"],
                "reply": f"请求失败: {str(e)}",
                "expected_keywords": case["expected_keywords"],
                "passed": False
            })
            print(f"❌ [{case['id']}] 请求失败: {str(e)}")
    
    elapsed = time.time() - start_time
    
    # 打印总结报告
    print("\n" + "=" * 60)
    print(f"📊 评估报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总计: {total} 个测试用例")
    print(f"通过: {passed} 个")
    print(f"失败: {total - passed} 个")
    print(f"准确率: {passed/total*100:.1f}%")
    print(f"总耗时: {elapsed:.1f} 秒")
    print(f"平均响应时间: {elapsed/total:.1f} 秒/题")
    print("=" * 60)
    
    # 保存详细报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "accuracy": f"{passed/total*100:.1f}%",
        "avg_response_time": f"{elapsed/total:.1f}s",
        "details": results
    }
    
    with open("evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存至 evaluation_report.json")

if __name__ == "__main__":
    evaluate()