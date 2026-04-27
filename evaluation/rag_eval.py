"""
RAG 评估脚本 - 适配 RAGAS 0.4.x
"""
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import pandas as pd
load_dotenv()

async def build_eval_dataset(questions_path: str) -> list:
    """构建评估数据集，返回 ragas 0.4.x 需要的格式"""
    from langchain_openai import ChatOpenAI
    from rag.vectorstore import search_textbooks

    questions_data = json.loads(
        Path(questions_path).read_text(encoding="utf-8")
    )

    llm = ChatOpenAI(
        model="qwen-max",
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        streaming=False,
    )

    dataset = []
    for item in questions_data:
        q = item["question"]
        gt = item["ground_truth"]
        print(f"  处理: {q[:30]}...")

        # 1. 检索上下文
        docs = search_textbooks(q, k=4)
        context_texts = [d.page_content for d in docs]

        # 2. 基于检索内容生成回答
        context_str = "\n\n".join(context_texts)
        prompt = (
            f"基于以下教材内容回答问题，只使用提供的内容，不要编造。\n\n"
            f"教材内容：\n{context_str}\n\n"
            f"问题：{q}\n\n回答："
        )
        response = await llm.ainvoke(prompt)

        # ✅ RAGAS 0.4.x 的数据格式
        dataset.append({
            "user_input": q,
            "retrieved_contexts": context_texts,
            "response": response.content,
            "reference": gt,
        })

    return dataset


async def run_evaluation():
    print("=" * 50)
    print("ATLAS RAG 评估系统 (RAGAS 0.4.x)")
    print("=" * 50)

    # 1. 构建数据集
    print("\n📊 构建评估数据集...")
    data = await build_eval_dataset("evaluation/dataset.json")

    # ✅ RAGAS 0.4.x 使用 EvaluationDataset
    from ragas import EvaluationDataset, evaluate
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import LLMContextRecall, Faithfulness
    from langchain_openai import ChatOpenAI

    evaluation_dataset = EvaluationDataset.from_list(data)

    # 2. 配置评估用 LLM
    ragas_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="qwen-plus",
            openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            streaming=False,
        )
    )

    # 3. 运行评估
    print("\n🔍 运行 RAGAS 评估（需要几分钟）...")
    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            LLMContextRecall(),
            Faithfulness(),
        ],
        llm=ragas_llm,
    )

   
    # 4. 打印报告
    print("\n" + "=" * 50)
    print("📈 评估报告（基线 Baseline）")
    print("=" * 50)
    
    context_recall = result['context_recall']
    faithfulness_score = result['faithfulness']
    avg = (context_recall + faithfulness_score) / 2
    
    print(f"Context Recall : {context_recall:.3f}  （召回内容覆盖率）")
    print(f"Faithfulness   : {faithfulness_score:.3f}  （回答忠实度）")
    print(f"\n综合得分       : {avg:.3f}")
    print("=" * 50)

    # 5. 保存详细结果
    Path("evaluation").mkdir(exist_ok=True)
    df = result.to_pandas()
    df.to_csv(
        "evaluation/eval_result_baseline.csv",
        index=False, encoding="utf-8-sig"
    )
    print("\n✅ 详细结果已保存至 evaluation/eval_result_baseline.csv")
    return result


if __name__ == "__main__":
    asyncio.run(run_evaluation())