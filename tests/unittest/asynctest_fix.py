import _bootlocale  # noqa: F401
import encodings
import idna  # noqa: F401

# Fix for running: python -m unittest discover -s ./pkg -t ./ -p test_*.py
encodings.search_function('idna')
encodings.search_function('utf-16le')
encodings.search_function('utf_8_sig')
encodings.search_function('cp1252')

'megotsthis.com'.encode('idna').decode('ascii')
idna.encode('megotsthis.com', uts46=True).decode('ascii')