import concurrent.futures
import sys
import time

import requests

# --- НАСТРОЙКИ ---
BASE_URL = "http://team15.kubepractice.ru"
LOGIN_URL = f"{BASE_URL}/api/user/signin"
CREATE_URL = f"{BASE_URL}/api/task/create/data/63/model/1//"
GET_ALL_URL = f"{BASE_URL}/api/task/all//"
EXECUTE_URL_TEMPLATE = "{base}/api/task/execute/{id}//"

# Учетные данные
CREDENTIALS = {
  "login": "test",
  "password": "test"
}


def login():
  """Шаг 1: Авторизация и получение токена"""
  print(f"--- 1. АВТОРИЗАЦИЯ ({CREDENTIALS['login']}) ---")
  try:
    response = requests.post(LOGIN_URL, json=CREDENTIALS)
    response.raise_for_status()
    data = response.json()

    token = data.get("access_token")
    if not token:
      print("Ошибка: Токен не пришел в ответе")
      sys.exit(1)

    print("Успешный вход. Токен получен.")

    # Формируем заголовки.
    # Судя по вашим curl, сервер требует и access_token, и Authorization
    headers = {
      'Content-Type': 'application/json',
      'access_token': token,  # Кастомный заголовок из первого примера
      'Authorization': f"Bearer {token}"
      # Стандартный заголовок из ответа (Bearer)
    }
    return headers
  except Exception as e:
    print(f"Ошибка при авторизации: {e}")
    sys.exit(1)


def create_single_task(session, headers, index):
  """Функция создания одной задачи (для многопоточности)"""
  try:
    # Используем session для переиспользования TCP соединений (быстрее)
    resp = session.post(CREATE_URL, headers=headers)
    if resp.status_code in [200, 201]:
      return True
    else:
      print(f"Ошибка создания #{index}: {resp.status_code}")
      return False
  except Exception as e:
    print(f"Исключение #{index}: {e}")
    return False


def main():
  # 1. Получаем заголовки с токеном
  headers = login()

  # Создаем сессию для оптимизации запросов
  session = requests.Session()

  # 2. Нагрузка - создание 500 задач
  print("\n--- 2. СОЗДАНИЕ 500 ЗАДАЧ (Многопоточность) ---")
  start_time = time.time()

  successful_creates = 0
  total_requests = 2000

  # Запускаем в 20 потоков для скорости
  with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(create_single_task, session, headers, i) for i in
               range(total_requests)]

    # Простой прогресс-бар
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
      if future.result():
        successful_creates += 1
      if i % 50 == 0:
        print(f"Обработано {i}/{total_requests} запросов...")

  duration = time.time() - start_time
  print(
      f"Готово! Создано: {successful_creates}/{total_requests} за {duration:.2f} сек.")

  # 3. Получение списка
  print("\n--- 3. ПОЛУЧЕНИЕ СПИСКА ЗАДАЧ ---")
  try:
    resp = session.get(GET_ALL_URL, headers=headers)
    resp.raise_for_status()
    all_tasks = resp.json()
    print(f"Всего задач в системе: {len(all_tasks)}")
  except Exception as e:
    print(f"Ошибка получения списка: {e}")
    sys.exit(1)

  # 4. Фильтрация INIT
  init_tasks = [t for t in all_tasks if t.get("status") == "init"]
  print(f"Найдено задач со статусом 'init': {len(init_tasks)}")

  if not init_tasks:
    print("Нечего выполнять.")
    return

  # 5. Запуск выполнения (Execute)
  print("\n--- 4. ЗАПУСК ВЫПОЛНЕНИЯ (EXECUTE) ---")

  def execute_single_task(task_id):
    url = EXECUTE_URL_TEMPLATE.format(base=BASE_URL, id=task_id)
    try:
      # Выполняем запрос (обычно GET или POST)
      r = session.post(url, headers=headers)
      if r.status_code == 200:
        return True
      else:
        print(f"Ошибка запуска Task {task_id}: {r.status_code}")
        return False
    except Exception as e:
      print(f"Ошибка сети Task {task_id}: {e}")
      return False

  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(execute_single_task, t['id']): t['id'] for t in
               init_tasks}

    completed_count = 0
    for future in concurrent.futures.as_completed(futures):
      if future.result():
        completed_count += 1

  print(f"Успешно отправлено на выполнение: {completed_count} задач.")


if __name__ == "__main__":
  main()
