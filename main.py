import sys
import signal
import logging
from typing import Optional
from storage import RecordStore, ValidationError
from server import create_server
from config import PORT, STORAGE_FILE, CREATE, GET_LIST, GET_DETAIL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Application:
    """Класс приложения для управления жизненным циклом"""

    def __init__(self):
        self.server = None
        self.store: Optional[RecordStore] = None

    def _setup_signal_handlers(self) -> None:
        """Настройка обработчиков сигналов для корректного завершения"""
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, signum=None, frame=None) -> None:
        """Корректное завершение работы сервера"""
        logger.info("Shutting down gracefully...")

        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Server stopped")

        sys.exit(0)

    def _print_banner(self) -> None:
        """Вывод информационного баннера"""

        detail_path = f"{GET_DETAIL}/{{id}}"

        banner = f"""
    ╔══════════════════════════════════════════════════════╗
    ║           RECORD STORAGE API SERVER                  ║
    ╠══════════════════════════════════════════════════════╣
    ║  Port:      {PORT:<47}║
    ║  Storage:   {STORAGE_FILE:<47}║
    ╠══════════════════════════════════════════════════════╣
    ║  Endpoints:                                          ║
    ║    POST   {CREATE:<44}║
    ║    GET    {GET_LIST:<44}║
    ║    GET    {detail_path:<44}║
    ╚══════════════════════════════════════════════════════╝
        """
        print(banner)

    def initialize(self) -> bool:
        """Инициализация приложения"""
        try:
            logger.info("Initializing application...")
            self.store = RecordStore(STORAGE_FILE)
            logger.info(f"Loaded {self.store.count()} records from storage")
            return True
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    def run(self) -> None:
        """Запуск приложения"""
        if not self.initialize():
            logger.error("Failed to initialize application")
            sys.exit(1)

        self._setup_signal_handlers()
        self._print_banner()

        try:
            self.server = create_server(self.store, PORT)
            logger.info(f"Server started on http://localhost:{PORT}")
            self.server.serve_forever()
        except OSError as e:
            logger.error(f"Failed to start server on port {PORT}: {e}")
            logger.info(f"Check if port {PORT} is already in use")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)


def main() -> None:
    """Главная функция"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
