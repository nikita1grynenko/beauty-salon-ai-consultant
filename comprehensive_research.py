import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from datetime import datetime
from dotenv import load_dotenv
from query_rag import query_bot
from ragas_evaluator import evaluate_rag_response

load_dotenv()

class ComprehensiveBeautySalonResearch:
    def __init__(self):
        self.results = []
        
        self.test_queries = [
            "Чи є знижки для нових клієнтів?",
            "Які послуги входять у догляд за обличчям?",
            "Скільки триває процедура ламінування вій?",
            "Чи потрібно записуватись заздалегідь?",
            "Які засоби ви використовуєте для чистки обличчя?",
            "Чи можна оплатити картою?",
            "Чи є у вас подарункові сертифікати?",
            "Який у вас графік роботи?",
            "Чи підходить кислотний пілінг для чутливої шкіри?",
            "Що входить у процедуру манікюру?",
            "Яка тривалість масажу спини?",
            "Чи є знижки у день народження?",
            "Чи можна поєднати декілька процедур за один візит?",
            "Який догляд рекомендуєте після пілінгу?",
            "Чи можна робити процедури вагітним?",
            "Скільки триває ефект біоревіталізації?",
            "Скільки коштує манікюр?",
            "Яка ціна педикюру?",
            "Скільки коштує піти у інфрачервону сауну?",
            "Яка ціна солярію?"
        ]

    def run_single_test(self, query, index):
        print(f"\n{'='*80}")
        print(f"🔍 Запит {index}/20: {query}")
        print('='*80)
        
        try:
            start_time = time.time()
            answer, retrieved_contexts = query_bot(query)
            response_time = time.time() - start_time
            
            print(f"💬 Відповідь: {answer}")
            print(f"⏱️ Час відповіді: {response_time:.2f} секунд")
            
            ragas_metrics = None
            ragas_time = 0
            try:
                ragas_start = time.time()
                ragas_metrics = evaluate_rag_response(query, answer, retrieved_contexts)
                ragas_time = time.time() - ragas_start
            except Exception as e:
                print(f"⚠️ Помилка RAGAS: {e}")
                ragas_metrics = {"response_relevancy": 0.0, "faithfulness": 0.0, "context_precision": 0.0}
            
            contains_apology = "На жаль" in answer or "наразі недоступна" in answer or "інформація відсутня" in answer
            has_meaningful_answer = not contains_apology and len(answer.strip()) > 20
            
            result = {
                "index": index,
                "query": query,
                "answer": answer,
                "retrieved_contexts": retrieved_contexts,
                "ragas_metrics": ragas_metrics,
                "contains_apology": contains_apology,
                "has_meaningful_answer": has_meaningful_answer,
                "answer_length": len(answer),
                "response_time": response_time,
                "ragas_time": ragas_time,
                "total_time": response_time + ragas_time,
                "timestamp": datetime.now().isoformat()
            }
            
            status = "✅ ВІДПОВІВ" if has_meaningful_answer else "❌ НЕ ВІДПОВІВ"
            print(f"📊 Результат: {status}")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
            return None

    def run_research(self):
        print("🚀 КОМПЛЕКСНЕ ДОСЛІДЖЕННЯ AI-КОНСУЛЬТАНТА САЛОНУ КРАСИ")
        print("="*90)
        print(f"📝 Всього запитів: {len(self.test_queries)}")
        print(f"🎯 Мета: Оцінити якість відповідей системи на типові запити клієнтів")
        
        total_start_time = time.time()
        
        for i, query in enumerate(self.test_queries, 1):
            self.run_single_test(query, i)
        
        total_research_time = time.time() - total_start_time
        print(f"\n⏱️ Загальний час дослідження: {total_research_time:.2f} секунд")
        
        self.analyze_results()
        self.visualize_results()

    def analyze_results(self):
        print("\n\n" + "="*90)
        print("📊 ДЕТАЛЬНИЙ АНАЛІЗ РЕЗУЛЬТАТІВ")
        print("="*90)
        
        total = len(self.results)
        answered = sum(1 for r in self.results if r["has_meaningful_answer"])
        success_rate = (answered / total) * 100 if total > 0 else 0
        
        print(f"\n📈 Загальна статистика:")
        print(f"   🔍 Всього запитів: {total}")
        print(f"   ✅ Успішних відповідей: {answered}")
        print(f"   ❌ Невдалих відповідей: {total - answered}")
        print(f"   📊 Рівень успішності: {success_rate:.1f}%")
        
        response_times = [r["response_time"] for r in self.results]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"\n⏱️ Статистика часу відповіді:")
        print(f"   🚀 Середній час: {avg_response_time:.2f} сек")
        print(f"   ⚡ Найшвидша відповідь: {min_response_time:.2f} сек")
        print(f"   🐌 Найповільніша відповідь: {max_response_time:.2f} сек")
        
        ragas_results = [r for r in self.results if r["ragas_metrics"] is not None]
        if ragas_results:
            avg_relevancy = sum(r["ragas_metrics"]["response_relevancy"] for r in ragas_results) / len(ragas_results)
            avg_faithfulness = sum(r["ragas_metrics"]["faithfulness"] for r in ragas_results) / len(ragas_results)
            avg_precision = sum(r["ragas_metrics"]["context_precision"] for r in ragas_results) / len(ragas_results)
            overall_score = (avg_relevancy + avg_faithfulness + avg_precision) / 3
            
            print(f"\n📊 Середні RAGAS метрики:")
            print(f"   🎯 Response Relevancy: {avg_relevancy:.3f}")
            print(f"   ✅ Faithfulness: {avg_faithfulness:.3f}")
            print(f"   🔍 Context Precision: {avg_precision:.3f}")
            print(f"   📈 Загальний бал: {overall_score:.3f}")
            
            if overall_score >= 0.8:
                print("   🟢 Відмінна якість відповідей!")
            elif overall_score >= 0.6:
                print("   🟡 Хороша якість відповідей")
            elif overall_score >= 0.4:
                print("   🟠 Задовільна якість відповідей")
            else:
                print("   🔴 Потребує значного покращення")
        
        print(f"\n🔍 Невдалі запити:")
        failed_queries = [r for r in self.results if not r["has_meaningful_answer"]]
        for fail in failed_queries:
            print(f"   ❌ \"{fail['query']}\" (час: {fail['response_time']:.2f}с)")
        
        filename = f"comprehensive_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результати збережено: {filename}")

    def visualize_results(self):
        print("\n📊 Створення графіків...")
        
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Результати дослідження AI-консультанта салону краси', fontsize=16, fontweight='bold')
        
        total = len(self.results)
        answered = sum(1 for r in self.results if r["has_meaningful_answer"])
        
        labels = ['Успішні відповіді', 'Невдалі відповіді']
        sizes = [answered, total - answered]
        colors = ['#4CAF50', '#F44336']
        explode = (0.05, 0)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.set_title('Загальна успішність відповідей')
        
        ragas_results = [r for r in self.results if r["ragas_metrics"] is not None and r["has_meaningful_answer"]]
        if ragas_results:
            avg_relevancy = sum(r["ragas_metrics"]["response_relevancy"] for r in ragas_results) / len(ragas_results)
            avg_faithfulness = sum(r["ragas_metrics"]["faithfulness"] for r in ragas_results) / len(ragas_results)
            avg_precision = sum(r["ragas_metrics"]["context_precision"] for r in ragas_results) / len(ragas_results)
            
            metrics = ['Response\nRelevancy', 'Faithfulness', 'Context\nPrecision']
            values = [avg_relevancy, avg_faithfulness, avg_precision]
            colors_bar = ['#2196F3', '#4CAF50', '#FF9800']
            
            bars = ax2.bar(metrics, values, color=colors_bar, alpha=0.8)
            ax2.set_title('Середні RAGAS метрики')
            ax2.set_ylabel('Оцінка (0-1)')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
            
            for bar, value in zip(bars, values):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
            
            queries = [f"Q{r['index']}" for r in ragas_results]
            overall_scores = [(r["ragas_metrics"]["response_relevancy"] + 
                             r["ragas_metrics"]["faithfulness"] + 
                             r["ragas_metrics"]["context_precision"]) / 3 for r in ragas_results]
            
            colors_scatter = ['#4CAF50' if score >= 0.7 else '#FF9800' if score >= 0.5 else '#F44336' 
                            for score in overall_scores]
            
            ax3.scatter(range(len(overall_scores)), overall_scores, c=colors_scatter, alpha=0.7, s=50)
            ax3.set_title('Загальний бал RAGAS для кожного запиту')
            ax3.set_xlabel('Номер запиту')
            ax3.set_ylabel('Середній бал RAGAS')
            ax3.set_ylim(0, 1)
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0.7, color='g', linestyle='--', alpha=0.5, label='Відмінно (0.7+)')
            ax3.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Добре (0.5+)')
            ax3.legend()
            
            response_times = [r["response_time"] for r in self.results]
            ax4.hist(response_times, bins=10, alpha=0.7, color='#9C27B0', edgecolor='black')
            ax4.set_title('Розподіл часу відповіді')
            ax4.set_xlabel('Час відповіді (секунди)')
            ax4.set_ylabel('Кількість відповідей')
            ax4.grid(True, alpha=0.3)
            
            avg_time = sum(response_times) / len(response_times)
            ax4.axvline(x=avg_time, color='red', linestyle='--', alpha=0.7, 
                       label=f'Середній час: {avg_time:.2f}с')
            ax4.legend()
        
        plt.tight_layout()
        
        chart_filename = f"research_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Графіки збережено: {chart_filename}")
        
        plt.show()
        
        self.create_detailed_metrics_chart()

    def create_detailed_metrics_chart(self):
        ragas_results = [r for r in self.results if r["ragas_metrics"] is not None and r["has_meaningful_answer"]]
        
        if not ragas_results:
            print("⚠️ Недостатньо даних для детального графіка RAGAS")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        queries = [f"Q{r['index']}" for r in ragas_results]
        relevancy = [r["ragas_metrics"]["response_relevancy"] for r in ragas_results]
        faithfulness = [r["ragas_metrics"]["faithfulness"] for r in ragas_results]
        precision = [r["ragas_metrics"]["context_precision"] for r in ragas_results]
        
        x = np.arange(len(queries))
        width = 0.25
        
        bars1 = ax1.bar(x - width, relevancy, width, label='Response Relevancy', color='#2196F3', alpha=0.8)
        bars2 = ax1.bar(x, faithfulness, width, label='Faithfulness', color='#4CAF50', alpha=0.8)
        bars3 = ax1.bar(x + width, precision, width, label='Context Precision', color='#FF9800', alpha=0.8)
        
        ax1.set_xlabel('Запити')
        ax1.set_ylabel('Оцінка RAGAS (0-1)')
        ax1.set_title('Детальні RAGAS метрики для кожного успішного запиту')
        ax1.set_xticks(x)
        ax1.set_xticklabels(queries, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        response_times = [r["response_time"] for r in self.results]
        query_indices = list(range(1, len(response_times) + 1))
        
        bars_time = ax2.bar(query_indices, response_times, color='#9C27B0', alpha=0.7)
        ax2.set_xlabel('Номер запиту')
        ax2.set_ylabel('Час відповіді (секунди)')
        ax2.set_title('Час відповіді для кожного запиту')
        ax2.grid(True, alpha=0.3)
        
        avg_time = sum(response_times) / len(response_times)
        ax2.axhline(y=avg_time, color='red', linestyle='--', alpha=0.7, 
                   label=f'Середній час: {avg_time:.2f}с')
        ax2.legend()
        
        for bar, time_val in zip(bars_time, response_times):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                    f'{time_val:.2f}с', ha='center', va='bottom', fontsize=8, rotation=90)
        
        plt.tight_layout()
        
        detailed_chart_filename = f"detailed_ragas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(detailed_chart_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Детальний графік RAGAS збережено: {detailed_chart_filename}")
        
        plt.show()

if __name__ == "__main__":
    research = ComprehensiveBeautySalonResearch()
    research.run_research() 