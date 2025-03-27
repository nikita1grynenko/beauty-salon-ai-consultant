import os
from dotenv import load_dotenv
from query_rag import query_bot
from build_vectorstore import build_vector_store

load_dotenv()


def main():
    # Перевіряємо, чи база вже існує
    if not os.path.exists("db"):
        print("Створення векторної бази...")
        build_vector_store()

    print("\nBeauty Salon AI Consultant")
    print("Введіть ваше питання. Напишіть 'вихід' для завершення.\n")

    while True:
        user_input = input("Клієнт: ")
        if user_input.lower() in ["вихід", "exit"]:
            print("До зустрічі!")
            break
        answer = query_bot(user_input)
        print("Бот:", answer, "\n")


if __name__ == "__main__":
    main()
