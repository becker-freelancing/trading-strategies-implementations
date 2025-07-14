import logging
import threading

from japy.japy_file_scanner import from_relative_paths
from japy.japy_server import get_japy_server_manager

# Logger konfigurieren
logger = logging.getLogger("trading-engine")
logger.setLevel(logging.DEBUG)

# Handler für Konsole (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Format definieren
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Handler dem Logger hinzufügen
logger.addHandler(console_handler)

file_scanner = from_relative_paths(["./live_prediction/classification"])

server_manager = get_japy_server_manager(file_scanner)
server_manager.start_japy_server()

try:
    while True:
        threading.Event().wait(timeout=1)
except KeyboardInterrupt:
    print("Server wird gestoppt...")
    server_manager.stop_japy_server()
    print("Server gestoppt.")
