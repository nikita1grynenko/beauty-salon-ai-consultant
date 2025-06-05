import os
import telebot
import datetime
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from logger import log_query, get_stats, get_top_queries
from build_vectorstore import build_vector_store
from ragas_evaluator import evaluate_rag_response

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Отримуємо список ID адміністраторів і видаляємо можливі пробіли
admin_ids_raw = os.getenv("ADMIN_USER_IDS", "")
ADMIN_USER_IDS = [id.strip() for id in admin_ids_raw.split(",") if id.strip()]

# Виводимо для діагностики
print(f"Завантажені ID адміністраторів: {ADMIN_USER_IDS}")

bot = telebot.TeleBot(bot_token)

# Словник для зберігання станів користувачів у процесі оновлення прайс-листа
user_states = {}

def query_bot(user_query: str) -> tuple[str, list[str]]:
    db = Chroma(persist_directory="db", embedding_function=OpenAIEmbeddings())
    results = db.similarity_search(user_query, k=3)
    context = "\n---\n".join([doc.page_content for doc in results])
    retrieved_contexts = [doc.page_content for doc in results]

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
    return response.content, retrieved_contexts

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Вітаємо у салоні краси «ESTHEIQUE». Напишіть ваше запитання.")

@bot.message_handler(commands=['myid'])
def show_id(message):
    """Показує ID користувача та перевіряє права адміністратора"""
    user_id = str(message.from_user.id)
    is_admin = user_id in ADMIN_USER_IDS
    
    admin_status = "Ви адміністратор" if is_admin else "Ви не адміністратор"
    bot.reply_to(message, f"Ваш ID: `{user_id}`\n{admin_status}\n\nДоступні ID адміністраторів: `{ADMIN_USER_IDS}`", parse_mode="Markdown")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    """Додає нового адміністратора"""
    user_id = str(message.from_user.id)
    
    # Перевіряємо, чи користувач має права адміністратора
    if user_id not in ADMIN_USER_IDS and ADMIN_USER_IDS:  # Пропускаємо перевірку, якщо немає адміністраторів
        bot.reply_to(message, "❌ У вас немає прав для додавання адміністраторів.")
        return
    
    # Парсимо аргументи команди
    command_args = message.text.split()
    if len(command_args) != 2:
        bot.reply_to(message, "⚠️ Використання: /addadmin USER_ID\nНаприклад: `/addadmin 123456789`", parse_mode="Markdown")
        return
    
    # Додаємо нового адміністратора
    new_admin_id = command_args[1].strip()
    
    # Якщо ID вже є у списку, повідомляємо про це
    if new_admin_id in ADMIN_USER_IDS:
        bot.reply_to(message, f"⚠️ Користувач з ID {new_admin_id} вже є адміністратором.")
        return
    
    # Додаємо ID до списку
    ADMIN_USER_IDS.append(new_admin_id)
    
    # Оновлюємо файл .env
    try:
        env_file_path = ".env"
        env_lines = []
        
        # Читаємо файл
        with open(env_file_path, "r") as f:
            env_lines = f.readlines()
        
        # Оновлюємо рядок з ID адміністраторів
        updated = False
        for i, line in enumerate(env_lines):
            if line.startswith("ADMIN_USER_IDS="):
                env_lines[i] = f'ADMIN_USER_IDS="{",".join(ADMIN_USER_IDS)}"\n'
                updated = True
                break
        
        # Якщо рядка не було, додаємо
        if not updated:
            env_lines.append(f'ADMIN_USER_IDS="{",".join(ADMIN_USER_IDS)}"\n')
        
        # Записуємо оновлений файл
        with open(env_file_path, "w") as f:
            f.writelines(env_lines)
        
        bot.reply_to(message, f"✅ Користувача з ID {new_admin_id} додано до адміністраторів!")
    except Exception as e:
        print(f"Помилка при оновленні файлу .env: {e}")
        bot.reply_to(message, f"❌ Помилка при оновленні файлу .env: {e}")

@bot.message_handler(commands=['updateprice'])
def update_price_command(message):
    """Ініціює процес оновлення прайс-листа"""
    user_id = str(message.from_user.id)
    
    # Перевіряємо, чи користувач має права адміністратора
    if user_id not in ADMIN_USER_IDS:
        bot.reply_to(message, "❌ У вас немає прав для оновлення прайс-листа.")
        return
    
    # Пояснюємо користувачу, що потрібно зробити
    instructions = (
        "📝 *Оновлення прайс-листа*\n\n"
        "Будь ласка, надішліть PDF-файл з новим прайс-листом. "
        "Після завантаження я збережу його і запропоную оновити векторну базу даних.\n\n"
        "Щоб скасувати процес, напишіть /cancel"
    )
    bot.reply_to(message, instructions, parse_mode="Markdown")
    
    # Встановлюємо стан користувача
    user_states[user_id] = "waiting_for_price_pdf"

