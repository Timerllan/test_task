"""
Тестирование API сервера
Тесты только для 3 основных эндпоинтов:
1. POST /create - создание записи
2. GET /get_list - получение всех записей
3. GET /get_detail/{id} - получение записи по ID
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_create_record():
    """Тест 1: Создание записи POST /create"""
    print("\n" + "=" * 50)
    print("ТЕСТ 1: Создание записи (POST /create)")
    print("=" * 50)

    # Данные для создания
    data = {"recording": "Test audio data"}

    try:
        response = requests.post(f"{BASE_URL}/create", json=data)

        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        # Проверяем, что запрос успешен
        if response.status_code == 201:
            print("✅ ТЕСТ ПРОЙДЕН: Запись создана успешно")
            return response.json().get("id")
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН: Неправильный статус")
            return None

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return None


def test_get_all_records():
    """Тест 2: Получение всех записей GET /get_list"""
    print("\n" + "=" * 50)
    print("ТЕСТ 2: Получение всех записей (GET /get_list)")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/get_list")

        print(f"Статус ответа: {response.status_code}")
        data = response.json()
        print(f"Количество записей: {len(data)}")
        print(f"Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # Проверяем, что запрос успешен
        if response.status_code == 200:
            print("✅ ТЕСТ ПРОЙДЕН: Список записей получен")
            return data
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН: Неправильный статус")
            return None

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return None


def test_get_record_by_id(record_id):
    """Тест 3: Получение записи по ID GET /get_detail/{id}"""
    print("\n" + "=" * 50)
    print(f"ТЕСТ 3: Получение записи по ID (GET /get_detail/{record_id})")
    print("=" * 50)

    try:
        response = requests.get(f"{BASE_URL}/get_detail/{record_id}")

        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        # Проверяем, что запрос успешен
        if response.status_code == 200:
            print("✅ ТЕСТ ПРОЙДЕН: Запись получена по ID")
            return True
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН: Запись не найдена")
            return False

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "🚀" * 25)
    print("ЗАПУСК ТЕСТИРОВАНИЯ API")
    print("🚀" * 25)

    # Проверяем, запущен ли сервер
    try:
        requests.get(f"{BASE_URL}/get_list", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ОШИБКА: Сервер не запущен!")
        print("Пожалуйста, запустите сервер: python main.py")
        return

    print("\n✅ Сервер запущен, начинаем тестирование...")

    # Тест 1: Создание записи
    record_id = test_create_record()

    if record_id:
        # Тест 2: Получение всех записей
        test_get_all_records()

        # Тест 3: Получение записи по ID
        test_get_record_by_id(record_id)

        print("\n" + "🎉" * 25)
        print("ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
        print("🎉" * 25)
    else:
        print("\n" + "❌" * 25)
        print("ТЕСТЫ НЕ ВЫПОЛНЕНЫ ИЗ-ЗА ОШИБКИ СОЗДАНИЯ ЗАПИСИ")
        print("❌" * 25)


if __name__ == "__main__":
    run_all_tests()