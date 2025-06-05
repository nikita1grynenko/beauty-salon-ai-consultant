import os
import json
from datetime import datetime
from dotenv import load_dotenv
from query_rag import query_bot
from ragas_evaluator import evaluate_rag_response

load_dotenv()

class SimpleBeautySalonResearch:
    def __init__(self):
        self.results = []
        
        self.test_queries = [
            {"query": "Скільки коштує манікюр?", "expected": "present", "category": "price"},
            {"query": "Яка ціна педикюру?", "expected": "present", "category": "price"},
            {"query": "Скільки коштує фарбування вій?", "expected": "present", "category": "price"},
            {"query": "Який у вас графік роботи?", "expected": "present", "category": "info"},
            {"query": "Чи є знижки для нових клієнтів?", "expected": "present", "category": "promo"},
            {"query": "Чи можна оплатити картою?", "expected": "present", "category": "payment"},
            {"query": "Чи робите ви стрижки?", "expected": "absent", "category": "service"},
            {"query": "Скільки коштує татуаж бровей?", "expected": "absent", "category": "price"},
            {"query": "Де ви знаходитесь?", "expected": "present", "category": "contact"},
            {"query": "Який номер телефону салону?", "expected": "present", "category": "contact"}
        ]

    def run_single_test(self, test_item):
        query = test_item["query"]
        expected = test_item["expected"]
        category = test_item["category"]
        
        print(f"\n{'='*60}")
        print(f"🔍 Запит: {query}")
        print(f"📝 Очікується: {'Є інформація' if expected == 'present' else 'Немає інформації'}")
        print(f"🏷️ Категорія: {category}")
        print('='*60)
        
        try:
            answer, retrieved_contexts = query_bot(query)
            print(f"💬 Відповідь: {answer}")
            
            ragas_metrics = None
            try:
                ragas_metrics = evaluate_rag_response(query, answer, retrieved_contexts)
            except Exception as e:
                print(f"⚠️ Помилка RAGAS: {e}")
            
            contains_apology = "На жаль" in answer or "наразі недоступна" in answer
            is_correct = (expected == "present" and not contains_apology) or (expected == "absent" and contains_apology)
            
            result = {
                "query": query,
                "answer": answer,
                "retrieved_contexts": retrieved_contexts,
                "expected": expected,
                "category": category,
                "ragas_metrics": ragas_metrics,
                "contains_apology": contains_apology,
                "is_correct": is_correct,
                "timestamp": datetime.now().isoformat()
            }
            
            status = "✅ ПРАВИЛЬНО" if is_correct else "❌ НЕПРАВИЛЬНО"
            print(f"📊 Результат: {status}")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            return None

    def run_research(self):
        print("🚀 СПРОЩЕНЕ ДОСЛІДЖЕННЯ AI-КОНСУЛЬТАНТА")
        print("="*70)
        
        for i, test_item in enumerate(self.test_queries, 1):
            print(f"\n[{i}/10]")
            self.run_single_test(test_item)
        
        self.analyze_results()

    def analyze_results(self):
        print("\n\n" + "="*70)
        print("📊 АНАЛІЗ РЕЗУЛЬТАТІВ")
        print("="*70)
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r["is_correct"])
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        print(f"\n📈 Загальна точність: {correct}/{total} ({accuracy:.1f}%)")
        
        present_info_tests = [r for r in self.results if r["expected"] == "present"]
        absent_info_tests = [r for r in self.results if r["expected"] == "absent"]
        
        if present_info_tests:
            present_correct = sum(1 for r in present_info_tests if r["is_correct"])
            present_accuracy = (present_correct / len(present_info_tests)) * 100
            print(f"✅ Присутня інформація: {present_correct}/{len(present_info_tests)} ({present_accuracy:.1f}%)")
        
        if absent_info_tests:
            absent_correct = sum(1 for r in absent_info_tests if r["is_correct"])
            absent_accuracy = (absent_correct / len(absent_info_tests)) * 100
            print(f"❌ Відсутня інформація: {absent_correct}/{len(absent_info_tests)} ({absent_accuracy:.1f}%)")
        
        print("\n🔍 АНАЛІЗ ПОМИЛОК:")
        errors = [r for r in self.results if not r["is_correct"]]
        
        for error in errors:
            print(f"\n❌ Помилка в запиті: \"{error['query']}\"")
            print(f"   Очікувалося: {'Відповідь' if error['expected'] == 'present' else 'Відмова'}")
            print(f"   Отримано: {'Відмова' if error['contains_apology'] else 'Відповідь'}")
            
            if error["expected"] == "present" and error["contains_apology"]:
                print(f"   🔍 Проблема: Система не знайшла інформацію, яка є в базі")
                print(f"   💡 Контекст: {error['retrieved_contexts'][0][:100]}...")
            elif error["expected"] == "absent" and not error["contains_apology"]:
                print(f"   🔍 Проблема: Система дала відповідь на інформацію, якої немає")
        
        ragas_results = [r for r in self.results if r["ragas_metrics"] is not None]
        if ragas_results:
            avg_relevancy = sum(r["ragas_metrics"]["response_relevancy"] for r in ragas_results) / len(ragas_results)
            avg_faithfulness = sum(r["ragas_metrics"]["faithfulness"] for r in ragas_results) / len(ragas_results)
            avg_precision = sum(r["ragas_metrics"]["context_precision"] for r in ragas_results) / len(ragas_results)
            
            print(f"\n📊 RAGAS Метрики:")
            print(f"   🎯 Релевантність: {avg_relevancy:.3f}")
            print(f"   ✅ Точність: {avg_faithfulness:.3f}")
            print(f"   🔍 Якість контексту: {avg_precision:.3f}")
        
        print("\n💡 ПРИЧИНИ НЕТОЧНОСТІ СИСТЕМИ:")
        print("1. 🔍 Проблеми пошуку у векторній базі - система не знаходить релевантні документи")
        print("2. 📄 Неякісна індексація PDF - текст з прайс-листа погано розпізнається")
        print("3. 🎯 Недосконалий алгоритм similarity search - не завжди знаходить схожі тексти")
        print("4. 🤖 Занадто консервативні prompt'и - система частіше відмовляється відповідати")
        print("5. 📊 Проблеми сегментації тексту - великі блоки тексту погано обробляються")
        
        print("\n🔧 РЕКОМЕНДАЦІЇ ДЛЯ ПОКРАЩЕННЯ:")
        print("1. 📝 Покращити обробку PDF - використати кращий парсер")
        print("2. 🔄 Перебудувати векторну базу з кращими параметрами чункінгу")
        print("3. 🎯 Оптимізувати embedding модель для українського тексту")
        print("4. 📋 Додати додаткові синоніми та альтернативні назви послуг")
        print("5. 🤖 Налаштувати менш консервативні prompt'и")
        
        filename = f"simple_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результати збережено: {filename}")

if __name__ == "__main__":
    research = SimpleBeautySalonResearch()
    research.run_research() 