import _bootlocale  # noqa: F401
import encodings

# Fix for running: python -m unittest discover -s ./pkg -t ./ -p test_*.py
encodings.search_function('idna')
encodings.search_function('utf-16le')
encodings.search_function('utf_8_sig')
encodings.search_function('cp1252')
