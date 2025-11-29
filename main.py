from machine import Pin
import time
import bluetooth

led = Pin(2, Pin.OUT)
ble = bluetooth.BLE()

name = "Antoha-esp32"
payload = bytearray([
    2, 0x01, 0x06,                # flags
    len(name)+1, 0x09             # complete name
]) + name.encode()

# Флаг подключения
connected = False

# Активируем BLE
ble.active(True)

# Константы событий BLE
BLE_IRQ_CENTRAL_CONNECT = 1
BLE_IRQ_CENTRAL_DISCONNECT = 2
BLE_IRQ_GATTS_WRITE = 3

# Обработчик событий BLE (определяем ДО регистрации)
def ble_irq(event, data):
    global connected
    print(f"BLE Event: {event}")  # Отладочный вывод
    
    if event == BLE_IRQ_CENTRAL_CONNECT:
        # Устройство подключилось
        connected = True
        print("Device connected!") # Используем английский для совместимости с mpremote
        # Останавливаем рекламу при подключении
        ble.gap_advertise(None)
    elif event == BLE_IRQ_CENTRAL_DISCONNECT:
        # Устройство отключилось
        connected = False
        print("Device disconnected!")  # Используем английский для совместимости с mpremote
        # Возобновляем рекламу после отключения
        advertising_start()

# Настраиваем имя
ble.config(gap_name=name)

# Регистрируем обработчик событий ПЕРЕД созданием сервисов
ble.irq(ble_irq)

# UUID для сервиса (создаем простой сервис для возможности подключения)
SERVICE_UUID = bluetooth.UUID(0x1800)  # Generic Access Profile
CHAR_UUID = bluetooth.UUID(0x2A00)     # Device Name

# Создаем сервис и характеристику
services = (
    (
        SERVICE_UUID,
        (
            (CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_WRITE),
        ),
    ),
)
ble.gatts_register_services(services)

def advertising_start():
    ble.gap_advertise(100000, adv_data=payload)
    print("Advertising as", name)

# Запускаем рекламу
advertising_start()

# Основной цикл - мигаем светодиодом при подключении
print("Main loop started. Waiting for connection...")  # Используем английский для совместимости с mpremote
while True:
    if connected:
        # Мигаем светодиодом при подключении
        led.value(1)
        time.sleep(0.5)
        led.value(0)
        time.sleep(0.5)
    else:
        # Просто выключаем светодиод, если не подключено
        led.value(0)
        time.sleep(0.1)
