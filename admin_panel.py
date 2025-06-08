import os
import streamlit as st
import pandas as pd
import datetime
import shutil
from logger import get_stats, get_top_queries, get_recent_queries
from build_vectorstore import build_vector_store

st.set_page_config(
    page_title="Адмін-панель | Салон краси AI",
    page_icon="⚙️",
    layout="wide",
)


# Функція для аутентифікації
def authenticate():
    """Аутентифікація користувача для доступу до адмін-панелі"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 Авторизація")
    st.subheader("Вхід до адмін-панелі салону краси «ESTHEIQUE»")

    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # За замовчуванням, краще змінити у .env

    password = st.text_input("Введіть пароль адміністратора", type="password", key="admin_password")
    
    if st.button("Увійти", key="login_button"):
        if password == admin_password:
            st.session_state.authenticated = True
            st.success("✅ Успішна авторизація! Перезавантажуємо сторінку...")
            st.rerun()
        else:
            st.error("❌ Неправильний пароль. Спробуйте знову.")
            st.session_state.authenticated = False

    st.info("Ця панель призначена лише для адміністраторів салону. Якщо у вас немає пароля, зверніться до директора.")
    st.stop()  # Зупиняємо виконання до успішної авторизації


def update_price_list():
    """Сторінка оновлення прайс-листа"""
    # Додаткова перевірка авторизації
    if not st.session_state.get("authenticated", False):
        st.error("❌ Необхідна авторизація для доступу до цієї сторінки")
        st.stop()
    
    st.title("📝 Оновлення прайс-листа")
    st.write("Завантажте новий прайс-лист в форматі PDF")

    uploaded_file = st.file_uploader("Виберіть PDF-файл", type=["pdf"])
    if uploaded_file is not None:
        # Створюємо тимчасову копію поточного прайс-листа
        price_list_path = "data/Прайс Березень 2025.pdf"
        backup_path = f"data/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            # Якщо існує старий файл, робимо резервну копію
            if os.path.exists(price_list_path):
                shutil.copy2(price_list_path, backup_path)
                st.info(f"Створено резервну копію: {backup_path}")

            # Зберігаємо новий файл
            with open(price_list_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success("✅ Прайс-лист успішно оновлено!")

            # Пропонуємо оновити векторну базу
            if st.button("Оновити векторну базу даних"):
                with st.spinner("Оновлення векторної бази..."):
                    build_vector_store()
                st.success("✅ Векторну базу успішно оновлено!")
        except Exception as e:
            st.error(f"Помилка при оновленні прайс-листа: {e}")

    # Показуємо список резервних копій
    st.subheader("Резервні копії прайс-листа")
    backup_files = [f for f in os.listdir("data") if f.startswith("backup_") and f.endswith(".pdf")]

    if backup_files:
        for backup in sorted(backup_files, reverse=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {backup}")
            with col2:
                if st.button("Відновити", key=f"restore_{backup}"):
                    price_list_path = "data/Прайс Березень 2025.pdf"
                    backup_path = f"data/{backup}"
                    shutil.copy2(backup_path, price_list_path)
                    st.success(f"✅ Відновлено прайс-лист з {backup}")
                    st.rerun()
    else:
        st.info("Резервних копій не знайдено")


def view_statistics():
    """Сторінка перегляду статистики"""
    # Додаткова перевірка авторизації
    if not st.session_state.get("authenticated", False):
        st.error("❌ Необхідна авторизація для доступу до цієї сторінки")
        st.stop()
    
    st.title("📊 Статистика запитів")

    # Отримуємо базову статистику
    stats = get_stats()

    # Показуємо основні метрики
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Усього запитів", stats["total_queries"])

    with col2:
        st.metric("Унікальних запитів", stats["unique_queries"])

    with col3:
        st.metric("Користувачів", stats["users"])

    # Показуємо найпопулярніші запити
    st.subheader("Найпопулярніші запити")

    top_queries = get_top_queries(20)
    if top_queries:
        df_top = pd.DataFrame(top_queries)
        st.bar_chart(df_top.set_index("query")["count"])
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("Поки немає даних про запити")

    # Показуємо останні запити
    st.subheader("Останні запити")

    recent_queries = get_recent_queries(50)
    if recent_queries:
        df_recent = pd.DataFrame(recent_queries)
        df_recent["timestamp"] = pd.to_datetime(df_recent["timestamp"])
        df_recent = df_recent[["timestamp", "query", "username", "user_id", "source"]]
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("Поки немає даних про запити")


def main():
    # Перевіряємо авторизацію
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
        return  # Зупиняємо виконання, якщо не авторизований

    # Створюємо бічну панель навігації
    st.sidebar.title("Адмін-панель")
    st.sidebar.subheader("Салон краси «ESTHEIQUE»")
    st.sidebar.success("✅ Ви увійшли як адміністратор")

    # Навігаційне меню
    page = st.sidebar.radio(
        "Оберіть розділ:",
        ["Статистика", "Оновлення прайс-листа"]
    )

    # Кнопка виходу
    if st.sidebar.button("Вийти", key="logout_button"):
        st.session_state.authenticated = False
        st.sidebar.success("Ви вийшли з системи")
        st.rerun()

    # Відображаємо обрану сторінку
    if page == "Статистика":
        view_statistics()
    elif page == "Оновлення прайс-листа":
        update_price_list()


if __name__ == "__main__":
    # Створюємо директорії, якщо вони не існують
    os.makedirs("data", exist_ok=True)

    # Запускаємо додаток
    main()
