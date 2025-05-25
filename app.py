import os
from dotenv import load_dotenv
from query_rag import query_bot
from build_vectorstore import build_vector_store
from logger import log_query, get_stats, get_top_queries
from ragas_evaluator import evaluate_rag_response

load_dotenv()


def print_stats():
    """Виводить статистику запитів на екран"""
    stats = get_stats()
    top_queries = get_top_queries(10)
    
    print("\n" + "="*50)
    print("📊 СТАТИСТИКА ЗАПИТІВ")
    print("="*50)
    print(f"Загальна кількість запитів: {stats['total_queries']}")
    print(f"Унікальних запитів: {stats['unique_queries']}")
    print(f"Користувачів: {stats['users']}")
    
    if 'sources' in stats:
        print("\nДжерела запитів:")
        for source, count in stats['sources'].items():
            print(f"  - {source}: {count}")
    
    if top_queries:
        print("\nНайпопулярніші запити:")
        for i, q in enumerate(top_queries, 1):
            print(f"{i}. \"{q['query']}\" - {q['count']} разів")
    print("="*50 + "\n")


def main():
    # Перевіряємо, чи база вже існує
    if not os.path.exists("db"):
        print("Створення векторної бази...")
        build_vector_store()

    print("\nBeauty Salon AI Consultant")
    print("Введіть ваше питання. Напишіть 'вихід' для завершення.")
    print("Напишіть 'статистика' для перегляду статистики запитів.\n")

    while True:
        user_input = input("Клієнт: ")
        
        if user_input.lower() in ["вихід", "exit"]:
            print("До зустрічі!")
            break
            
        if user_input.lower() == "статистика":
            print_stats()
            continue
            
        # Логуємо запит
        log_query(user_input, source="app")
        
        # Отримуємо відповідь та контекст
        answer, retrieved_contexts = query_bot(user_input)
        print("Бот:", answer, "\n")
        
        # Оцінюємо відповідь за допомогою RAGAS
        try:
            evaluate_rag_response(user_input, answer, retrieved_contexts)
        except Exception as e:
            print(f"Помилка при оцінці RAGAS: {e}")


if __name__ == "__main__":
    main()
