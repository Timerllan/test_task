"""
Модуль HTTP сервера для обработки запросов к API хранилища записей.
Обеспечивает эндпоинты для создания, получения списка и получения записи по ID.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import logging
from config import ENCODING, CREATE, GET_LIST, GET_DETAIL
from storage import ValidationError


logger = logging.getLogger(__name__)


class Handler(BaseHTTPRequestHandler):
    """
    Обработчик HTTP запросов.
    Обрабатывает POST и GET запросы к API.
    """

    def __init__(self, store, *args, **kwargs):
        """
        Инициализация обработчика с хранилищем данных.

        Args:
            store: Экземпляр класса RecordStore для работы с данными
            *args: Позиционные аргументы для родительского класса
            **kwargs: Именованные аргументы для родительского класса
        """
        self.store = store  # Сохраняем ссылку на хранилище
        super().__init__(*args, **kwargs)  # Вызываем конструктор родителя

    def log_message(self, format: str, *args) -> None:
        """
        Переопределение метода логирования для использования стандартного logging.

        Args:
            format: Строка формата сообщения
            *args: Аргументы для форматирования
        """
        logger.info(f"{self.address_string()} - {format % args}")

    def _send_json(self, data, status=200):
        """
        Отправка JSON ответа клиенту.

        Args:
            data: Данные для отправки (будут преобразованы в JSON)
            status: HTTP статус код (по умолчанию 200 OK)
        """
        # Устанавливаем статус ответа
        self.send_response(status)
        # Указываем тип содержимого как JSON
        self.send_header("Content-Type", "application/json")
        # Завершаем заголовки
        self.end_headers()
        # Преобразуем данные в JSON, добавляем отступы и отправляем
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode(ENCODING))

    def _parse_body(self):
        """
        Парсинг тела HTTP запроса из JSON.

        Returns:
            dict: Распарсенные JSON данные или None при ошибке

        Обрабатывает:
            - Слишком большие запросы (>10MB)
            - Невалидный JSON
            - Другие ошибки парсинга
        """
        try:

            content_length = int(self.headers.get("Content-Length", 0))


            if content_length > 10_000_000:
                self._send_json({"error": "Payload too large"}, 413)
                return None


            body = self.rfile.read(content_length)

            return json.loads(body.decode(ENCODING))

        except json.JSONDecodeError:

            self._send_json({"error": "Invalid JSON"}, 400)
            return None
        except Exception as e:

            logger.error(f"Parse error: {e}")
            self._send_json({"error": "Bad request"}, 400)
            return None

    def do_POST(self):
        """
        Обработка POST запросов.
        Поддерживает только создание записей (POST /create).
        """

        parsed = urlparse(self.path)
        path = parsed.path


        if path == CREATE:
            # Парсим тело запроса
            data = self._parse_body()
            if data is None:
                return

            try:

                record_id = self.store.create(data)

                self._send_json({
                    "id": record_id,
                    "message": "Record created successfully"
                }, 201)  # 201 Created
            except ValidationError as e:
                # Ошибка валидации данных (неправильный формат)
                self._send_json({"error": str(e)}, 400)
            except Exception as e:

                logger.error(f"Create error: {e}")
                self._send_json({"error": "Internal server error"}, 500)
        else:
            # Путь не найден
            self._send_json({"error": "Not found"}, 404)

    def do_GET(self):
        """
        Обработка GET запросов.
        Поддерживает:
        - GET /get_list - получение всех записей
        - GET /get_detail/{id} - получение записи по ID
        """

        parsed = urlparse(self.path)
        path = parsed.path


        if path == GET_LIST:
            all_records = self.store.get_all()
            self._send_json(all_records)


        elif path.startswith(GET_DETAIL + "/"):
            # Извлекаем ID из пути (часть после последнего слеша)
            record_id = path.split("/")[-1]

            # Валидация формата ID (должно быть число)
            if not record_id or not record_id.isdigit():
                self._send_json({"error": "Invalid ID format. ID must be a number"}, 400)
                return


            record = self.store.get(record_id)
            if record is None:
                # Запись не найдена
                self._send_json({"error": f"Record with ID {record_id} not found"}, 404)
            else:

                self._send_json({record_id: record})
        else:

            self._send_json({"error": "Not found"}, 404)


def create_server(store, port):
    """
    Фабричная функция для создания и настройки HTTP сервера.

    Args:
        store: Экземпляр хранилища данных (RecordStore)
        port: Порт для прослушивания

    Returns:
        HTTPServer: Настроенный экземпляр HTTP сервера
    """

    def handler_factory(*args, **kwargs):
        """
        Фабрика обработчиков, внедряющая зависимость store.
        Позволяет передать хранилище в каждый экземпляр обработчика.

        Returns:
            Handler: Экземпляр обработчика с внедренным хранилищем
        """
        return Handler(store, *args, **kwargs)


    return HTTPServer(("", port), handler_factory)