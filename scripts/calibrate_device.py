import pygame
import argparse
import sys
import serial
import csv
import time

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('sEMG Calibration Program')

clock = pygame.time.Clock()

# Argument parsing for serial port and baud rate
parser = argparse.ArgumentParser(description='Set port name and baud rate')
parser.add_argument('--port', type=str,
                    default=None,
                    help='Path of serial port connected to Arduino')

parser.add_argument('--baud_rate', type=int,
                    default=None,
                    help='Integer baud rate of serial port. Must match Arduino')

args = parser.parse_args()

# Variables for serial communication
data_reading_enabled = args.port is not None and args.baud_rate is not None
data_reading_active = False
serial_port = None
data_list = []

def draw_text(text, font_size, color, surface, x, y):
    font = pygame.font.SysFont(None, font_size)
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def draw_button(text, font_size, color, rect_color, rect, surface):
    pygame.draw.rect(surface, rect_color, rect)
    draw_text(text, font_size, color, surface, rect.centerx, rect.centery)

def title_screen():
    while True:
        screen.fill(WHITE)
        draw_text('sEMG Calibration Program', 50, BLACK, screen, WIDTH // 2, HEIGHT // 4)

        # Buttons
        instructions_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        begin_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

        draw_button('Instructions', 30, WHITE, BLACK, instructions_button, screen)
        draw_button('Begin Calibration', 30, WHITE, BLACK, begin_button, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if data_reading_active and serial_port:
                    serial_port.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if instructions_button.collidepoint(event.pos):
                    instructions_screen()
                elif begin_button.collidepoint(event.pos):
                    calibration_screen()

        pygame.display.flip()
        clock.tick(FPS)

def instructions_screen():
    while True:
        screen.fill(WHITE)
        draw_text('Instructions', 50, BLACK, screen, WIDTH // 2, HEIGHT // 6)

        # Display port, baud rate, and data reading status
        port_text = f'Port: {args.port}' if args.port else 'Port: None'
        baud_rate_text = f'Baud Rate: {args.baud_rate}' if args.baud_rate else 'Baud Rate: None'
        data_status = 'Yes' if data_reading_enabled else 'No'
        data_reading_text = f'Data Reading Enabled: {data_status}'

        draw_text(port_text, 30, BLACK, screen, WIDTH // 2, HEIGHT // 3)
        draw_text(baud_rate_text, 30, BLACK, screen, WIDTH // 2, HEIGHT // 3 + 40)
        draw_text(data_reading_text, 30, BLACK, screen, WIDTH // 2, HEIGHT // 3 + 80)

        # Back button
        back_button = pygame.Rect(50, 50, 100, 50)
        draw_button('Back', 30, WHITE, BLACK, back_button, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if data_reading_active and serial_port:
                    serial_port.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # Go back to the title screen

        pygame.display.flip()
        clock.tick(FPS)

def display_screen_with_circles(duration_ms, text, bg_color, text_color, num_circles, stimulus_value):
    global data_reading_active, serial_port, data_list

    start_time = pygame.time.get_ticks()
    elapsed_time = 0
    circle_interval = 1000  # 1 second in milliseconds
    circle_radius = 20
    circle_spacing = 50
    circle_positions = []

    # Calculate positions of circles
    total_width = num_circles * (2 * circle_radius + circle_spacing) - circle_spacing
    start_x = (WIDTH - total_width) // 2 + circle_radius
    y = HEIGHT // 2 + 100

    for i in range(num_circles):
        x = start_x + i * (2 * circle_radius + circle_spacing)
        circle_positions.append((x, y))

    while elapsed_time < duration_ms:
        elapsed_time = pygame.time.get_ticks() - start_time
        screen.fill(bg_color)
        draw_text(text, 80, text_color, screen, WIDTH // 2, HEIGHT // 2 - 50)

        # Update filled circles
        filled_circles = int(elapsed_time // circle_interval)

        # Draw circles
        for i in range(num_circles):
            if i < filled_circles:
                color = (0, 255, 0)  # Green
            else:
                color = WHITE
            pygame.draw.circle(screen, color, circle_positions[i], circle_radius)

        pygame.display.flip()

        # Read data from serial port if active
        if data_reading_active and serial_port:
            try:
                while serial_port.in_waiting > 0:
                    data_line = serial_port.readline().decode('utf-8').strip()
                    # Parse the data into eight floating point numbers
                    data_values = data_line.split(',')
                    if len(data_values) == 8:
                        try:
                            electrodes = [float(value) for value in data_values]
                            data_entry = {
                                'electrode_1': electrodes[0],
                                'electrode_2': electrodes[1],
                                'electrode_3': electrodes[2],
                                'electrode_4': electrodes[3],
                                'electrode_5': electrodes[4],
                                'electrode_6': electrodes[5],
                                'electrode_7': electrodes[6],
                                'electrode_8': electrodes[7],
                                'stimulus': stimulus_value
                            }
                            data_list.append(data_entry)
                        except ValueError:
                            print(f"Invalid data format: {data_line}")
                    else:
                        print(f"Incorrect number of values: {data_line}")
            except Exception as e:
                print(f"Error reading from serial port: {e}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if data_reading_active and serial_port:
                    serial_port.close()
                pygame.quit()
                sys.exit()
        clock.tick(FPS)

def calibration_screen():
    global data_reading_active, serial_port

    # Attempt to open the serial port
    if data_reading_enabled:
        try:
            serial_port = serial.Serial(args.port, args.baud_rate, timeout=1)

            # Wait for Arduino to reset
            time.sleep(2)

            # Flush input buffer to clear any existing data
            serial_port.flushInput()
            
            data_reading_active = True
            print(f"Serial port {args.port} opened at {args.baud_rate} baud.")
        except Exception as e:
            print(f"Error opening serial port: {e}")
            data_reading_active = False

    # Countdown 3...2...1...
    for i in range(3, 0, -1):
        screen.fill(WHITE)
        draw_text(str(i), 100, BLACK, screen, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1000)

    # Repeat REST and FLEX screens 10 times
    for cycle in range(2):
        # REST screen with circles, stimulus_value = 0
        display_screen_with_circles(4000, 'REST', RED, WHITE, 3, 0)

        # FLEX screen with circles, stimulus_value = 1
        display_screen_with_circles(6000, f'FLEX {cycle + 1}', BLUE, WHITE, 5, 1)

    # Close the serial port after calibration
    if data_reading_active and serial_port:
        serial_port.close()
        data_reading_active = False
        print("Serial port closed.")

    # THANK YOU screen
    thank_you_screen()

def thank_you_screen():
    while True:
        screen.fill(BLACK)
        draw_text('THANK YOU', 80, WHITE, screen, WIDTH // 2, HEIGHT // 2)

        # Finish button
        finish_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
        draw_button('Finish', 30, BLACK, WHITE, finish_button, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if data_reading_active and serial_port:
                    serial_port.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if finish_button.collidepoint(event.pos):
                    if data_reading_active and serial_port:
                        serial_port.close()
                    # Save data to CSV file
                    save_data_to_csv()
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def save_data_to_csv():
    if data_list:
        fieldnames = [
            'electrode_1', 'electrode_2', 'electrode_3', 'electrode_4',
            'electrode_5', 'electrode_6', 'electrode_7', 'electrode_8',
            'stimulus'
        ]
        filename = 'calibration_data.csv'
        try:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_list)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
    else:
        print("No data to save.")

if __name__ == '__main__':
    title_screen()
