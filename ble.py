from machine import Pin
import time
import bluetooth
import struct
import micropython

ble = bluetooth.BLE()

# Глобальные переменные
connected = False
conn_handle = None
advertise_payload = None
hrs_gatt_handle = None   # value handle
pox_gatt_handle = None   # value handle





def ble_init():
    global advertise_payload, hrs_gatt_handle, pox_gatt_handle

    ble_name = "ESP32"
    name_bytes = ble_name.encode()

    # --- 1. AD structure: Flags ---
    flags = bytearray([2, 0x01, 0x06])

    # --- 2. AD structure: Complete Local Name ---
    name_ad = bytearray([len(name_bytes) + 1, 0x09]) + name_bytes

    # --- 3. AD structure: Complete List of 16-bit Service UUIDs ---
    service_uuids_ad = bytearray([
        5,        # length
        0x03,     # Complete List of 16-bit Service Class UUIDs
        0x0D, 0x18,  # 0x180D (Heart Rate)
        0x22, 0x18   # 0x1822 (Pulse Oximeter)
    ])

    advertise_payload = flags + name_ad + service_uuids_ad

    # ---------- GATT сервисы ----------
    HRS_SERVICE_UUID = bluetooth.UUID(0x180D)      # Heart Rate Service
    PULSEOX_SERVICE_UUID = bluetooth.UUID(0x1822)  # Pulse Oximeter Service

    HRS_MEAS_UUID = bluetooth.UUID(0x2A37)         # Heart Rate Measurement
    PULSEOX_MEAS_UUID = bluetooth.UUID(0x2A5F)     # PLX Spot-Check Measurement

    CHAR_FLAGS = bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY

    services = (
        (HRS_SERVICE_UUID, (
            (HRS_MEAS_UUID, CHAR_FLAGS),
        )),
        (PULSEOX_SERVICE_UUID, (
            (PULSEOX_MEAS_UUID, CHAR_FLAGS),
        )),
    )

    ble.active(True)
    time.sleep_ms(50)

    # <<< ВАЖНО: распаковываем СРАЗУ в глобальные переменные
    ((hrs_gatt_handle,), (pox_gatt_handle,)) = ble.gatts_register_services(services)

    print("HRS gatt handle:", hrs_gatt_handle, "type:", type(hrs_gatt_handle))
    print("PulseOx gatt handle:", pox_gatt_handle, "type:", type(pox_gatt_handle))

    ble.config(gap_name=ble_name)
    ble.irq(ble_irq)

    print("BLE init done")

    first_conn()



def first_conn():
    # первый коннект – 60 секунд рекламы
    try_conn(60)


def try_conn(time_out_sleep=5):
    """Старт рекламы и ожидание подключения до таймаута."""
    global advertise_payload, connected

    if advertise_payload is None:
        ble_init()
        # ble_init уже вызовет first_conn, но давай сделаем проще:
        # лучше вызывать try_conn отдельно после ble_init
        # но для простоты тут считаем, что advertise_payload уже есть

    connected = False

    ble.active(True)
    ble.gap_advertise(100_000, advertise_payload)
    print("Advertise start for", time_out_sleep, "sec")

    start = time.ticks_ms()
    timeout_ms = time_out_sleep * 1000

    # Ждём либо коннекта, либо истечения таймаута
    while (not connected) and (time.ticks_diff(time.ticks_ms(), start) < timeout_ms):
        time.sleep_ms(100)

    if not connected:
        print("No connection, stop advertise & power off BLE")
        ble.gap_advertise(None)
        ble.active(False)
    else:
        print("Connected within timeout, keep BLE on (wait for data send)")
        # Выключим BLE уже ПОСЛЕ отправки данных, в DISCONNECT-обработчике



# Константы событий BLE (для информации)
BLE_IRQ_CENTRAL_CONNECT = 1
BLE_IRQ_CENTRAL_DISCONNECT = 2
BLE_IRQ_GATTS_WRITE = 3


def ble_irq(event, data):
    global connected, conn_handle

    print("BLE Event:", event)

    if event == BLE_IRQ_CENTRAL_CONNECT:
        # data = (conn_handle, addr_type, addr)
        conn_handle, addr_type, addr = data
        connected = True
        print("Device connected, handle:", conn_handle)

        # Останавливаем рекламу (это ещё более-менее ок из IRQ)
        try:
            ble.gap_advertise(None)
        except OSError as e:
            print("gap_advertise stop error:", e)

        # НИЧЕГО тяжёлого тут не делаем:
        # ни sleep, ни gatts_write/notify!
        micropython.schedule(_scheduled_send, 0)

    elif event == BLE_IRQ_CENTRAL_DISCONNECT:
        conn_handle_dis, addr_type, addr = data
        connected = False
        print("Device disconnected:", conn_handle_dis)

        # После дисконнекта – выключаем BLE для экономии
        print("Power off BLE after disconnect")
        ble.active(False)

def _scheduled_send(_):
    # сюда мы попадаем уже ВНЕ IRQ
    # можно спокойно делать gatts_write/notify
    ble_send_data(7, 12)


def ble_send_data(spo2_value = 5, hrs_value = 5):
    """Отправка данных по GATT (сперва write, потом notify)."""
    global conn_handle, connected, hrs_gatt_handle, pox_gatt_handle

    if not connected or conn_handle is None:
        print("Not connected, cannot send data")
        return

    if hrs_gatt_handle is None or pox_gatt_handle is None:
        print("ERROR: GATT handles are None")
        return

    spo2_payload = struct.pack("B", spo2_value)
    hrs_payload = struct.pack("B", hrs_value)

    try:
        ble.gatts_write(pox_gatt_handle, spo2_payload)
        ble.gatts_write(hrs_gatt_handle, hrs_payload)

        ble.gatts_notify(conn_handle, pox_gatt_handle, spo2_payload)
        ble.gatts_notify(conn_handle, hrs_gatt_handle, hrs_payload)
        print("Data sent:", spo2_value, hrs_value)
    except OSError as e:
        print("gatts_write/notify error:", e)
