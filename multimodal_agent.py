import os
import requests
from dotenv import load_dotenv
load_dotenv()

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

def analyze_product_image(image_url: str, product_type: str = "商品") -> str:
    """
    让AI分析商品图片，判断是否有瑕疵
    """
    prompt = f"""请仔细查看这张{product_type}的图片，从以下方面分析：

1. 商品是否有明显的破损、裂纹、划痕？
2. 如果有瑕疵，具体在什么位置？严重程度如何？
3. 根据常见的电商退换货政策，这种情况是否应该允许退货？
4. 如果是客服，你会给客户什么建议？

请用中文回答，语气专业但友善。"""

    response = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "nex-agi/Nex-N2-Pro",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            "temperature": 0
        }
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"API 调用失败（状态码 {response.status_code}）：{response.text}"


if __name__ == "__main__":
    # 用一张 Unsplash 上的商品图片测试（链接稳定）
    test_image = "https://kkimgs.yisou.com/ims?kt=url&at=ori&key=aHR0cDovL2ltYWdlLnN1bmluZy5jbi8vdWltZy9aUi9zaGFyZV9vcmRlci8xNjI0NjIyMDIzMzQ1MjEzNDRfNjQweDY0MC5qcGc=&sign=yx:-fjZtDgMHm95a6yl8O5g7GaNVLM=&tv=0_0"
    
    print("🔍 正在分析商品图片...\n")
    result = analyze_product_image(test_image, "太阳镜")
    print(f"📊 分析结果：\n{result}")