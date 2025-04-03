import os
import telebot
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(bot_token)

def query_bot(user_query: str) -> str:
    db = Chroma(persist_directory="db", embedding_function=OpenAIEmbeddings())
    results = db.similarity_search(user_query, k=3)
    context = "\n---\n".join([doc.page_content for doc in results])

    system_prompt = f"""
Ти — асистент салону краси «ESTHEIQUE». Відповідай клієнтам тільки на основі наведеного контексту.

Якщо у контексті немає точної відповіді — скажи: "На жаль, ця інформація наразі недоступна."

Контекст:
{context}
"""

    chat = ChatOpenAI(temperature=0.2, model_name="gpt-4")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    response = chat.invoke(messages)
    return response.content

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Вітаємо у салоні краси «ESTHEIQUE». Напишіть ваше запитання.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        answer = query_bot(message.text)
        bot.reply_to(message, answer)
    except Exception as e:
        print("Помилка:", e)
        bot.reply_to(message, "Вибачте, сталася помилка. Спробуйте ще раз пізніше.")

print("Бот запущено")
bot.infinity_polling()
