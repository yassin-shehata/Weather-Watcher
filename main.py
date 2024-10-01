import utime
from machine import I2C, Pin
import urequests
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from neopixel import Neopixel
import random
from machine import ADC
import time
import network
import machine

ssid = 'airuc-guest'  # This should be ‘airuc-guest’ on campus Wi-Fi
# Remove password if using airuc-guest, otherwise fill in your password
password = 'YOUR WIFI PASSWORD HERE'

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid)  # Add password parameter if needed
        while not wlan.isconnected():
            pass  # Wait for connection

try:
    connect()
except KeyboardInterrupt:
    machine.reset()

if network.WLAN(network.STA_IF).isconnected():
    print('Connected. Network config:', network.WLAN(network.STA_IF).ifconfig())
else:
    print('Unable to connect. Please check your credentials or Wi-Fi availability.')









potentiometer = ADC(26)  # Physical Pin 31 or GP26
conversion_factor = 3.3 / (65535)
# LCD constants: Adjust the I2C address and pins as needed
I2C_ADDR = 0x27  # Change to your LCD's I2C address, if needed
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# LED strip configuration
LED_COUNT = 30  # Number of LED pixels.
LED_PIN = 28  # GPIO pin connected to the pixels (18 uses PWM!).

# Initialize the I2C and LCD
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Create LEDStrip object with appropriate configuration
strip = Neopixel(LED_COUNT, 0, LED_PIN, "GRB")

# API key for OpenWeatherMap: Replace with your actual API key
api_key = "e6f76b3acdf61c4afa4c58886ca61161"

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = urequests.get(url).json()
    temp_k = response['main']['temp']
    wind_speed = round(response['wind']['speed'])
    return {
        'temp_c': temp_k - 273.15,  # Kelvin to Celsius
        'wind_speed': wind_speed
    }

def display_weather(city, weather):
    lcd.clear()
    city_display = city if len(city) <= I2C_NUM_COLS else city[:I2C_NUM_COLS-3] + '...'
    lcd.move_to(0, 0)
    lcd.putstr(city_display)
    temp_str = f"T:{weather['temp_c']:.1f}C"
    wind_speed_str = f"W:{weather['wind_speed']}m/s"
    lcd.move_to(0, 1)
    lcd.putstr(f"{temp_str} {wind_speed_str}")

def set_led_color(temp_c):
    # Define your own temperature ranges and colors here
    if temp_c < 0:
        color = (0, 0, 255)  # Blue for cold
    elif 0 <= temp_c < 15:
        color = (110, 255, 255)  # Light Blue for chilly
    elif 15 <= temp_c < 23:
        color = (255, 165, 0)  # Orange for mild
    else:
        color = (255, 0, 0)  # Red for hot
    
    strip.fill(color)
    strip.show()

def turn_off_leds():
    strip.fill((0, 0, 0))
    strip.show()

def set_skydive_led_status(skydiving_open):
    if skydiving_open:
        color = (0, 255, 0)  # Green for skydiving open
    else:
        color = (255, 0, 0)  # Red for skydiving closed
    strip.fill(color)
    strip.show()

# Main program loopwhile True:
while True:
    voltage = potentiometer.read_u16() * conversion_factor  # Read potentiometer voltage

    # Map voltage to city name
    if 0.00 <= voltage < 0.38:
        city_name = "Calgary"
    elif 0.38 <= voltage < 0.54:
        city_name = "Tokyo"
    elif 0.54 <= voltage < 0.70:
        city_name = "Brooklyn"
    elif 0.70 <= voltage < 0.86:
        city_name = "London"
    elif 0.86 <= voltage < 1.02:
        city_name = "Cairo"
    elif 1.02 <= voltage < 1.18:
        city_name = "Doha"
    elif 1.18 <= voltage < 1.34:
        city_name = "Khobar"
    elif 1.34 <= voltage < 1.50:
        city_name = "Moscow"
    elif 1.50 <= voltage < 1.66:
        city_name = "Mumbai"
    elif 1.66 <= voltage < 1.82:
        city_name = "Beijing"
    elif 1.82 <= voltage < 1.98:
        city_name = "Singapore"
    elif 1.98 <= voltage < 2.14:
        city_name = "Johannesburg"
    elif 2.14 <= voltage < 2.30:
        city_name = "Brasilia"
    elif 2.30 <= voltage < 2.46:
        city_name = "Brussels"
    elif 2.46 <= voltage < 2.62:
        city_name = "Paris"
    elif 2.62 <= voltage < 2.78:
        city_name = "Bangkok"
    elif 2.78 <= voltage < 2.94:
        city_name = "Puebla"
    elif 2.94 <= voltage <= 3.3:
        city_name = "Sydney"
    else:
        city_name = "Toronto"



    lcd.clear()
    lcd.putstr(f"City: {city_name}")
    try:
        weather = get_weather(api_key, city_name)
        display_weather(city_name, weather)
        set_led_color(weather['temp_c'])  # Set the LED color based on temperature
        utime.sleep(3)  # Display the temperature color for 3 seconds
        turn_off_leds()  # Turn off the LED

        skydiving_open = weather['wind_speed'] < 5  # Assuming skydiving is open if wind speed is less than 5 m/s
        set_skydive_led_status(skydiving_open)  # Set the LED color based on skydiving status

        if skydiving_open:
            lcd.move_to(0, 1)
            lcd.putstr("Skydive Open   ")
        else:
            lcd.move_to(0, 1)
            lcd.putstr("Skydive Closed ")
    except Exception as e:
        lcd.clear()
        lcd.putstr("Error:")
        lcd.move_to(0, 1)
        lcd.putstr(str(e)[:16])

    utime.sleep(3) 




