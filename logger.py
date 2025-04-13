import os
import json
import datetime
from collections import Counter
from typing import List, Dict, Any, Optional

# Шлях до файлу з логами
LOG_FILE = "logs/queries.json"

def ensure_log_directory():
    """Перевіряє наявність директорії для логів і створює її при необхідності"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

def log_query(query: str, user_id: Optional[str] = None, username: Optional[str] = None, source: str = "telegram"):
    """Логує запит користувача у файл JSON
    
    Args:
        query: текст запиту
        user_id: ідентифікатор користувача (опціонально)
        username: ім'я користувача (опціонально)
        source: джерело запиту (telegram, admin_panel, тощо)
    """
    ensure_log_directory()
    
    # Читаємо існуючі логи
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []
    
    # Додаємо новий запис
    logs.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "user_id": user_id,
        "username": username,
        "source": source
    })
    
    # Зберігаємо оновлені логи
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def get_top_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """Повертає найпопулярніші запити
    
    Args:
        limit: максимальна кількість запитів для повернення
        
    Returns:
        Список словників {query: str, count: int} з популярними запитами
    """
    ensure_log_directory()
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    # Рахуємо кількість запитів
    queries = [log["query"].lower() for log in logs]
    counter = Counter(queries)
    
    # Повертаємо найпопулярніші
    return [{"query": query, "count": count} 
            for query, count in counter.most_common(limit)]

def get_stats() -> Dict[str, Any]:
    """Повертає базову статистику запитів"""
    ensure_log_directory()
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"total_queries": 0, "unique_queries": 0, "users": 0}
    
    queries = [log["query"].lower() for log in logs]
    users = set(log["user_id"] for log in logs if log["user_id"])
    
    return {
        "total_queries": len(logs),
        "unique_queries": len(set(queries)),
        "users": len(users),
        "sources": dict(Counter(log["source"] for log in logs))
    }

def get_recent_queries(limit: int = 100) -> List[Dict[str, Any]]:
    """Повертає останні запити
    
    Args:
        limit: максимальна кількість запитів для повернення
        
    Returns:
        Список словників з інформацією про останні запити
    """
    ensure_log_directory()
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    # Сортуємо за часом (від найновіших до найстаріших)
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Повертаємо обмежену кількість
    return logs[:limit] 