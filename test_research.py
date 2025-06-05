import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from query_rag import query_bot
from ragas_evaluator import evaluate_rag_response

load_dotenv()

class BeautySalonResearch:
    def __init__(self):
        self.results = []
        
        self.test_queries = [
            "Скільки коштує манікюр?",
            "Яка ціна педикюру?",
            "Скільки триває процедура ламінування вій?",
            "Чи є знижки для нових клієнтів?",
            "Який у вас графік роботи?",
            "Чи можна оплатити картою?",
            "Що входить у догляд за обличчям?",
            "Які засоби ви використовуєте для чистки обличчя?",
            "Чи є у вас подарункові сертифікати?",
            "Що входить у процедуру манікюру?",
            "Яка тривалість масажу спини?",
            "Чи є знижки у день народження?",
            "Чи можна поєднати декілька процедур за один візит?",
            "Який догляд ви рекомендуєте після пілінгу?",
            "Чи можна робити процедури вагітним?",
            "Скільки триває ефект біоревіталізації?",
            "Чи підходить кислотний пілінг для чутливої шкіри?",
            "Чи потрібно записуватись заздалегідь?",
            "Скільки коштує масаж обличчя?",
            "Яка ціна чистки обличчя?",
            "Чи робите ви брові?",
            "Скільки коштує фарбування вій?",
            "Яка вартість парафінотерапії?",
            "Чи є комплексні програми догляду?",
            "Скільки коштує консультація косметолога?"
        ]
        
        self.absent_info_queries = [
            "Чи робите ви стрижки?",
            "Скільки коштує фарбування волосся?",
            "Чи є у вас послуги перукаря?",
            "Де ви знаходитесь?",
            "Яка ваша адреса?",
            "Який номер телефону салону?",
            "Чи працюєте ви у вихідні?",
            "Скільки коштує татуаж бровей?",
            "Чи робите ви нарощування нігтів?",
            "Яка ціна лазерної епіляції?"
        ]

    def run_single_test(self, query, test_type="present"):
        print(f"\n{'='*80}")
        print(f"🔍 ТЕСТУВАННЯ: {query}")
        print(f"📝 Тип тесту: {'Інформація присутня' if test_type == 'present' else 'Інформація відсутня'}")
        print('='*80)
        
        try:
            answer, retrieved_contexts = query_bot(query)
            print(f"💬 Відповідь системи: {answer}")
            
            ragas_metrics = None
            try:
                ragas_metrics = evaluate_rag_response(query, answer, retrieved_contexts)
            except Exception as e:
                print(f"⚠️ Помилка при обчисленні RAGAS метрик: {e}")
            
            result = {
                "query": query,
                "answer": answer,
                "retrieved_contexts": retrieved_contexts,
                "test_type": test_type,
                "ragas_metrics": ragas_metrics,
                "timestamp": datetime.now().isoformat(),
                "answer_quality_assessment": self.assess_answer_quality(query, answer, test_type)
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Помилка при обробці запиту: {e}")
            return None

    def assess_answer_quality(self, query, answer, test_type):
        assessment = {
            "contains_apology": "На жаль" in answer or "наразі недоступна" in answer,
            "length": len(answer),
            "mentions_context": any(word in answer.lower() for word in ["прайс", "послуг", "салон", "grn", "грн"]),
            "appropriate_for_type": None
        }
        
        if test_type == "present":
            assessment["appropriate_for_type"] = not assessment["contains_apology"]
        else:
            assessment["appropriate_for_type"] = assessment["contains_apology"]
            
        return assessment

    def run_research(self):
        print("🚀 ПОЧАТОК ДОСЛІДЖЕННЯ СИСТЕМИ AI-КОНСУЛЬТАНТА САЛОНУ КРАСИ")
        print("="*100)
        
        print("\n📋 ТЕСТУВАННЯ ЗАПИТІВ НА ПРИСУТНЮ ІНФОРМАЦІЮ")
        print("-"*80)
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n[{i}/25] Тестую запит...")
            self.run_single_test(query, "present")
        
        print("\n\n📋 ТЕСТУВАННЯ ЗАПИТІВ НА ВІДСУТНЮ ІНФОРМАЦІЮ")
        print("-"*80)
        for i, query in enumerate(self.absent_info_queries, 1):
            print(f"\n[{i}/10] Тестую запит на відсутню інформацію...")
            self.run_single_test(query, "absent")
        
        self.save_results()
        self.generate_report()

    def save_results(self):
        filename = f"research_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результати збережено у файл: {filename}")

    def generate_report(self):
        print("\n\n" + "="*100)
        print("📊 ЗВІТ ПО ДОСЛІДЖЕННЮ")
        print("="*100)
        
        present_info_results = [r for r in self.results if r["test_type"] == "present"]
        absent_info_results = [r for r in self.results if r["test_type"] == "absent"]
        
        print(f"\n🎯 МЕТА:")
        print("Перевірити здатність системи коректно розуміти запити користувачів,")
        print("знаходити релевантну інформацію у базі знань та формувати точні, зрозумілі відповіді.")
        
        print(f"\n📋 МЕТОДОЛОГІЯ:")
        print(f"Було підготовлено набір з {len(self.test_queries)} різноманітних тестових запитів,")
        print("які охоплювали типові питання клієнтів салону: запити про вартість конкретних послуг,")
        print("тривалість процедур, наявність та умови акційних пропозицій, загальні питання про салон.")
        print("Ці запити послідовно надсилалися до діалогової системи.")
        print(f"Додатково протестовано {len(self.absent_info_queries)} запитів на інформацію,")
        print("яка свідомо була відсутня у базі знань.")
        
        print(f"\n📈 РЕЗУЛЬТАТИ:")
        
        print(f"\n1️⃣ ТЕСТУВАННЯ ПРИСУТНЬОЇ ІНФОРМАЦІЇ ({len(present_info_results)} запитів):")
        correct_answers = sum(1 for r in present_info_results 
                            if r["answer_quality_assessment"]["appropriate_for_type"])
        print(f"   ✅ Правильних відповідей: {correct_answers}/{len(present_info_results)} ({correct_answers/len(present_info_results)*100:.1f}%)")
        
        with_apology = sum(1 for r in present_info_results 
                          if r["answer_quality_assessment"]["contains_apology"])
        print(f"   ❌ Невиправдані відмови: {with_apology}/{len(present_info_results)} ({with_apology/len(present_info_results)*100:.1f}%)")
        
        print(f"\n2️⃣ ТЕСТУВАННЯ ВІДСУТНЬОЇ ІНФОРМАЦІЇ ({len(absent_info_results)} запитів):")
        correct_refusals = sum(1 for r in absent_info_results 
                              if r["answer_quality_assessment"]["appropriate_for_type"])
        print(f"   ✅ Правильних відмов: {correct_refusals}/{len(absent_info_results)} ({correct_refusals/len(absent_info_results)*100:.1f}%)")
        
        incorrect_answers = len(absent_info_results) - correct_refusals
        print(f"   ❌ Невірних відповідей: {incorrect_answers}/{len(absent_info_results)} ({incorrect_answers/len(absent_info_results)*100:.1f}%)")
        
        print(f"\n3️⃣ RAGAS МЕТРИКИ:")
        ragas_results = [r for r in self.results if r["ragas_metrics"] is not None]
        if ragas_results:
            avg_relevancy = sum(r["ragas_metrics"]["response_relevancy"] for r in ragas_results) / len(ragas_results)
            avg_faithfulness = sum(r["ragas_metrics"]["faithfulness"] for r in ragas_results) / len(ragas_results)
            avg_precision = sum(r["ragas_metrics"]["context_precision"] for r in ragas_results) / len(ragas_results)
            avg_overall = (avg_relevancy + avg_faithfulness + avg_precision) / 3
            
            print(f"   🎯 Середня релевантність відповіді: {avg_relevancy:.3f}")
            print(f"   ✅ Середня точність до контексту: {avg_faithfulness:.3f}")
            print(f"   🔍 Середня якість контексту: {avg_precision:.3f}")
            print(f"   📊 Загальна оцінка RAGAS: {avg_overall:.3f}")
            
            if avg_overall >= 0.8:
                quality_rating = "🟢 Відмінна"
            elif avg_overall >= 0.6:
                quality_rating = "🟡 Хороша"
            elif avg_overall >= 0.4:
                quality_rating = "🟠 Задовільна"
            else:
                quality_rating = "🔴 Потребує покращення"
            
            print(f"   📈 Загальна якість системи: {quality_rating}")
        
        print(f"\n4️⃣ ВИСНОВКИ:")
        overall_accuracy = (correct_answers + correct_refusals) / len(self.results) * 100
        print(f"   📊 Загальна точність системи: {overall_accuracy:.1f}%")
        
        if overall_accuracy >= 90:
            print("   🏆 Система демонструє відмінну якість роботи")
        elif overall_accuracy >= 80:
            print("   ✅ Система працює добре, є невеликі можливості для покращення")
        elif overall_accuracy >= 70:
            print("   ⚠️ Система працює задовільно, потребує оптимізації")
        else:
            print("   🔧 Система потребує значних покращень")
            
        print("\n" + "="*100)

if __name__ == "__main__":
    research = BeautySalonResearch()
    research.run_research() 