@bot.message_handler(commands=['cancel'])
def cancel_operation(message):
    """Скасовує поточну операцію користувача"""
    user_id = str(message.from_user.id)
    
    if user_id in user_states:
        del user_states[user_id]
        bot.reply_to(message, "✅ Операцію скасовано.")
    else:
        bot.reply_to(message, "ℹ️ Немає активних операцій для скасування.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Обробка надісланих документів"""
    user_id = str(message.from_user.id)
    
    # Перевіряємо, чи очікуємо PDF-файл від цього користувача
    if user_id in user_states and user_states[user_id] == "waiting_for_price_pdf":
        # Перевіряємо, чи це PDF-файл
        file_info = message.document
        if not file_info.file_name.lower().endswith('.pdf'):
            bot.reply_to(message, "❌ Будь ласка, надішліть файл у форматі PDF.")
            return
        
        # Завантажуємо файл
        file_id = file_info.file_id
        file_path = bot.get_file(file_id).file_path
        downloaded_file = bot.download_file(file_path)
        
        # Створюємо директорію для збереження файлів, якщо її не існує
        os.makedirs("data", exist_ok=True)
        
        # Шлях для збереження прайс-листа
        price_list_path = "data/Прайс Березень 2025.pdf"
        backup_path = f"data/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            # Якщо існує старий файл, робимо резервну копію
            if os.path.exists(price_list_path):
                shutil.copy2(price_list_path, backup_path)
                bot.reply_to(message, f"ℹ️ Створено резервну копію старого прайс-листа.")
            
            # Зберігаємо новий файл
            with open(price_list_path, "wb") as new_file:
                new_file.write(downloaded_file)
            
            bot.reply_to(message, "✅ Прайс-лист успішно оновлено!")
            
            # Питаємо, чи треба оновити векторну базу
            markup = telebot.types.InlineKeyboardMarkup()
            yes_button = telebot.types.InlineKeyboardButton("Так, оновити базу", callback_data="update_vectorstore")
            no_button = telebot.types.InlineKeyboardButton("Ні, залишити як є", callback_data="skip_update")
            markup.add(yes_button, no_button)
            
            bot.send_message(message.chat.id, "Бажаєте оновити векторну базу даних з новим прайс-листом?", reply_markup=markup)
            
            # Очищуємо стан користувача
            del user_states[user_id]
            
        except Exception as e:
            bot.reply_to(message, f"❌ Помилка при оновленні прайс-листа: {str(e)}")
            print(f"Помилка при оновленні прайс-листа: {e}")

@bot.callback_query_handler(func=lambda call: call.data in ["update_vectorstore", "skip_update"])
def callback_handler(call):
    """Обробка відповідей на питання про оновлення векторної бази"""
    if call.data == "update_vectorstore":
        # Повідомляємо про початок оновлення
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⏳ Оновлюю векторну базу... Це може зайняти кілька хвилин."
        )
        
        try:
            # Оновлюємо векторну базу
            build_vector_store()
            
            # Повідомляємо про успішне оновлення
            bot.send_message(call.message.chat.id, "✅ Векторна база успішно оновлена!")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Помилка при оновленні векторної бази: {str(e)}")
            print(f"Помилка при оновленні векторної бази: {e}")
    else:  # skip_update
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="ℹ️ Оновлення векторної бази пропущено. Прайс-лист оновлено."
        )

@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Показує статистику запитів (тільки для адміністраторів)"""
    user_id = str(message.from_user.id)
    
    # Перевіряємо, чи користувач має права адміністратора
    if user_id not in ADMIN_USER_IDS:
        bot.reply_to(message, f"❌ У вас немає прав для перегляду статистики. Ваш ID: {user_id}. Адмін ID: {ADMIN_USER_IDS}")
        return
    
    # Отримуємо статистику
    stats = get_stats()
    top_queries = get_top_queries(10)
    
    stats_text = f"📊 *Статистика запитів*\n\n"
    stats_text += f"Загальна кількість запитів: {stats['total_queries']}\n"
    stats_text += f"Унікальних запитів: {stats['unique_queries']}\n"
    stats_text += f"Користувачів: {stats['users']}\n\n"
    
    if top_queries:
        stats_text += "*Найпопулярніші запити:*\n"
        for i, q in enumerate(top_queries, 1):
            stats_text += f"{i}. \"{q['query']}\" - {q['count']} разів\n"
    
    bot.reply_to(message, stats_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Якщо користувач у процесі оновлення прайс-листа і написав текст
        user_id = str(message.from_user.id)
        if user_id in user_states:
            state = user_states[user_id]
            if state == "waiting_for_price_pdf":
                bot.reply_to(message, "📄 Будь ласка, надішліть PDF-файл з прайс-листом або введіть /cancel, щоб скасувати операцію.")
                return
        
        # Логуємо запит
        username = message.from_user.username or f"user_{user_id}"
        log_query(message.text, user_id=user_id, username=username)
        
        # Обробляємо запит
        answer, retrieved_contexts = query_bot(message.text)
        bot.reply_to(message, answer)
        
        # Оцінюємо відповідь за допомогою RAGAS (виводиться в консоль)
        try:
            evaluate_rag_response(message.text, answer, retrieved_contexts)
        except Exception as eval_error:
            print(f"Помилка при оцінці RAGAS: {eval_error}")
            
    except Exception as e:
        print("Помилка:", e)
        bot.reply_to(message, "Вибачте, сталася помилка. Спробуйте ще раз пізніше.")

print("Бот запущено")
bot.infinity_polling()
