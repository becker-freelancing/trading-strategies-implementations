import logging

from japy.japy_file_scanner import from_relative_path
from japy.japy_server import get_japy_server_manager

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

file_scanner = from_relative_path("./functions")

server_manager = get_japy_server_manager(file_scanner)

server_manager.start_japy_server()
