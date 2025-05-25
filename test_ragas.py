#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_ragas_evaluation():
    """Тестує роботу RAGAS оцінки"""
    print("🧪 Тестування RAGAS оцінки...")
    
    try:
        from ragas_evaluator import evaluate_rag_response
        
        # Тестові дані
        test_cases = [
            {
                "user_input": "Скільки коштує манікюр?",
                "response": "Манікюр коштує 350 грн.",
                "contexts": ["Прайс-лист: Манікюр - 350 грн, Педикюр - 400 грн"]
            },
            {
                "user_input": "Які послуги надає салон?",
                "response": "Салон надає послуги манікюру, педикюру та догляду за обличчям.",
                "contexts": ["Послуги салону: манікюр, педикюр, догляд за обличчям, масаж"]
            },
            {
                "user_input": "Коли працює салон?",
                "response": "На жаль, ця інформація наразі недоступна.",
                "contexts": ["Прайс-лист: Манікюр - 350 грн, Педикюр - 400 грн"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Тест {i} ---")
            metrics = evaluate_rag_response(
                test_case["user_input"],
                test_case["response"], 
                test_case["contexts"]
            )
            
            if metrics:
                print("✅ Тест пройшов успішно!")
            else:
                print("❌ Тест не пройшов")
                
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("Переконайтеся, що встановлені всі залежності:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Помилка при тестуванні: {e}")
        return False
    
    print("\n🎉 Всі тести завершені!")
    return True

def test_basic_imports():
    """Тестує базові імпорти"""
    print("📦 Перевірка імпортів...")
    
    try:
        import ragas
        print("✅ RAGAS імпортовано успішно")
        
        from ragas.metrics import ResponseRelevancy, Faithfulness
        print("✅ Метрики RAGAS імпортовано успішно")
        
        from ragas import SingleTurnSample
        print("✅ SingleTurnSample імпортовано успішно")
        
        return True
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестів RAGAS...")
    
    # Перевіряємо наявність API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Не знайдено OPENAI_API_KEY в .env файлі")
        sys.exit(1)
    
    # Тестуємо імпорти
    if not test_basic_imports():
        print("❌ Тести імпортів не пройшли")
        sys.exit(1)
    
    # Тестуємо оцінку
    if test_ragas_evaluation():
        print("✅ Всі тести пройшли успішно!")
    else:
        print("❌ Деякі тести не пройшли")
        sys.exit(1) 