import random

import pygame
from tkinter import messagebox
from net import Network
import time
import requests

current_file = open('client.py').read()
if not current_file == requests.get('https://raw.githubusercontent.com/mabdullahprogrammer/UNO/refs/heads/main/client.py').content:
    print('Update Needed')
    exit()



width, height = 1340, 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('UNO Game')
pygame.init()


class Timer:
    def __init__(self, duration):
        self.duration = duration  # Total time in seconds
        self.start_time = time.time()  # Record the start time

    def reset(self):
        """Reset the timer."""
        self.start_time = time.time()

    def get_time_left(self):
        """Calculate the remaining time."""
        elapsed_time = time.time() - self.start_time
        return max(0, self.duration - elapsed_time)

    def draw(self, win, x, y):
        """Draw the timer on the screen."""
        font = pygame.font.SysFont('Arial', 30)
        time_left = self.get_time_left()
        timer_text = font.render(f'Time left: {int(time_left)}s', True, (255, 255, 255))
        win.blit(timer_text, (x, y))
class CircularButton:
    def __init__(self, center, radius, color, text):
        self.center = center
        self.radius = radius
        self.color = color
        self.text = text
        self.enabled = True  # Button is enabled by default
        self.font = pygame.font.SysFont('Arial', 24)
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))

    def draw(self, screen):
        # Draw the button in a different color if it's disabled
        button_color = (100, 100, 100) if not self.enabled else self.color
        pygame.draw.circle(screen, button_color, self.center, self.radius)

        # Draw text only if the button is enabled
        if self.enabled:
            text_rect = self.text_surface.get_rect(center=self.center)
            screen.blit(self.text_surface, text_rect)

    def is_clicked(self, pos):
        # Only check for clicks if the button is enabled
        if not self.enabled:
            return False

        distance = ((pos[0] - self.center[0]) ** 2 + (pos[1] - self.center[1]) ** 2) ** 0.5
        return distance <= self.radius

    def set_enabled(self, enabled):
        self.enabled = enabled
class Cards:
    def __init__(self, x, y, img_path, c_name):
        self.x = x
        self.y = y
        self.card = c_name
        self.img = pygame.image.load(img_path)
        self.width, self.height = self.img.get_width(), self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Create a rect for boundary detection

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def click(self, pos):
        x1, y1 = pos
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        return False


TIMER_BAR_LENGTH = 400  # Initial length of the timer bar
TIMER_BAR_HEIGHT = 20  # Height of the timer bar
TIME_LIMIT = 5  # Time limit in seconds


# Draw a horizontal timer bar below the score
def draw_timer_bar(surface, elapsed_time, total_time, position, length, height):
    # Calculate the percentage of time left
    time_left_percentage = max((total_time - elapsed_time) / total_time, 0)

    # Determine the current width of the bar based on time left
    current_width = int(length * time_left_percentage)

    # Calculate the color transition from green to red
    r = int(255 * (1 - time_left_percentage))  # Increase red component as time decreases
    g = int(255 * time_left_percentage)  # Decrease green component as time decreases
    b = 0  # Blue component remains constant

    # Draw the depleted portion in gray
    depleted_rect = pygame.Rect(position[0] + current_width, position[1], length - current_width, height)
    pygame.draw.rect(surface, (128, 128, 128), depleted_rect)

    # Draw the remaining time with the changing color
    timer_rect = pygame.Rect(position[0], position[1], current_width, height)
    pygame.draw.rect(surface, (r, g, b), timer_rect)

def draw(win, x, y, img):
    img = pygame.image.load(img)
    win.blit(img, (x, y))

