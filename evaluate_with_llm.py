import os
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import time
from datetime import datetime

# ==================== 配置 ====================
API_URL = "http://127.0.0.1:8000/chat"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ 未找到 DEEPSEEK_API_KEY！请检查 .env 文件。")

# 测试用例：问题 + 期望达到的标准
test_cases = [
    {
        "id": "业务-退货流程",
        "question": "我想退货，怎么操作？",
        "expected": "应该给出退货流程步骤（提交申请→商家审核→寄回商品→确认退款），并提及7天内可退货"
    },
    {
        "id": "业务-物流时效",
        "question": "物流多久不更新可以联系客服？",
        "expected": "应该说明超过48小时未更新可联系客服查询"
    },
    {
        "id": "业务-支付方式",
        "question": "你们支持哪些支付方式？",
        "expected": "应该列出微信支付、支付宝、银行卡支付三种方式"
    },
    {
        "id": "盲区-货到付款",
        "question": "你们支持货到付款吗？",
        "expected": "应该明确表示不支持货到付款，并引导使用支持的支付方式"
    },
    {
        "id": "盲区-京东卡",
        "question": "可以用京东卡支付吗？",
        "expected": "应该表示暂不支持，并引导使用支持的支付方式"
    },
    {
        "id": "盲区-春节发货",
        "question": "春节发货吗？",
        "expected": "如果知识库未覆盖，应该诚实告知，不瞎编"
    },
    {
        "id": "闲聊-问候",
        "question": "你好",
        "expected": "应该友好问候，不需要调用知识库"
    },
    {
        "id": "闲聊-天气",
        "question": "今天天气怎么样",
        "expected": "应该礼貌告知这是客服系统，不提供天气服务，并引导用户咨询业务问题"
    },
    {
        "id": "闲聊-感谢",
        "question": "谢谢你的帮助",
        "expected": "应该礼貌回应感谢"
    },
]

def judge_answer(question, answer, expected):
    """让DeepSeek当裁判，对回答进行多维度打分"""
    
    prompt = f"""你是一个AI客服系统评估专家。请对以下AI客服的回答进行多维度评分。

**用户问题**：{question}

**AI客服回答**：{answer}

**期望标准**：{expected}

请从以下三个维度分别打分（每个维度1-5分），并给出简短理由：

1. **准确性**：回答是否准确、不瞎编？（1=完全错误，5=完全准确）
2. **完整性**：是否覆盖了用户想知道的要点？（1=严重遗漏，5=完全覆盖）
3. **语言质量**：是否礼貌、专业、使用"您"称呼用户？（1=生硬不礼貌，5=非常专业友好）

最终输出格式（严格按此格式，方便程序解析）：
准确性: X分
完整性: X分
语言质量: X分
总分: X.X/5
评语: XXX
"""
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        },
        timeout=30
    )
    
    return response.json()["choices"][0]["message"]["content"]

def evaluate():
    results = []
    total_score = 0
    total_cases = len(test_cases)
    
    print(f"🧪 开始LLM裁判评估：共 {total_cases} 个测试用例\n")
    start_time = time.time()
    
    for case in test_cases:
        try:
            # 第一步：调用Agent获取回答
            agent_response = requests.post(
                API_URL,
                json={"message": case["question"]},
                timeout=30
            )
            agent_reply = agent_response.json().get("reply", "")
            
            # 第二步：让LLM裁判打分
            print(f"📝 正在评估 [{case['id']}] ...")
            judge_result = judge_answer(case["question"], agent_reply, case["expected"])
            
            # 解析裁判结果
            lines = judge_result.strip().split('\n')
            scores = {}
            for line in lines:
                if '准确性' in line:
                    scores['accuracy'] = line.split(':')[1].strip()
                elif '完整性' in line:
                    scores['completeness'] = line.split(':')[1].strip()
                elif '语言质量' in line:
                    scores['language'] = line.split(':')[1].strip()
                elif '总分' in line:
                    total = float(line.split(':')[1].strip().split('/')[0])
                    total_score += total
            
            print(f"   准确性: {scores.get('accuracy', 'N/A')}")
            print(f"   完整性: {scores.get('completeness', 'N/A')}")
            print(f"   语言质量: {scores.get('language', 'N/A')}")
            print(f"   总分: {total}\n")
            
            results.append({
                "id": case["id"],
                "question": case["question"],
                "agent_reply": agent_reply[:300],
                "expected": case["expected"],
                "scores": scores,
                "judge_raw": judge_result
            })
            
        except Exception as e:
            print(f"❌ [{case['id']}] 评估失败: {str(e)}\n")
    
    elapsed = time.time() - start_time
    
    # 打印总结报告
    print("=" * 60)
    print(f"📊 LLM裁判评估报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总计: {total_cases} 个测试用例")
    print(f"平均得分: {total_score/total_cases:.2f}/5")
    print(f"总耗时: {elapsed:.1f} 秒")
    print("=" * 60)
    
    # 保存详细报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": total_cases,
        "average_score": f"{total_score/total_cases:.2f}/5",
        "total_time": f"{elapsed:.1f}s",
        "details": results
    }
    
    with open("evaluation_llm_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存至 evaluation_llm_report.json")

if __name__ == "__main__":
    evaluate()