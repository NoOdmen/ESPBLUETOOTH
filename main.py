from machine import Pin, PWM
import time
import math

# Используем пин 2, как в оригинальном main.py
# PWM позволяет плавно изменять яркость светодиода
led = PWM(Pin(2), freq=1000, duty=0)

def fade_in(led, duration_ms=1000, steps=100):
    """Плавно зажигает светодиод"""
    step_delay = duration_ms // steps
    for i in range(steps + 1):
        # Вычисляем яркость от 0 до 1023 (максимальная яркость для ESP32)
        brightness = int((i / steps) * 1023)
        led.duty(brightness)
        time.sleep_ms(step_delay)

def fade_out(led, duration_ms=1000, steps=100):
    """Плавно гасит светодиод"""
    step_delay = duration_ms // steps
    for i in range(steps, -1, -1):
        # Вычисляем яркость от 1023 до 0
        brightness = int((i / steps) * 1023)
        led.duty(brightness)
        time.sleep_ms(step_delay)

# Бесконечный цикл: плавно зажигаем и плавно гасим
while True:
    fade_in(led, duration_ms=1000)   # Плавно зажигаем за 1 секунду
    fade_out(led, duration_ms=1000)  # Плавно гасим за 1 секунду
    time.sleep_ms(200)                # Небольшая пауза между циклами
