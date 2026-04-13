import json
import logging
from typing import Dict, Any, Optional
from config import STORAGE_FILE, ENCODING

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Ошибка валидации данных"""
    pass


class RecordStore:
    """Базовый класс для хранения записей"""

    def __init__(self, filepath: str = None):
        self.filepath = filepath or STORAGE_FILE
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Загрузка данных из файла"""
        try:
            with open(self.filepath, "r", encoding=ENCODING) as f:
                self.data = json.load(f)
                self._validate_all_records()
        except FileNotFoundError:
            logger.info(f"Storage file {self.filepath} not found, creating new")
            self.data = {}
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted storage file: {e}")
            self.data = {}

    def _validate_all_records(self) -> None:
        """Валидация всех записей при загрузке"""
        invalid_ids = []

        for record_id, record_data in self.data.items():
            if not self._is_valid_record(record_data):
                logger.warning(f"Invalid record {record_id}, removing")
                invalid_ids.append(record_id)

        for record_id in invalid_ids:
            del self.data[record_id]

        if invalid_ids:
            self._save()

    def _is_valid_record(self, record_data: Any) -> bool:
        """Проверка валидности записи"""
        if not isinstance(record_data, dict):
            return False

        if set(record_data.keys()) != {'recording'}:
            return False

        recording = record_data.get('recording')
        if not isinstance(recording, str):
            return False

        if not recording or not recording.strip():
            return False

        if len(recording) > 1000:
            return False

        return True

    def _validate_record_data(self, record_data: Any) -> None:
        """Валидация входных данных"""
        if not isinstance(record_data, dict):
            raise ValidationError("Record must be a JSON object")

        if set(record_data.keys()) != {'recording'}:
            raise ValidationError("Record must contain ONLY 'recording' field")

        recording = record_data.get('recording')

        if not isinstance(recording, str):
            raise ValidationError("Field 'recording' must be a string")

        if not recording or not recording.strip():
            raise ValidationError("Field 'recording' cannot be empty")

        if len(recording) > 1000:
            raise ValidationError("Field 'recording' max length is 1000 characters")

    def _save(self) -> None:
        """Сохранение данных в файл"""
        try:
            with open(self.filepath, "w", encoding=ENCODING) as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save: {e}")
            raise

    def _get_next_id(self) -> int:
        """Получение следующего ID"""
        if not self.data:
            return 1
        max_id = max(int(key) for key in self.data.keys())
        return max_id + 1

    def create(self, record_data: Dict) -> str:
        """Создание записи"""
        self._validate_record_data(record_data)
        record_id = str(self._get_next_id())
        self.data[record_id] = {"recording": record_data["recording"]}
        self._save()
        logger.info(f"Created record {record_id}")
        return record_id

    def get(self, record_id: str) -> Optional[Dict]:
        """Получение записи по ID"""
        if not record_id or not record_id.isdigit():
            return None
        return self.data.get(record_id)

    def get_all(self) -> Dict:
        """Получение всех записей"""
        return self.data.copy()

    def update(self, record_id: str, record_data: Dict) -> bool:
        """Обновление записи"""
        if record_id not in self.data:
            logger.warning(f"Update failed: record {record_id} not found")
            return False

        self._validate_record_data(record_data)
        self.data[record_id] = {"recording": record_data["recording"]}
        self._save()
        logger.info(f"Updated record {record_id}")
        return True

    def delete(self, record_id: str) -> bool:
        """Удаление записи"""
        if record_id not in self.data:
            logger.warning(f"Delete failed: record {record_id} not found")
            return False

        del self.data[record_id]
        self._save()
        logger.info(f"Deleted record {record_id}")
        return True

    def count(self) -> int:
        """Количество записей"""
        return len(self.data)

    def clear(self) -> None:
        """Очистка всех записей"""
        self.data.clear()
        self._save()
        logger.info("All records cleared")
