
import MetaTrader5 as mt5





path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
login = 124207670
password = "abcdABCD123!@#"
server = "Exness-MT5Trial7"
timeout = 10000
portable = False
if mt5.initialize(path=path, login=login, password=password, server=server, timeout=timeout, portable=portable):
    print("Initialization successful")
else:
    print('Initialize failed')