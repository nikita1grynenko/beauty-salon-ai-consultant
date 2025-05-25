import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from ragas.metrics import (
    ResponseRelevancy,
    Faithfulness,
    LLMContextPrecisionWithoutReference
)
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

class RAGASEvaluator:
    def __init__(self):
        self.llm = LangchainLLMWrapper(ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        ))
        self.embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        
        self.response_relevancy = ResponseRelevancy(
            llm=self.llm,
            embeddings=self.embeddings
        )
        self.faithfulness = Faithfulness(llm=self.llm)
        self.context_precision = LLMContextPrecisionWithoutReference(llm=self.llm)
    
    async def evaluate_response(
        self, 
        user_input: str, 
        response: str, 
        retrieved_contexts: List[str]
    ) -> Dict[str, float]:
        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts
        )
        
        try:
            response_relevancy_score = await self.response_relevancy.single_turn_ascore(sample)
        except Exception as e:
            print(f"Помилка при обчисленні Response Relevancy: {e}")
            response_relevancy_score = 0.0
        
        try:
            faithfulness_score = await self.faithfulness.single_turn_ascore(sample)
        except Exception as e:
            print(f"Помилка при обчисленні Faithfulness: {e}")
            faithfulness_score = 0.0
        
        try:
            context_precision_score = await self.context_precision.single_turn_ascore(sample)
        except Exception as e:
            print(f"Помилка при обчисленні Context Precision: {e}")
            context_precision_score = 0.0
        
        return {
            "response_relevancy": response_relevancy_score,
            "faithfulness": faithfulness_score,
            "context_precision": context_precision_score
        }
    
    def print_metrics(self, metrics: Dict[str, float], user_input: str):
        print("\n" + "="*60)
        print("📊 RAGAS МЕТРИКИ ОЦІНКИ ВІДПОВІДІ")
        print("="*60)
        print(f"Запит: {user_input}")
        print("-"*60)
        
        print(f"🎯 Response Relevancy: {metrics['response_relevancy']:.3f}")
        print("   (Наскільки відповідь релевантна до запиту)")
        
        print(f"✅ Faithfulness: {metrics['faithfulness']:.3f}")
        print("   (Наскільки відповідь підтверджується контекстом)")
        
        print(f"🔍 Context Precision: {metrics['context_precision']:.3f}")
        print("   (Якість отриманого контексту)")
        
        avg_score = sum(metrics.values()) / len(metrics)
        print(f"\n📈 Середній бал: {avg_score:.3f}")
        
        if avg_score >= 0.8:
            print("🟢 Відмінна якість відповіді!")
        elif avg_score >= 0.6:
            print("🟡 Хороша якість відповіді")
        elif avg_score >= 0.4:
            print("🟠 Задовільна якість відповіді")
        else:
            print("🔴 Потребує покращення")
        
        print("="*60 + "\n")

def evaluate_rag_response(user_input: str, response: str, retrieved_contexts: List[str]):
    evaluator = RAGASEvaluator()
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
        
        metrics = loop.run_until_complete(
            evaluator.evaluate_response(user_input, response, retrieved_contexts)
        )
        evaluator.print_metrics(metrics, user_input)
        return metrics
    except Exception as e:
        print(f"Помилка при оцінці RAGAS метрик: {e}")
        return None

if __name__ == "__main__":
    test_input = "Скільки коштує манікюр?"
    test_response = "Манікюр коштує 350 грн."
    test_contexts = ["Прайс-лист: Манікюр - 350 грн, Педикюр - 400 грн"]
    
    evaluate_rag_response(test_input, test_response, test_contexts) 