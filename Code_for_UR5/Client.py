from pymodbus.client import ModbusTcpClient
HOST = "192.168.1.184"
PORT = 502


with ModbusTcpClient(host=HOST, port=PORT) as client:
    client.connect()
    result = client.read_holding_registers(address=1, count=2, slave=255)
    print(result.registers[0])