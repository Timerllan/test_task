"""
Тест производительности сервера
"""

import time
import urllib.request
import json

URL = "http://localhost:8000"

print("="*50)
print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ СЕРВЕРА")
print("="*50)

# Проверка что сервер работает
try:
    urllib.request.urlopen(f"{URL}/get_list", timeout=2)
    print("✅ Сервер работает\n")
except:
    print("❌ Сервер не запущен! Запустите: python main.py")
    exit()

""" ТЕСТ 1: Создание записей """
print("1️⃣ Тест создания 50 записей...")
start = time.time()
for i in range(50):
    data = json.dumps({"recording": f"test_{i}"}).encode()
    req = urllib.request.Request(f"{URL}/create", data=data, method='POST')
    urllib.request.urlopen(req)
elapsed = time.time() - start
print(f"   ⏱️  {elapsed:.2f} сек на 50 записей")
print(f"   🚀 {50/elapsed:.1f} записей в секунду\n")

""" ТЕСТ 2: Получение списка """
print("2️⃣ Тест получения списка 30 раз...")
start = time.time()
for _ in range(30):
    urllib.request.urlopen(f"{URL}/get_list")
elapsed = time.time() - start
print(f"   ⏱️  {elapsed:.2f} сек на 30 запросов")
print(f"   🚀 {30/elapsed:.1f} запросов в секунду\n")

# ТЕСТ 3: Получение по ID
print("3️⃣ Тест получения по ID 50 раз...")

""" создание 5 записей """
ids = []
for i in range(5):
    data = json.dumps({"recording": f"base_{i}"}).encode()
    req = urllib.request.Request(f"{URL}/create", data=data, method='POST')
    resp = urllib.request.urlopen(req)
    ids.append(json.loads(resp.read())['id'])


start = time.time()
for i in range(50):
    id = ids[i % len(ids)]
    urllib.request.urlopen(f"{URL}/get_detail/{id}")
elapsed = time.time() - start
print(f"   ⏱️  {elapsed:.2f} сек на 50 запросов")
print(f"   🚀 {50/elapsed:.1f} запросов в секунду\n")

print("="*50)
print("✅ Тест завершён")
print("="*50)