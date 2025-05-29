import os
import pandas as pd
import docx2txt
import tempfile
import pdfplumber
import requests
import streamlit as st
from io import BytesIO

# 从环境变量读取DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

def call_deepseek_api(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"调用 DeepSeek API 失败，状态码 {response.status_code}: {response.text}"

def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        text = docx2txt.process(tmp.name)
    return text

def extract_text(file):
    if file.name.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif file.name.endswith(".docx"):
        return extract_text_from_docx(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return "不支持的文件类型"

def analyze_interview(transcript, outline, target):
    prompt = f"""
你是一个具备深度洞察力的「访谈分析专家」，熟悉新媒体营销、业务增长、组织管理等多个相关领域。你的任务是对访谈内容进行结构化解析、深入提炼并提出可操作的延伸建议。你的目标不只是整理内容，而是帮助团队洞察规律、发现盲点、形成可复用的方法论。

---

【任务一｜逐条对照访谈大纲】  
请根据下方访谈大纲，逐一检查受访者是否进行了明确回应：  
- 若有回应，请详细提取相关内容，保留受访者典型表述、关键细节、实际数据。  
- 若为“部分覆盖”或“未覆盖”，请提出**精准、延展性强的补问建议**，可用于后续追问或复采。

---

【任务二｜案例与线索提取】  
请识别访谈中所有包含“时间 + 人物 + 行动 + 结果”的完整案例，纳入“案例补充”类；若有数据、因果、判断、方法等信息，请归为“数据线索”类。注意：  
- 案例要突出具体行为与转化结果  
- 数据要反映因果逻辑或策略效果

---

【任务三｜故事模块提取】  
请额外提取受访者**自然讲述中具有代表性或启发意义的故事内容**，标注为“故事”。判断标准如下：  
- 该内容呈现出一段**真实发生的经历**，有助于理解其行为模式、思维方式或问题本质  
- 与房地产经纪行业相关，能引发对业务、客户关系、组织策略的进一步思考  
- 尽可能涵盖要素：“时间、人物、事件、动机、过程、结果”，如要素不全，请整理现有内容并提出**具体可追问补问建议**

---

【任务四｜结构化输出表格】  
请输出以下 Markdown 表格，不允许添加表格外的其他文字：

| 类型 | 问题或主题 | 内容摘要 | 原始话术 | 覆盖情况 | 补问建议 |
|------|------------|----------|-----------|-----------|-----------|

- 类型：大纲对应 / 案例补充 / 数据线索 / 故事  
- 内容摘要：不少于150字，尽量详实，还原受访者逻辑、现象与判断  
- 原始话术：提取具代表性的原句（可略微润色但不改原意）  
- 覆盖情况：是 / 否 / 部分覆盖  
你是一个具备深度洞察力的「访谈分析专家」，熟悉新媒体营销、业务增长、组织管理等多个相关领域。你的任务是对访谈内容进行结构化解析、深入提炼并提出可操作的延伸建议。你的目标不只是整理内容，而是帮助团队洞察规律、发现盲点、形成可复用的方法论。

---

【任务一｜逐条对照访谈大纲】  
请根据下方访谈大纲，逐一检查受访者是否进行了明确回应：  
- 若有回应，请详细提取相关内容，保留受访者典型表述、关键细节、实际数据。  
- 若为“部分覆盖”或“未覆盖”，请提出**精准、延展性强的补问建议**，可用于后续追问或复采。

---

【任务二｜案例与线索提取】  
请识别访谈中所有包含“时间 + 人物 + 行动 + 结果”的完整案例，纳入“案例补充”类；若有数据、因果、判断、方法等信息，请归为“数据线索”类。注意：  
- 案例要突出具体行为与转化结果  
- 数据要反映因果逻辑或策略效果

---

【任务三｜故事模块提取】  
请额外提取受访者**自然讲述中具有代表性或启发意义的故事内容**，标注为“故事”。判断标准如下：  
- 该内容呈现出一段**真实发生的经历**，有助于理解其行为模式、思维方式或问题本质  
- 与房地产经纪行业相关，能引发对业务、客户关系、组织策略的进一步思考  
- 尽可能涵盖要素：“时间、人物、事件、动机、过程、结果”，如要素不全，请整理现有内容并提出**具体可追问补问建议**

---

【任务四｜结构化输出表格】  
请输出以下 Markdown 表格，不允许添加表格外的其他文字：

| 类型 | 问题或主题 | 内容摘要 | 原始话术 | 覆盖情况 | 补问建议 |
|------|------------|----------|-----------|-----------|-----------|

- 类型：大纲对应 / 案例补充 / 数据线索 / 故事  
- 内容摘要：不少于150字，尽量详实，还原受访者逻辑、现象与判断  
- 原始话术：提取具代表性的原句（可略微润色但不改原意）  
- 覆盖情况：是 / 否 / 部分覆盖  
- 补问建议：若为“否”或“部分覆盖”，必须给出具体可操作的问题，**鼓励提出延伸性思考问题**
你是一个具备深度洞察力的「访谈分析专家」，熟悉新媒体营销、业务增长、组织管理等多个相关领域。你的任务是对访谈内容进行结构化解析、深入提炼并提出可操作的延伸建议。你的目标不只是整理内容，而是帮助团队洞察规律、发现盲点、形成可复用的方法论。

---

【任务一｜逐条对照访谈大纲】  
请根据下方访谈大纲，逐一检查受访者是否进行了明确回应：  
- 若有回应，请详细提取相关内容，保留受访者典型表述、关键细节、实际数据。  
- 若为“部分覆盖”或“未覆盖”，请提出**精准、延展性强的补问建议**，可用于后续追问或复采。

---

【任务二｜案例与线索提取】  
请识别访谈中所有包含“时间 + 人物 + 行动 + 结果”的完整案例，纳入“案例补充”类；若有数据、因果、判断、方法等信息，请归为“数据线索”类。注意：  
- 案例要突出具体行为与转化结果  
- 数据要反映因果逻辑或策略效果

---

【任务三｜故事模块提取】  
请额外提取受访者**自然讲述中具有代表性或启发意义的故事内容**，标注为“故事”。判断标准如下：  
- 该内容呈现出一段**真实发生的经历**，有助于理解其行为模式、思维方式或问题本质  
- 与房地产经纪行业相关，能引发对业务、客户关系、组织策略的进一步思考  
- 尽可能涵盖要素：“时间、人物、事件、动机、过程、结果”，如要素不全，请整理现有内容并提出**具体可追问补问建议**

---

【任务四｜结构化输出表格】  
请输出以下 Markdown 表格，不允许添加表格外的其他文字：

| 类型 | 问题或主题 | 内容摘要 | 原始话术 | 覆盖情况 | 补问建议 |
|------|------------|----------|-----------|-----------|-----------|

- 类型：大纲对应 / 案例补充 / 数据线索 / 故事  
- 内容摘要：不少于150字，尽量详实，还原受访者逻辑、现象与判断  
- 原始话术：提取具代表性的原句（可略微润色但不改原意）  
- 覆盖情况：是 / 否 / 部分覆盖  
- 补问建议：若为“否”或“部分覆盖”，必须给出具体可操作的问题，**鼓励提出延伸性思考问题**

---

【可选任务｜启发性延展】  
如当前访谈内容丰富，请补充以下内容：

### 【专家总结】  
用200字以内总结访谈的核心洞察，例如：受访者的策略核心在哪，当前方法的优劣，有哪些可转化为方法论的模式。

### 【延伸追问清单】  
请基于当前访谈内容，从业务、策略、组织、数据等角度，生成5条可用于二次访谈或横向对比研究的深度问题。  
例如：  
- 针对爆款频次下降，受访者是否曾做过流量触达路径的重构？  
- 如何评估短视频与图文内容对意向客户的引导路径差异？

### 【潜在策略建议】  
如内容足够清晰，请尝试生成 2-3 条**可落地的建议**，帮助团队优化现有策略、内容结构或运营节奏。

---

请严格按照以上格式完成任务，优先输出表格内容。如有额外内容请附加在表格之后，不要添加额外解释。

---
【访谈目标】
{target}

【访谈大纲】
{outline}

【访谈原文】
{transcript}
"""
    return call_deepseek_api(prompt)

def main():
    st.set_page_config(page_title="访谈结构整理工具", layout="wide")
    st.title("📋 访谈结构整理 MVP 工具")

    target = st.text_area("请输入访谈目标（例如：本次访谈主要目标是什么）")

    st.markdown("### 第一步：上传访谈文件（pdf、docx、txt）")
    interview_file = st.file_uploader("上传访谈记录文件：", type=["pdf", "docx", "txt"])

    st.markdown("### 第二步：上传访谈大纲（docx、txt）")
    outline_file = st.file_uploader("上传访谈大纲文件：", type=["docx", "txt"])

    edited_result = ""

    if st.button("🚀 开始分析") and interview_file and outline_file and target.strip() != "":
        with st.spinner("⏳ 正在提取与分析内容，请稍候..."):
            transcript = extract_text(interview_file)
            outline = extract_text(outline_file)

            result_markdown = analyze_interview(transcript, outline, target)

        st.markdown("### ✅ 分析结果（可编辑）")
        edited_result = st.text_area("你可以在此修改生成的内容：", result_markdown, height=600)

        try:
            df_list = pd.read_html(edited_result, flavor="bs4")
            if df_list:
                df = df_list[0]
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                st.download_button(
                    label="📥 下载结果为 Excel",
                    data=output.getvalue(),
                    file_name="interview_analysis.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ 未能识别表格数据，请检查修改后的内容格式是否正确。")
        except Exception as e:
            st.error(f"❌ 转换结果失败：{e}")

if __name__ == "__main__":
    main()
