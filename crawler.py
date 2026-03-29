# -*- coding: utf-8 -*-
import requests
import sys
import os
import time
import json
import re
from bs4 import BeautifulSoup

# ============================================
# 使用 DeepSeek 免费 API 生成结构化笔记
# ============================================

# 从环境变量读取 API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
USE_AI = True

def crawl_hanchacha(lesson_name):
    """从 hanchacha.com 爬取所有相关资料"""
    print(f"  🔍 正在从 hanchacha.com 搜索《{lesson_name}》...")
    
    all_text = ""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 搜索
        search_url = f"https://hanchacha.com/?s={lesson_name}"
        print(f"    搜索URL: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找相关链接
        links = soup.find_all('a', href=True)
        found_urls = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text().lower()
            if lesson_name.lower() in text and 'hanchacha.com' in href:
                if href not in found_urls:
                    found_urls.append(href)
        
        print(f"    找到 {len(found_urls)} 个相关页面")
        
        # 提取所有页面内容
        for idx, url in enumerate(found_urls[:3]):
            try:
                print(f"    正在提取页面 {idx+1}: {url}")
                page_resp = requests.get(url, headers=headers, timeout=10)
                page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                content_div = page_soup.find('article') or page_soup.find('div', class_='entry-content') or page_soup.find('div', class_='post-content')
                
                if content_div:
                    text = content_div.get_text(strip=True)
                    # 清理文本
                    text = re.sub(r'\s+', ' ', text)
                    all_text += f"\n\n--- 页面 {idx+1} ---\n{text[:1500]}"
                    print(f"      提取到 {len(text[:1500])} 字")
            except Exception as e:
                print(f"    提取失败: {e}")
                
    except Exception as e:
        print(f"  hanchacha 爬取失败: {e}")
    
    return all_text[:4000]

def crawl_other_sites(lesson_name):
    """爬取其他网站作为补充"""
    other_text = ""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 百度搜索
    try:
        print(f"    正在搜索百度...")
        url = f"https://www.baidu.com/s?wd={lesson_name} 课文讲解 知识点"
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result')
        for idx, result in enumerate(results[:2]):
            text = result.get_text(strip=True)
            if len(text) > 100:
                other_text += f"\n\n--- 百度搜索结果 {idx+1} ---\n{text[:800]}"
        print(f"    百度找到 {len(results[:2])} 条结果")
    except Exception as e:
        print(f"    百度搜索失败: {e}")
    
    return other_text[:2000]

def generate_with_ai(lesson_name, raw_materials):
    """使用 AI 生成完整的学霸笔记"""
    
    print(f"  🤖 AI 状态: {'已启用' if DEEPSEEK_API_KEY else '未配置（使用模板）'}")
    
    if DEEPSEEK_API_KEY and USE_AI:
        try:
            print("  🤖 正在调用 DeepSeek API...")
            
            # 完整的模板
            template = f"""请根据以下关于《{lesson_name}》的教学资料，生成一份完整的、高质量的学霸笔记。

必须严格按照以下模板格式，每个板块都要写满具体内容，不能留空，不能用"请根据课文填写"这种占位符：

# 🌊 探秘{lesson_name} · 学霸综合笔记 🐠

> 一份集**知识点、课堂笔记、教学思路**于一体的超实用手册

---

## 📚 一、课文一瞥：它讲了什么？

（写具体的内容：课文简介、核心问题、主要内容、中心句）

---

## 🧱 二、文章结构：总分总，超清晰！

| 部分 | 自然段 | 内容 | 作用 |
|------|--------|------|------|
| 开头 | （具体段落） | （具体内容） | （具体作用） |
| 中间 | （具体段落） | （具体内容） | （具体作用） |
| 结尾 | （具体段落） | （具体内容） | （具体作用） |

> 💡 **写作要点：** （总结结构特点）

---

## ✨ 三、阅读与写作：深挖课文"宝藏"

### 1. 写作特色分析

| 阅读要点 | 写法分析 | 写作小技巧 |
|----------|----------|------------|
| （具体的写作特点1） | （具体的分析方法） | （具体可操作的小技巧） |
| （具体的写作特点2） | （具体的分析方法） | （具体可操作的小技巧） |
| （具体的写作特点3） | （具体的分析方法） | （具体可操作的小技巧） |

> 💡 **写作要点：** （总结写作方法）

---

## 📝 四、语言积累：词语库+句式库

### 1. 重点词语

| 类别 | 词语 |
|------|------|
| 必会字词 | （具体的词语，至少5个） |
| 近义词 | （具体的词语对） |
| 反义词 | （具体的词语对） |
| 成语/AABC | （具体的成语） |

### 2. 仿写句式

> **（句式名称，如：有的...有的...有的...）**
>
> *   **课文原句**：（具体的原句）
> *   **仿写示例**：（具体的仿写，要完整）

---

## 🎯 五、课后挑战：小试牛刀

1.  **朗读小能手**：（具体的朗读任务）
2.  **小小解说员**：（具体的解说任务）
3.  **妙笔生花**：（具体的写作任务）

---

以下是爬取到的资料，请基于这些内容生成具体的、有教学价值的笔记：

{raw_materials}

如果资料不足，请结合你的语文教学知识补充完整。

请直接输出笔记内容，不要输出其他解释。"""

            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是小学语文教学专家，擅长生成高质量、详细的课文笔记。每个板块都要写具体、有教学价值的内容，绝对不能用'请根据课文填写'这种占位符。"},
                        {"role": "user", "content": template}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
                },
                timeout=60
            )
            
            print(f"  API 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                note = result["choices"][0]["message"]["content"]
                print(f"  ✅ AI 生成成功！笔记长度: {len(note)} 字")
                return note
            else:
                print(f"  ⚠️ AI 调用失败: {response.status_code}")
                print(f"  错误信息: {response.text[:500]}")
                return generate_template_note(lesson_name, raw_materials)
                
        except Exception as e:
            print(f"  ⚠️ AI 生成异常: {e}")
            import traceback
            traceback.print_exc()
            return generate_template_note(lesson_name, raw_materials)
    else:
        print("  📝 使用模板生成（AI未启用）")
        return generate_template_note(lesson_name, raw_materials)

def generate_template_note(lesson_name, raw_materials):
    """备用：基于模板生成（不用 AI）"""
    
    # 从爬取材料中提取一段作为内容
    content_preview = raw_materials[:800] if raw_materials else f"《{lesson_name}》是一篇优美的课文。"
    
    return f"""# 🌊 探秘{lesson_name} · 学霸综合笔记 🐠

> 一份集**知识点、课堂笔记、教学思路**于一体的超实用手册

---

## 📚 一、课文一瞥：它讲了什么？

{content_preview}

*   **核心问题**：本文的核心思想是什么？
*   **主要内容**：课文从多个角度展开描写。
*   **中心句**：文中的点睛之笔值得品味。

---

## 🧱 二、文章结构：总分总，超清晰！

| 部分 | 自然段 | 内容 | 作用 |
|------|--------|------|------|
| **第一部分** | 1 | 引入主题 | 吸引读者 |
| **第二部分** | 2-5 | 具体描写 | 展开叙述 |
| **第三部分** | 6 | 总结升华 | 点明主旨 |

> 💡 **写作要点：** 文章采用清晰的结构，层次分明。

---

## ✨ 三、阅读与写作：深挖课文"宝藏"

### 1. 写作特色分析

| 阅读要点 | 写法分析 | 写作小技巧 |
|----------|----------|------------|
| 生动描写 | 运用比喻、拟人等修辞 | 让文章更生动 |
| 结构清晰 | 总分总结构 | 让读者一目了然 |
| 语言优美 | 精选词语，句式多变 | 增强表达效果 |

> 💡 **写作要点：** 学会运用多种修辞手法，让文章更生动。

---

## 📝 四、语言积累：词语库+句式库

### 1. 重点词语

| 类别 | 词语 |
|------|------|
| 必会字词 | 请根据课文填写 |
| 近义词 | 请根据课文填写 |
| 反义词 | 请根据课文填写 |

### 2. 仿写句式

> **句式示例**
>
> *   **课文原句**：请从课文中找出精彩句子
> *   **仿写示例**：请尝试仿写

---

## 🎯 五、课后挑战：小试牛刀

1.  **朗读小能手**：有感情地朗读课文
2.  **小小解说员**：向家人介绍课文内容
3.  **妙笔生花**：运用学到的写法写一段话

---

*✨ 数据来源：hanchacha.com 及网络爬虫*
*📅 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

def main():
    if len(sys.argv) < 2:
        print("请提供课文名称")
        sys.exit(1)
    
    lesson_name = sys.argv[1]
    print("=" * 60)
    print(f"🕷️ 正在为《{lesson_name}》生成学霸笔记...")
    print(f"🤖 DeepSeek API: {'已配置' if DEEPSEEK_API_KEY else '未配置'}")
    print("=" * 60)
    
    # 1. 爬取 hanchacha
    print("\n⭐ [1/3] 爬取 hanchacha.com...")
    hanchacha_text = crawl_hanchacha(lesson_name)
    print(f"   共收集 {len(hanchacha_text)} 字")
    
    # 2. 爬取其他网站补充
    print("\n📡 [2/3] 补充其他网站...")
    other_text = crawl_other_sites(lesson_name)
    print(f"   共收集 {len(other_text)} 字")
    
    # 合并所有资料
    all_materials = f"""
【来自 hanchacha.com 的资料】
{hanchacha_text}

【来自其他网站的资料】
{other_text}
"""
    
    # 3. 使用 AI 生成笔记
    print("\n🤖 [3/3] 正在生成学霸笔记...")
    note = generate_with_ai(lesson_name, all_materials)
    
    # 4. 保存
    os.makedirs('data', exist_ok=True)
    output_file = f"data/{lesson_name}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(note)
    
    print(f"\n✅ 笔记已保存: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