def draw_rounded_rect(surface, rect, color, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

# Function to display a semi-transparent pop-up window
def wild_draw_4_popup():
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a transparent overlay
    overlay.fill((0, 0, 0, 150))  # Black overlay with some transparency
    win.blit(overlay, (0, 0))

    # Draw rounded rectangle box for popup
    popup_rect = pygame.Rect(400, 200, 540, 300)
    draw_rounded_rect(win, popup_rect, (255, 255, 255), 20)

    # Render buttons with text
    font = pygame.font.SysFont('Arial', 40)
    challenge_button = pygame.Rect(450, 300, 200, 80)
    draw_card_button = pygame.Rect(700, 300, 200, 80)

    draw_rounded_rect(win, challenge_button, (100, 200, 100), 10)  # Green button for "Challenge"
    draw_rounded_rect(win, draw_card_button, (200, 100, 100), 10)  # Red button for "Draw Card (x4)"

    # Draw text on buttons
    challenge_text = font.render("Challenge", True, (255, 255, 255))
    draw_card_text = font.render("Draw Card (x4)", True, (255, 255, 255))
    win.blit(challenge_text, (challenge_button.x + 30, challenge_button.y + 20))
    win.blit(draw_card_text, (draw_card_button.x + 30, draw_card_button.y + 20))

    pygame.display.update()
    return challenge_button, draw_card_button

# Function to handle the "Draw 4" popup
def handle_draw_four_popup():
    challenge_button, draw_card_button = wild_draw_4_popup()
    action = None

    # Handle user interaction for "Draw 4" actions
    while action is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if challenge_button.collidepoint(pos):
                    action = "challenge"
                elif draw_card_button.collidepoint(pos):
                    action = "draw"

    return action

def draw_card(cname):
    # Create a transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Black overlay with some transparency
    win.blit(overlay, (0, 0))

    # Draw rounded rectangle box for popup
    popup_rect = pygame.Rect(400, 200, 540, 400)  # Adjusted height to make space for image
    draw_rounded_rect(win, popup_rect, (255, 255, 255), 20)

    # Load and display the card image above the buttons
    try:
        card_image = pygame.image.load(f'images/{cname}.png')
        card_image = pygame.transform.scale(card_image, (150, 225))  # Resize the card image as needed
        win.blit(card_image, (popup_rect.x + popup_rect.width // 2 - 75, popup_rect.y + 20))  # Center the image
    except pygame.error:
        print(f"Error: Could not load image for {cname}.png")  # In case the image does not load correctly

    # Render buttons with text
    font = pygame.font.SysFont('Arial', 40)
    draw_button = pygame.Rect(450, 450, 200, 80)  # Adjust y-position to be below card image
    cancel_card_button = pygame.Rect(700, 450, 200, 80)

    draw_rounded_rect(win, draw_button, (100, 200, 100), 10)  # Green button for "Play"
    draw_rounded_rect(win, cancel_card_button, (200, 100, 100), 10)  # Red button for "Cancel"

    # Draw text on buttons
    draw_text = font.render("Play", True, (255, 255, 255))
    cancel_card_text = font.render("Cancel", True, (255, 255, 255))
    win.blit(draw_text, (draw_button.x + 50, draw_button.y + 20))  # Adjusted text position
    win.blit(cancel_card_text, (cancel_card_button.x + 30, cancel_card_button.y + 20))

    pygame.display.update()
    return draw_button, cancel_card_button
def handle_draw_card(cname):
    draw_button, Cancel_card_button = draw_card(cname)
    action = None

    # Handle user interaction for "Draw 4" actions
    while action is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if draw_button.collidepoint(pos):
                    action = "play"
                elif Cancel_card_button.collidepoint(pos):
                    action = "cancel"

    return action

def wild_card_color_selection():
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a transparent overlay
    overlay.fill((0, 0, 0, 150))  # Black overlay with some transparency
    win.blit(overlay, (0, 0))

    # Draw rounded rectangle box for popup
    popup_rect = pygame.Rect(500, 200, 340, 300)
    draw_rounded_rect(win, popup_rect, (255, 255, 255), 20)

    # Render color selection options
    colors = ['Red', 'Green', 'Blue', 'Yellow']
    color_rects = {}
    for i, color in enumerate(colors):
        color_rect = pygame.Rect(550, 240 + i * 60, 240, 40)
        color_rects[color] = color_rect
        color_rgb = (255, 0, 0) if color == 'Red' else (0, 255, 0) if color == 'Green' else (0, 0, 255) if color == 'Blue' else (255, 255, 0)
        draw_rounded_rect(win, color_rect, color_rgb, 10)

        # Draw text on color options
        font = pygame.font.SysFont('Arial', 30)
        color_text = font.render(color.capitalize(), True, (0, 0, 0))
        win.blit(color_text, (color_rect.x + 80, color_rect.y + 5))

    pygame.display.update()
    return color_rects

# Function to handle the color selection popup
def handle_color_selection():
    selected_color = None
    color_rects = wild_card_color_selection()

    # Handle user interaction for color selection
    while selected_color is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for color, rect in color_rects.items():
                    if rect.collidepoint(pos):
                        selected_color = color
                        break

    return selected_color

def redrawWin(win, game, player, e_time):
    win.fill((128, 128, 128))  # Fill the background with a gray color
    bts = []
    deck = game.deck
    card_spacing = 55  # Space between each card

    player_positions = {
        "bottom": (250, height - 200),
        "top": (300, 50),
        "left": (50, 200),  # x-coordinate for left player
        "right": (width - 640, 200)  # x-coordinate for right player
    }

    # Mapping player positions based on player index
    if player == 0:
        position_mapping = {
            "0": "bottom", "1": "left", "2": "top", "3": "right"
        }
    elif player == 1:
        position_mapping = {
            "1": "bottom", "2": "left", "3": "top", "0": "right"
        }
    elif player == 2:
        position_mapping = {
            "2": "bottom", "3": "left", "0": "top", "1": "right"
        }
    else:
        position_mapping = {
            "3": "bottom", "0": "left", "1": "top", "2": "right"
        }
    if player == 0 and game.total_player == 2:
        position_mapping = {
            "0": "bottom", "2": "left", "1": "top", "3": "right"
        }
    elif player == 1 and game.total_player == 2:
        position_mapping = {
            "1": "bottom", "2": "left", "0": "top", "3": "right"
        }

    font = pygame.font.SysFont('Airal', 90)
    if player == game.turn:

        text = font.render('Your Turn', 1, (255, 40, 10), (128, 128, 128))
        win.blit(text, (900, 300))
    text = font.render(f'{game.points[player]} Points|{player}', 1, (255, 255, 255), (128, 128, 128))
    win.blit(text, (900, 400))

    # Draw the timer bar below the score
    timer_bar_position = (850, 500)  # Position of the timer bar
    draw_timer_bar(win, e_time, TIME_LIMIT, timer_bar_position, TIMER_BAR_LENGTH, TIMER_BAR_HEIGHT)

    for p_index, player_cards in deck.items():
        position = position_mapping.get(str(p_index))
        if not position:
            continue
        x, y = player_positions[position]
        face_down = position != "bottom"

        for i, card in enumerate(player_cards):
            card_img = 'images/back.png' if face_down else f'images/{card}.png'

            if position in ["left", "right"]:
                card_x = x  # Keep the x coordinate constant for left and right players
                card_y = y + i * card_spacing/2  # Adjust the y coordinate for vertical stacking
                # Load and rotate the card image
                card_surface = pygame.image.load(card_img)
                rotated_card = pygame.transform.rotate(card_surface, -90 if position == 'left' else 90)
                # Adjust the position to center the rotated card
                rotated_x = card_x + (card_surface.get_height() - rotated_card.get_height()) // 2
                rotated_y = card_y + (card_surface.get_width() - rotated_card.get_width()) // 2
                win.blit(rotated_card, (rotated_x, rotated_y))  # Draw the rotated card
            else:
                row = i //7
                col = i % 7
                # Calculate x and y positions
                card_x = x + col * card_spacing  # x-position shifts for each column in the row
                card_y = y + row * 100  # y-position shifts for each new row
                print("i: "+str(i))
                print("x: " + str(card_x))
                print("y: " + str(card_y))
                if face_down:
                    card_x = x + i * card_spacing/2
                    card_y = y
                    draw(win, card_x, card_y, card_img)  # Draw back of the card if face-down
                else:
                    card_obj = Cards(card_x, card_y, card_img, card)
                    bts.append(card_obj)
                    card_obj.draw(win)
    if game.sequence == -1:
        draw(win, 290, 230, 'images/Right_Moving1.png')
        draw(win, 430, 250, 'images/Right_Moving2.png')
    else:
        draw(win, 300, 255, 'images/Reverse_Moving1.png')
        draw(win, 430, 240, 'images/Reverse_Moving2.png')

    top_card_img = f"images/Wild_{game.top_card['color']}.png" if 'Wild' in game.top_card[
        'name'] else f"images/{game.top_card['name']}.png"
    draw(win, 400, 300, top_card_img)  # Draw the top card in the discard pile
    pygame.display.update()
    return bts


def main():
    running = True
    clock = pygame.time.Clock()
    network = Network()
    player = int(network.getP())
    print(f"Its Player {player}")
    uno_button = CircularButton(center=(100, 200), radius=50, color=(255, 0, 0), text="Yell UNO!")
    try:
        game = network.send("get")
        if game is None:
            raise Exception("Game data received is None.")
    except Exception as e:
        print(f"Couldn't get game..Quitting: {e}")
        pygame.quit()
        return
    bts = []
    for p_index, player_cards in game.deck.items():
        for i, card in enumerate(player_cards):
            card_img = f'images/{card}.png'
            if card in game.deck[f'{player}']:
                # Calculate the Y position correctly for drawing the cards
                card_y = height - 150  # or some other logic based on your game design
                bts.append(Cards(500 + i * 50, card_y, card_img, card))
    elapsed_time = 0
    last_turn = None
    while running:
        clock.tick(60)
        try:
            game = network.send("get")
            if game is None:
                raise Exception("Game data received is None.")
        except Exception as e:
            print(f"Couldn't get game: {e}")
            break

        if game.checkWin() == player and game.checkWin():
            font = pygame.font.SysFont('Agency FB', 90)
            text = font.render('You WON!', 1, (0, 255, 0))
            win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
            pygame.display.update()
            pygame.time.delay(5000)
            print("Winner Found!")
            break
        elif game.checkWin():
            font = pygame.font.SysFont('Agency FB', 90)
            text = font.render('You Lost', 1, (255, 0, 0))
            win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
            pygame.display.update()
            pygame.time.delay(5000)
            print("Winner Found!")
            break

        # Check if it's a new turn
        if last_turn != game.turn:
            last_turn = game.turn
            elapsed_time = 0  # Reset the timer when a new turn starts

        # Update elapsed time
        if player == game.turn:
            elapsed_time += 1 / 60  # Assuming clock.tick(60), increment elapsed_time in seconds

        # Check if time runs out
        if elapsed_time >= TIME_LIMIT and player == game.turn:
            actions = game.get_moves()
            if 'Draw_Four' in game.top_card['name']:
                action = random.choice(actions)
                game.play(action)
                r = network.get('game')
                if r == 'get-game':
                    network.send_pickle(game)
            elif actions != 'draw_card':
                color = None
                action=random.choice(actions)
                if 'Wild' in action:
                    color = random.choice(['Red', 'Green', 'Blue', 'Yellow'])
                game.play(action, wild_color=color)  # Automatically play 'draw_card'
                font = pygame.font.SysFont('Agency FB', 60, True)
                text = font.render(f'''Your Turn Was Played by Bot.
Action: {action} {f"Color: {color}" if "wild" in action.lower() else ""}''', 1, (40, 40, 40))
                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                pygame.display.update()
                pygame.time.delay(1000)
                r = network.get('game')
                if r == 'get-game':
                    network.send_pickle(game)
            else:
                game.draw_card()
                game.play('draw_card')
                r = network.get('game')
                if r == 'get-game':
                    network.send_pickle(game)
            elapsed_time = 0  # Reset the timer

        if player == game.turn:
            uno_button.set_enabled(True)
        else:
            uno_button.set_enabled(False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(f"Mouse clicked at position: {pos}")
                if uno_button.is_clicked(event.pos):
                    try:
                        game.yell_uno()
                    except Exception as e:
                        messagebox.showwarning('UNO', f"{e}")
                    else:
                        network.send('game')
                        network.send_pickle(game)
                for b in bts:
                    if b.click(pos):
                        print('Played')
                        if game.turn == player:
                            if 'wild_draw_four' in game.top_card['name'].lower() and not game.wild_moved:
                                action = handle_draw_four_popup()
                                try:
                                    game.play(action)
                                    r = network.get('game')
                                    if r == 'get-game':
                                        print('Game send')
                                        network.send_pickle(game)
                                except Exception as e:
                                    messagebox.showwarning('UNO', f'{e}')
                            elif game.can_play():
                                if b.card.startswith('Wild'):
                                    selected_color = handle_color_selection()  # Get the color selected by the player
                                    if selected_color:
                                        try:
                                            game.play(b.card, wild_color=selected_color)
                                            r = network.get('game')
                                            if r == 'get-game':
                                                print('Game send')
                                                network.send_pickle(game)
                                        except Exception as e:
                                            messagebox.showwarning('UNO', f'{e}')
                                else:
                                    print('Player Turn Can play')
                                    try:
                                        game.play(b.card)
                                        r = network.get('game')
                                        if r == 'get-game':
                                            print('Game send')
                                            network.send_pickle(game)
                                    except Exception as e:
                                        messagebox.showwarning('UNO', f'{e}')
                            else:
                                opt, cname = game.draw_card()
                                if opt:
                                    act = handle_draw_card(cname)
                                    if act == 'play':
                                        if cname.startswith('Wild'):
                                            selected_color = handle_color_selection()  # Get the color selected by the player
                                            if selected_color:
                                                try:
                                                    game.play(cname, wild_color=selected_color)
                                                    r = network.get('game')
                                                    if r == 'get-game':
                                                        print('Game send')
                                                        network.send_pickle(game)
                                                except Exception as e:
                                                    messagebox.showwarning('UNO', f'{e}')
                                        else:
                                            print('Player Turn Can play')
                                            try:
                                                game.play(cname)
                                                r = network.get('game')
                                                if r == 'get-game':
                                                    print('Game send')
                                                    network.send_pickle(game)
                                            except Exception as e:
                                                messagebox.showwarning('UNO', f'{e}')
                                    else:
                                        game.play('draw_card')
                                        r = network.get('game')
                                        if r == 'get-game':
                                            network.send_pickle(game)
                                else:
                                    game.play('draw_card')
                                    r = network.get('game')
                                    if r == 'get-game':
                                        network.send_pickle(game)


        bts = redrawWin(win, game, player, elapsed_time)
        uno_button.draw(win)



if __name__ == "__main__":
    main()
