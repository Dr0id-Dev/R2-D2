import RPi.GPIO as GPIO          # For controlling Raspberry Pi GPIO pins
import time                      # For adding delays and timing functions
import pyvesc                    # For communicating with the VESC motor controller
import serial                    # For serial communication with the VESC
import logging                   # For logging functionality
from datetime import datetime    # For timestamps in logs
import os                        # For file and directory operations
import board                     # Part of CircuitPython, for hardware interfacing
import displayio                 # For controlling the display
import terminalio                # For display fonts
from adafruit_display_text import label  # For displaying text on the screen
import adafruit_st7789           # For controlling the specific ST7789 display
from PIL import Image, ImageDraw, ImageFont  # For image processing
import textwrap                  # For wrapping text on the display

class DisplayController:
    def __init__(self):
        # Release any resources currently in use for the displays
        displayio.release_displays()
        
        # Setup SPI
        spi = board.SPI()
        tft_cs = board.CE0
        tft_dc = board.D25
        
        # Display setup
        display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
        self.display = adafruit_st7789.ST7789(
            display_bus, 
            width=280, 
            height=240,
            rotation=180  # Adjust if needed based on your mount
        )
        
        # Create main display group
        self.main_group = displayio.Group()
        self.display.show(self.main_group)
        
        # Setup colors
        self.colors = {
            'RED': 0xFF0000,
            'WHITE': 0xFFFFFF,
            'BLACK': 0x000000,
            'YELLOW': 0xFFFF00
        }
        
    def show_message(self, message, color=0xFFFFFF):
        # Clear previous content
        while len(self.main_group) > 0:
            self.main_group.pop()
            
        # Create text area for large text
        text_area = label.Label(
            terminalio.FONT,
            text=message,
            color=color,
            scale=3,  # Make text larger
            anchor_point=(0.5, 0.5),
            anchored_position=(140, 120)  # Center of 280x240 display
        )
        
        self.main_group.append(text_area)
        
    def show_code_scroll(self, code_text):
        # Wrap text to fit display width
        wrapped_text = textwrap.fill(code_text, width=30)
        lines = wrapped_text.split('\n')
        
        # Show each line with small scrolling delay
        for i in range(len(lines)):
            text_area = label.Label(
                terminalio.FONT,
                text='\n'.join(lines[max(0, i-7):i+1]),  # Show 8 lines at a time
                color=self.colors['WHITE'],
                scale=1,
                anchor_point=(0, 0),
                anchored_position=(10, 10)
            )
            
            while len(self.main_group) > 0:
                self.main_group.pop()
                
            self.main_group.append(text_area)
            time.sleep(0.5)  # Scroll delay

class RobotController:
    def __init__(self):
        # GPIO setup for ultrasonic sensor
        self.TRIG = 23  # GPIO pin for trigger
        self.ECHO = 24  # GPIO pin for echo
        
        # Serial setup for VESC
        self.serial_port = '/dev/ttyACM0'  # Typical port for VESC
        self.vesc = None
        
        # Initialize display
        self.display = DisplayController()
        
        # Setup logging
        self.setup_logging()
        
        # Show boot sequence
        self.show_boot_sequence()
        
        self.setup_gpio()
        self.setup_vesc()
        
    def show_boot_sequence(self):
        # Show running code
        with open(__file__, 'r') as file:
            self.display.show_code_scroll(file.read())
            
        # Show exact system check messages with appropriate colors
        sys_checks = [
            ('SYS CHECK INFO', self.display.colors['WHITE']),
            ('SYS CHECK WARNING', self.display.colors['YELLOW']),
            ('SYS CHECK ERROR', self.display.colors['RED'])
        ]
        
        for status, color in sys_checks:
            self.display.show_message(status, color)
            time.sleep(1)
            
    def setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/robot_log_{timestamp}.log'
        
        class DisplayHandler(logging.Handler):
            def __init__(self, display_controller):
                super().__init__()
                self.display = display_controller
                
            def emit(self, record):
                # Show different log levels on display with appropriate colors
                if record.levelname in ['INFO', 'WARNING', 'ERROR']:
                    color = {
                        'INFO': self.display.colors['WHITE'],
                        'WARNING': self.display.colors['YELLOW'],
                        'ERROR': self.display.colors['RED']
                    }.get(record.levelname, self.display.colors['WHITE'])
                    
                    self.display.show_message(record.levelname, color)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
                DisplayHandler(self.display)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Robot controller initialized')
        
    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        
        GPIO.output(self.TRIG, False)
        time.sleep(2)  # Let sensor settle
        self.logger.info('GPIO setup completed')
        
    def setup_vesc(self):
        try:
            self.vesc = serial.Serial(self.serial_port, baudrate=115200, timeout=0.05)
            self.logger.info('VESC connection established')
        except serial.SerialException as e:
            self.logger.error(f"Error connecting to VESC: {e}")
            
    def get_distance(self):
        try:
            GPIO.output(self.TRIG, True)
            time.sleep(0.00001)
            GPIO.output(self.TRIG, False)
            
            pulse_start = time.time()
            pulse_end = time.time()
            timeout_start = time.time()
            
            while GPIO.input(self.ECHO) == 0:
                pulse_start = time.time()
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    self.logger.warning("Timeout waiting for echo start")
                    return None
                    
            while GPIO.input(self.ECHO) == 1:
                pulse_end = time.time()
                if time.time() - timeout_start > 0.1:  # 100ms timeout
                    self.logger.warning("Timeout waiting for echo end")
                    return None
                    
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound * time / 2
            distance = round(distance, 2)
            
            if distance > 4000:  # More than 4 meters
                self.logger.warning(f"Unusually large distance reading: {distance}mm")
            elif distance < 2:  # Less than 2mm
                self.logger.warning(f"Unusually small distance reading: {distance}mm")
            else:
                self.logger.debug(f"Distance reading: {distance}mm")
                
            return distance
            
        except Exception as e:
            self.logger.error(f"Error getting distance reading: {e}")
            return None
        
    def stop_robot(self):
        if self.vesc:
            try:
                pyvesc.SetDutyCycle(0).write(self.vesc)  # Set duty cycle to 0 to stop
                self.logger.info("Stop command sent to VESC")
            except Exception as e:
                self.logger.error(f"Error sending stop command to VESC: {e}")
                
    def cleanup(self):
        GPIO.cleanup()
        if self.vesc:
            self.vesc.close()
        self.logger.info("Robot controller shutdown complete")
            
    def monitor_distance(self):
        try:
            self.logger.info("Starting distance monitoring")
            consecutive_errors = 0
            
            while True:
                distance = self.get_distance()
                
                if distance is None:
                    consecutive_errors += 1
                    self.logger.warning(f"Failed reading - consecutive errors: {consecutive_errors}")
                    if consecutive_errors >= 5:
                        self.logger.error("Too many consecutive sensor errors - stopping robot")
                        self.stop_robot()
                        break
                else:
                    consecutive_errors = 0
                    
                    if distance <= 20:  # If obstacle is within 20mm
                        self.logger.warning(f"Obstacle detected at {distance}mm - stopping robot")
                        self.stop_robot()
                    
                time.sleep(0.1)  # Small delay between readings
                
        except KeyboardInterrupt:
            self.logger.info("Program stopped by user")
            self.cleanup()
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.cleanup()

if __name__ == "__main__":
    robot = RobotController()
    robot.monitor_distance()
