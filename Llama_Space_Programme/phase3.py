
import os
import random
import pygame
import global_variables
import events

# The main launcher owns the shared display.
screen_width = 1280
screen_height = 720
screen = None
clock = pygame.time.Clock()
fps = 60

# fonts
# Keep the font file in the same folder as this Python file.
game_folder = os.path.dirname(os.path.abspath(__file__))

# AUDIO
# martian.mp3 is the looping background music for the Mars section.
# button.mp3 is played whenever the player clicks an on-screen button.

martian_music_path = os.path.join(game_folder, "martian.mp3")
button_sound_path = os.path.join(game_folder, "button.mp3")

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    if os.path.isfile(button_sound_path):
        button_sound = pygame.mixer.Sound(button_sound_path)
        button_sound.set_volume(0.65)
    else:
        button_sound = None
        print("Could not find audio file: button.mp3")

except pygame.error as audio_error:
    print("Audio could not be initialised:", audio_error)
    button_sound = None


def play_button_sound():
    if button_sound is not None:
        button_sound.play()


font_path = os.path.join(game_folder, "ShareTechMono-Regular.ttf")


def load_game_font(font_size):
    if os.path.isfile(font_path):
        return pygame.font.Font(font_path, font_size)

    # Fallback if the Share Tech Mono file has not been added yet.
    # The game will still run, although it will use a system monospace font.
    fallback_font = pygame.font.SysFont("monospace", font_size)
    return fallback_font


font_big = load_game_font(42)
font_medium = load_game_font(27)
font_small = load_game_font(23)
font_small_italic = load_game_font(21)
font_tiny = load_game_font(19)

# Share Tech Mono is supplied as a regular font. These synthetic styles
# give headings and secondary text a little extra distinction.
#font_big.set_bold(True)
#font_medium.set_bold(True)
#font_small_italic.set_italic(True)

# colours
background_colour = (17, 15, 14)
panel_colour = (29, 23, 19)
text_colour = (245, 229, 197)
muted_colour = (224, 157, 69)
line_colour = (105, 70, 39)
highlight_colour = (224, 157, 69)
warning_colour = (235, 91, 76)

# give each resource its own colour
oxygen_colour = (75, 190, 220)
food_colour = (150, 195, 90)
water_colour = (70, 135, 230)
energy_colour = (235, 165, 75)
power_colour = (175, 115, 220)

biome_colours = {
    "Rocky Plains": (105, 105, 100),
    "Desert": (165, 115, 70),
    "Crater": (65, 67, 75),
    "Volcano": (145, 65, 50),
    "Water": (65, 115, 155),
    "Base": (85, 135, 105)
}

# load biome images if they're available
def load_biome_images():
    biome_images = {}

    biome_image_files = {
        "Rocky Plains": "rocky_plains.png",
        "Desert": "desert.png",
        "Crater": "crater.png",
        "Volcano": "volcano.png",
        "Water": "water.png",
        "Base": "base.png"
    }

    for biome_name in biome_image_files:
        image_file = biome_image_files[biome_name]
        image_path = os.path.join(game_folder, image_file)

        if os.path.isfile(image_path):
            image = pygame.image.load(image_path).convert()
            image = pygame.transform.smoothscale(image, (46, 46))
            biome_images[biome_name] = image

    return biome_images

biome_images = load_biome_images()

# Load the full Mars background for the left-hand side of the interface.
# The image should be called "mars.jpg" and sit beside this Python file.
def load_mars_background():
    image_path = os.path.join(game_folder, "mars.jpg")

    if os.path.isfile(image_path):
        image = pygame.image.load(image_path).convert()
        image = pygame.transform.smoothscale(image, (540, 720))
        return image

    return None


mars_background = load_mars_background()

# get the starting values
number_of_rows = 10
number_of_columns = 10
day = 1

money = global_variables.money
food = global_variables.food
water = global_variables.water
oxygen = global_variables.oxygen
energy = global_variables.energy
power = global_variables.power
rad = 100
inventory = global_variables.inventory

# base storage starts empty
base_oxygen = 0
base_food = 0
base_water = 0

x_pos = 1
y_pos = 1
bases = 1

# map layout
cell_size = 46
map_start_x = 44
map_start_y = 128

# generate the map
def generate_biomes(basex, basey):
    planet_map = []

    for x in range(number_of_columns):
        column = []

        for y in range(number_of_rows):
            column.append("Rocky Plains")

        planet_map.append(column)

    middle_x_start = (number_of_columns - 2) // 2
    middle_y_start = (number_of_rows - 2) // 2

    # put the biomes in their places
    planet_map[basex][basey] = "Base"

    planet_map[middle_x_start][middle_y_start] = "Crater"
    planet_map[middle_x_start + 1][middle_y_start] = "Crater"
    planet_map[middle_x_start][middle_y_start + 1] = "Crater"
    planet_map[middle_x_start + 1][middle_y_start + 1] = "Crater"

    planet_map[middle_x_start][number_of_rows - 1] = "Water"
    planet_map[middle_x_start + 1][number_of_rows - 1] = "Water"

    planet_map[number_of_columns - 1][middle_y_start] = "Volcano"
    planet_map[number_of_columns - 1][middle_y_start + 1] = "Volcano"
    planet_map[number_of_columns - 2][middle_y_start] = "Volcano"
    planet_map[number_of_columns - 2][middle_y_start + 1] = "Volcano"

    planet_map[middle_x_start][0] = "Desert"
    planet_map[middle_x_start + 1][0] = "Desert"
    planet_map[middle_x_start - 1][0] = "Desert"
    planet_map[middle_x_start - 1][1] = "Desert"
    planet_map[middle_x_start - 2][0] = "Desert"

    return planet_map

planet_map = generate_biomes(x_pos, y_pos)

# Keep track of the first base and every base built later.
# The first base is marked in gold; additional bases are marked in cyan.
first_base_position = (x_pos, y_pos)
new_base_positions = []

# check whether an item is in the inventory
def item_is_owned(item_name):
    """Return True when an item is present in the current inventory.

    Phase 1 stores purchases as item lists, but accepting plain strings too
    makes the shared inventory check resilient to older save/test formats.
    """
    wanted_name = str(item_name).strip().casefold()

    for item in inventory:
        if isinstance(item, (list, tuple)) and item:
            owned_name = str(item[0]).strip().casefold()
        elif isinstance(item, str):
            owned_name = item.strip().casefold()
        else:
            continue

        if owned_name == wanted_name:
            return True

    return False

# work out how much we can store
def personal_oxygen_capacity():
    capacity = 100

    if item_is_owned("Emergency oxygen supply"):
        capacity = 120

    return capacity

def personal_food_capacity():
    capacity = 100
    return capacity

def personal_water_capacity():
    capacity = 100

    if item_is_owned("Water storage tank"):
        capacity = 200

    return capacity

def personal_power_capacity():
    capacity = 100

    if item_is_owned("Backup battery"):
        capacity = capacity + 100

    return capacity

def base_oxygen_capacity():
    capacity = 100 * bases
    return capacity

def base_food_capacity():
    capacity = 100 * bases
    return capacity

def base_water_capacity():
    capacity = 100 * bases

    if item_is_owned("Water storage tank"):
        capacity = capacity + 100

    return capacity

# put spare water into the base
def deposit_water_at_base():
    global water
    global base_water

    personal_reserve = 100
    excess_water = water - personal_reserve

    if excess_water > 0:
        available_base_space = base_water_capacity() - base_water
        water_to_deposit = min(excess_water, available_base_space)

        water = water - water_to_deposit
        base_water = base_water + water_to_deposit

# top up resources when we're at a base
def refill_from_base():
    global oxygen, food, water
    global base_oxygen, base_food, base_water

    oxygen_space = personal_oxygen_capacity() - oxygen
    oxygen_transfer = min(oxygen_space, base_oxygen)
    oxygen = oxygen + oxygen_transfer
    base_oxygen = base_oxygen - oxygen_transfer

    food_space = personal_food_capacity() - food
    food_transfer = min(food_space, base_food)
    food = food + food_transfer
    base_food = base_food - food_transfer

    water_space = personal_water_capacity() - water
    water_transfer = min(water_space, base_water)
    water = water + water_transfer
    base_water = base_water - water_transfer

# update all the resources
def update_stuff(dt):
    global oxygen, food, water, power
    global base_oxygen, base_food, base_water

    solar_efficiency = 1 - (0.02 * (day - 1))
    solar_efficiency = max(0, solar_efficiency)

    # generate resources from equipment
    for item in inventory:
        item_name = item[0]

        if item_name == "Plethora of plants":
            base_oxygen = base_oxygen + 6 * dt

        if item_name == "Solar panels":
            power = power + 10 * solar_efficiency * dt

        if item_name == "Self-sweeping solar panels":
            power = power + 10 * dt

    # grow food if we have enough water and power
    if item_is_owned("Hydroponic crop system"):
        if base_water >= 2 * dt and power >= 2 * dt:
            base_water = base_water - 2 * dt
            power = power - 2 * dt
            base_food = base_food + 4 * dt

    # consume personal resources
    oxygen = oxygen - 4 * dt
    food = food - 2 * dt

    if item_is_owned("Water recycling system"):
        water = water - 1 * dt
    else:
        water = water - 2 * dt

    # keep resources within their limits
    power = min(power, personal_power_capacity())
    power = max(0, power)

    base_oxygen = min(base_oxygen, base_oxygen_capacity())
    base_food = min(base_food, base_food_capacity())
    base_water = min(base_water, base_water_capacity())

    base_oxygen = max(0, base_oxygen)
    base_food = max(0, base_food)
    base_water = max(0, base_water)

# finish a turn and check whether we're still alive
status_message = "Welcome to Mars. Try not to die."
game_over = False

# The starting-base and spacesuit checks must use the inventory from the
# completed shop phase. They are therefore run from run_phase3(), not when
# this module is imported at the beginning of the game.
def check_starting_survival_requirements():
    global game_over, status_message

    game_over = False
    status_message = "Welcome to Mars. Try not to die."

    # A Polycarbon dome is the supported starting base. A Concrete box is
    # recognised separately so the player receives the intended explanation.
    if not item_is_owned("Polycarbon dome"):
        game_over = True

        if item_is_owned("Concrete box"):
            status_message = "The pressure difference at the corners killed you."
        else:
            status_message = "No base bought."

    elif (
        not item_is_owned("Basic spacesuit")
        and not item_is_owned("Advanced spacesuit")
    ):
        game_over = True
        status_message = "You died because you did not purchase a spacesuit."

# event popup information
event_popup_active = False
event_popup_title = ""
event_popup_description = ""
event_popup_subtitle = ""
event_popup_close_rect = pygame.Rect(0, 0, 0, 0)

def finish_turn():
    global day, game_over, status_message
    global money, energy, power, oxygen, water, base_oxygen, rad
    global event_popup_active, event_popup_title, event_popup_description, event_popup_subtitle

    dt = 1

    # Radiation is deliberately tracked internally and is never drawn
    # on the interface.
    if item_is_owned("Radiation shielding"):
        radiation_change_per_turn = -0.1
    else:
        radiation_change_per_turn = -0.5

    rad = rad + radiation_change_per_turn
    rad = max(0, rad)

    if planet_map[x_pos][y_pos] == "Base":
        deposit_water_at_base()

    update_stuff(dt)

    if planet_map[x_pos][y_pos] == "Base":
        refill_from_base()

    # Check the normal survival conditions first.
    if water <= 0:
        game_over = True
        status_message = "You have run out of water."

    elif oxygen <= 0:
        game_over = True
        status_message = "You have run out of oxygen."

    elif food <= 0:
        game_over = True
        status_message = "You have run out of food."

    elif energy < 0:
        game_over = True
        status_message = "You have run out of energy."

    elif rad <= 0:
        game_over = True
        status_message = "You died from radiation exposure."

    # Every fifth turn, there is a 75% chance of a random event.
    # day is checked before it is increased, so the event occurs after turns 5, 10, 15, etc.
    if not game_over and events.should_trigger_event(day):

        (
            money,
            energy,
            power,
            oxygen,
            water,
            base_oxygen,
            event_popup_title,
            event_popup_description,
            event_popup_subtitle,
            deathmessage
        ) = events.run_random_event(
            money,
            energy,
            power,
            oxygen,
            water,
            base_oxygen
        )

        # Keep resources within their usual storage limits after an event.
        oxygen = min(oxygen, personal_oxygen_capacity())
        water = min(water, personal_water_capacity())
        energy = min(energy, 100)
        power = min(power, personal_power_capacity())
        power = max(power, 0)
        base_oxygen = min(base_oxygen, base_oxygen_capacity())
        base_oxygen = max(base_oxygen, 0)

        event_popup_active = True

        # Some events can end the mission immediately.
        if deathmessage is not None:
            game_over = True
            status_message = str(deathmessage)

        elif water <= 0:
            game_over = True
            status_message = "You have run out of water."

        elif oxygen <= 0:
            game_over = True
            status_message = "You have run out of oxygen."

        elif food <= 0:
            game_over = True
            status_message = "You have run out of food."

        elif energy <= 0:
            game_over = True
            status_message = "You have run out of energy."

        elif rad <= 0:
            game_over = True
            status_message = "You died from radiation exposure."

    day = day + 1

# move around the map
def move_player(direction):
    global x_pos, y_pos
    global energy, water
    global status_message

    if energy < 0.25:
        status_message = "Not enough energy to move."
        return

    if water < 0.25:
        status_message = "Not enough water to move."
        return

    new_x = x_pos
    new_y = y_pos

    if direction == "north":
        new_y = new_y + 1

    elif direction == "south":
        new_y = new_y - 1

    elif direction == "east":
        new_x = new_x + 1

    elif direction == "west":
        new_x = new_x - 1

    if new_x < 0 or new_x >= number_of_columns:
        status_message = "You cannot move beyond the map."
        return

    if new_y < 0 or new_y >= number_of_rows:
        status_message = "You cannot move beyond the map."
        return

    energy = energy - 0.25
    water = water - 0.25

    x_pos = new_x
    y_pos = new_y

    status_message = "Moved " + direction + "."
    finish_turn()

# mine some ice
def mine_water():
    global energy, power, water
    global status_message

    current_biome = planet_map[x_pos][y_pos]

    if current_biome != "Water":
        status_message = "There is no accessible ice here."
        return

    available_water_space = personal_water_capacity() - water

    if available_water_space <= 0:
        status_message = "Your water supply is already full."
        return

    if energy < 5 or power < 5:
        status_message = "You need 5 energy and 5 power to mine ice."
        return

    energy = energy - 5
    power = power - 5

    water_mined = min(50, available_water_space)
    water = water + water_mined

    status_message = "Mined " + str(int(water_mined)) + " units of water."
    finish_turn()

# see whether there's any ore about
def mine_ore():
    global energy, power, money
    global status_message

    if energy < 10 or power < 10:
        status_message = "You need 10 energy and 10 power to mine."
        return

    energy = energy - 10
    power = power - 10

    ore_probability = random.randint(1, 100)
    current_biome = planet_map[x_pos][y_pos]

    if current_biome == "Volcano":
        ore_probability = ore_probability * 1.5

    elif current_biome == "Water":
        ore_probability = ore_probability * 0.6

    elif current_biome == "Desert":
        ore_probability = ore_probability * 0.9

    elif current_biome == "Crater":
        ore_probability = ore_probability * 1.1

    if ore_probability > 70:
        second_roll = random.randint(1, 100)

        if second_roll > 20:
            reward = random.randint(20, 100)
            money = money + reward
            status_message = "You found valuable ore. Earned £" + str(reward) + "."
        else:
            status_message = "You found some ore, but it was not commercially useful."
    else:
        status_message = "No useful ore found."

    finish_turn()

# deploy the probe
def probe():
    global status_message

    status_message = "Your llama does not have prostate cancer."
    finish_turn()

# have a little rest
def rest():
    global energy, status_message

    energy = min(100, energy + 10)
    status_message = "You rested and recovered some energy."
    finish_turn()

# build another base
def build_base():
    global energy, power, water, oxygen, bases
    global status_message, new_base_positions

    current_biome = planet_map[x_pos][y_pos]

    if bases >= 3:
        status_message = "You cannot build more than three bases."
        return

    if current_biome == "Base":
        status_message = "There is already a base here."
        return

    if current_biome == "Water":
        status_message = "You cannot build a base on an ice cap."
        return

    if energy < 50 or power < 50:
        status_message = "Building requires 50 energy and 50 power."
        return

    if water < 30 or oxygen < 10:
        status_message = "Building requires 30 water and 10 oxygen."
        return

    # find a structure in the inventory
    base_item_index = None

    for index in range(len(inventory)):
        item_name = inventory[index][0]

        if item_name == "Concrete box":
            base_item_index = index
            break

        elif item_name == "Polycarbon dome":
            base_item_index = index
            break

    if base_item_index is None:
        status_message = "You need a Concrete box or Polycarbon dome."
        return

    # use up the structure and resources
    del inventory[base_item_index]

    energy = energy - 50
    power = power - 50
    water = water - 30
    oxygen = oxygen - 10

    planet_map[x_pos][y_pos] = "Base"
    bases = bases + 1
    new_base_positions.append((x_pos, y_pos))

    status_message = "Base constructed successfully."
    finish_turn()

# draw a square-cornered retro panel with a gold border
def draw_retro_panel(panel_rect, alpha=220, border_colour=None):
    if border_colour is None:
        border_colour = highlight_colour

    panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel_surface.fill((panel_colour[0], panel_colour[1], panel_colour[2], alpha))
    screen.blit(panel_surface, panel_rect.topleft)

    pygame.draw.rect(screen, border_colour, panel_rect, 2)

    # A second, slightly inset line gives the panel an old instrument-panel look.
    inner_rect = panel_rect.inflate(-7, -7)
    if inner_rect.width > 0 and inner_rect.height > 0:
        pygame.draw.rect(screen, line_colour, inner_rect, 1)


# draw the map
def draw_map():
    for x in range(number_of_columns):
        for y in range(number_of_rows):
            biome_name = planet_map[x][y]

            screen_x = map_start_x + (x * cell_size)
            screen_y = map_start_y + ((number_of_rows - 1 - y) * cell_size)

            cell_rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)

            if biome_name in biome_images:
                screen.blit(biome_images[biome_name], cell_rect)
            else:
                pygame.draw.rect(screen, biome_colours[biome_name], cell_rect)

    # draw the grid over the squares
    map_width = number_of_columns * cell_size
    map_height = number_of_rows * cell_size

    for column in range(number_of_columns + 1):
        line_x = map_start_x + column * cell_size
        pygame.draw.line(screen, (35, 25, 18), (line_x, map_start_y), (line_x, map_start_y + map_height), 2)

    for row in range(number_of_rows + 1):
        line_y = map_start_y + row * cell_size
        pygame.draw.line(screen, (35, 25, 18), (map_start_x, line_y), (map_start_x + map_width, line_y), 2)

    # Mark the original base in gold and later bases in cyan.
    # Numbering makes it clear which base is the first one.
    original_base_x = first_base_position[0]
    original_base_y = first_base_position[1]

    original_base_screen_x = map_start_x + (original_base_x * cell_size)
    original_base_screen_y = map_start_y + ((number_of_rows - 1 - original_base_y) * cell_size)

    original_base_rect = pygame.Rect(
        original_base_screen_x + 4,
        original_base_screen_y + 4,
        cell_size - 8,
        cell_size - 8
    )

    original_base_colour = (255, 205, 75)

    pygame.draw.rect(
        screen,
        original_base_colour,
        original_base_rect,
        4
    )

    draw_centred_text(
        "1",
        font_small,
        original_base_colour,
        original_base_rect.centerx,
        original_base_rect.centery - font_small.get_linesize() // 2
    )

    for base_number in range(len(new_base_positions)):

        new_base_x = new_base_positions[base_number][0]
        new_base_y = new_base_positions[base_number][1]

        new_base_screen_x = map_start_x + (new_base_x * cell_size)
        new_base_screen_y = map_start_y + ((number_of_rows - 1 - new_base_y) * cell_size)

        new_base_rect = pygame.Rect(
            new_base_screen_x + 4,
            new_base_screen_y + 4,
            cell_size - 8,
            cell_size - 8
        )

        new_base_colour = (70, 225, 235)

        pygame.draw.rect(
            screen,
            new_base_colour,
            new_base_rect,
            4
        )

        draw_centred_text(
            str(base_number + 2),
            font_small,
            new_base_colour,
            new_base_rect.centerx,
            new_base_rect.centery - font_small.get_linesize() // 2
        )

    # mark the llama's position
    player_centre_x = map_start_x + (x_pos * cell_size) + cell_size // 2
    player_centre_y = map_start_y + ((number_of_rows - 1 - y_pos) * cell_size) + cell_size // 2
    cross_size = 11

    pygame.draw.line(screen, (20, 20, 20), (player_centre_x - cross_size, player_centre_y), (player_centre_x + cross_size, player_centre_y), 7)
    pygame.draw.line(screen, (20, 20, 20), (player_centre_x, player_centre_y - cross_size), (player_centre_x, player_centre_y + cross_size), 7)
    pygame.draw.line(screen, (255, 255, 255), (player_centre_x - cross_size, player_centre_y), (player_centre_x + cross_size, player_centre_y), 3)
    pygame.draw.line(screen, (255, 255, 255), (player_centre_x, player_centre_y - cross_size), (player_centre_x, player_centre_y + cross_size), 3)

# put some text on screen
def draw_text(text, font, colour, x, y):
    text_surface = font.render(str(text), True, colour)
    screen.blit(text_surface, (x, y))

def draw_centred_text(text, font, colour, centre_x, y):
    text_surface = font.render(str(text), True, colour)
    text_rect = text_surface.get_rect()
    text_rect.centerx = centre_x
    text_rect.y = y
    screen.blit(text_surface, text_rect)

# wrap text to fit inside a window
def wrap_text(text, font, max_width):

    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:

        if current_line == "":
            test_line = word
        else:
            test_line = current_line + " " + word

        if font.size(test_line)[0] <= max_width:
            current_line = test_line

        else:
            if current_line != "":
                lines.append(current_line)

            # Split a single very long word into smaller pieces.
            if font.size(word)[0] > max_width:

                partial_word = ""

                for character in word:

                    test_partial_word = partial_word + character

                    if font.size(test_partial_word)[0] <= max_width:
                        partial_word = test_partial_word
                    else:
                        if partial_word != "":
                            lines.append(partial_word)

                        partial_word = character

                current_line = partial_word

            else:
                current_line = word

    if current_line != "":
        lines.append(current_line)

    if len(lines) == 0:
        lines.append("")

    return lines


def draw_wrapped_text(text, font, colour, x, y, max_width, line_gap=3, max_lines=None):

    lines = wrap_text(text, font, max_width)
    line_height = font.get_linesize() + line_gap

    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]

        # Indicate that more text exists beyond the available space.
        final_line = lines[-1]
        while final_line and font.size(final_line + "...")[0] > max_width:
            final_line = final_line[:-1]

        lines[-1] = final_line.rstrip() + "..."

    for line in lines:
        draw_text(line, font, colour, x, y)
        y += line_height

    return y, lines

# draw one of the resource meters
def draw_meter(label, value, maximum, colour, x, y):

    meter_width = 105
    meter_height = 11

    # Resource name above the meter.
    draw_text(label, font_tiny, muted_colour, x, y)

    # Empty meter background.
    meter_rect = pygame.Rect(x, y + 29, meter_width, meter_height)
    pygame.draw.rect(screen, (48, 36, 27), meter_rect)

    # Coloured meter fill.
    if maximum > 0:
        meter_fraction = value / maximum
    else:
        meter_fraction = 0

    meter_fraction = max(0, min(1, meter_fraction))
    fill_width = int(meter_width * meter_fraction)

    if fill_width > 0:
        fill_rect = pygame.Rect(x, y + 29, fill_width, meter_height)
        pygame.draw.rect(screen, colour, fill_rect)

    # Fine outline around the meter.
    pygame.draw.rect(screen, line_colour, meter_rect, 1)

# show all the resources
def draw_resources():

    # A single panel ties the resource meters and base storage together.
    resource_panel = pygame.Rect(565, 91, 690, 112)
    draw_retro_panel(resource_panel, alpha=225)

    resource_positions = [590, 720, 850, 980, 1110]

    draw_meter("OXYGEN", oxygen, personal_oxygen_capacity(), oxygen_colour, resource_positions[0], 111)
    draw_meter("FOOD", food, personal_food_capacity(), food_colour, resource_positions[1], 111)
    draw_meter("WATER", water, personal_water_capacity(), water_colour, resource_positions[2], 111)
    draw_meter("ENERGY", energy, 100, energy_colour, resource_positions[3], 111)
    draw_meter("POWER", power, personal_power_capacity(), power_colour, resource_positions[4], 111)

    # Money gets its own box. Its width follows the actual amount displayed.
    money_text = "£" + str(int(money))
    money_surface = font_big.render(money_text, True, highlight_colour)

    money_box_width = money_surface.get_width() + 30
    money_box_height = money_surface.get_height() + 12

    money_box = pygame.Rect(
        1235 - money_box_width,
        21,
        money_box_width,
        money_box_height
    )

    draw_retro_panel(money_box, alpha=235)
    money_rect = money_surface.get_rect(center=money_box.center)
    screen.blit(money_surface, money_rect)

    # Base storage sits neatly along the bottom of the resource panel.
    base_storage_text = (
        "BASE STORAGE   "
        + "O2 " + str(round(base_oxygen))
        + "     FOOD " + str(round(base_food))
        + "     H2O " + str(round(base_water))
    )

    draw_text(base_storage_text, font_tiny, muted_colour, 590, 174)

# check whether any resources are running low
def get_resource_warnings():
    warnings = []

    if oxygen <= personal_oxygen_capacity() * 0.25:
        warnings.append("Oxygen is running low!")

    if food <= personal_food_capacity() * 0.25:
        warnings.append("Food is running low!")

    if water <= personal_water_capacity() * 0.25:
        warnings.append("Water is running low!")

    if energy <= 25:
        warnings.append("Energy is running low!")

    if power <= personal_power_capacity() * 0.25:
        warnings.append("Power is running low!")

    if money <= 1000:
        warnings.append("Money is running low!")

    return warnings

# show the status and warning messages
def draw_notifications():

    window_x = 580
    window_y = 265
    minimum_width = 330
    maximum_width = 360

    warnings = get_resource_warnings()

    # Work out a suitable width from the longest line of text.
    widest_text = font_tiny.size("ALERTS")[0]

    for warning in warnings:
        warning_width = font_tiny.size("! " + warning)[0]
        widest_text = max(widest_text, warning_width)

    window_width = widest_text + 38
    window_width = max(minimum_width, window_width)
    window_width = min(maximum_width, window_width)

    content_width = window_width - 28
    message_lines = wrap_text(status_message, font_tiny, content_width)

    # The height is calculated from the actual number of lines to display.
    title_height = font_small.get_linesize() + 17
    message_height = len(message_lines) * (font_tiny.get_linesize() + 2)
    warning_height = len(warnings) * (font_tiny.get_linesize() + 2)

    if len(warnings) == 0:
        warning_height = font_tiny.get_linesize() + 2

    window_height = 18 + title_height + 8 + message_height + 8 + warning_height + 15

    # Keep the alerts panel clear of the action buttons below it.
    maximum_height = 250
    window_height = min(window_height, maximum_height)

    notification_rect = pygame.Rect(window_x, window_y, window_width, window_height)
    draw_retro_panel(notification_rect, alpha=238)

    draw_text("ALERTS", font_small, muted_colour, window_x + 15, window_y + 12)

    text_y = window_y + 12 + title_height

    # Show the complete action message where possible.
    available_message_lines = max(
        1,
        (window_height - (text_y - window_y) - 35) // (font_tiny.get_linesize() + 2)
    )

    if len(message_lines) > available_message_lines:
        message_lines = message_lines[:available_message_lines]
        final_line = message_lines[-1]

        while final_line and font_tiny.size(final_line + "...")[0] > content_width:
            final_line = final_line[:-1]

        message_lines[-1] = final_line.rstrip() + "..."

    for line in message_lines:
        draw_text(line, font_tiny, text_colour, window_x + 14, text_y)
        text_y += font_tiny.get_linesize() + 2

    text_y += 7

    if len(warnings) > 0:

        for warning in warnings:

            if text_y + font_tiny.get_linesize() > notification_rect.bottom - 8:
                break

            draw_text("! " + warning, font_tiny, warning_colour, window_x + 14, text_y)
            text_y += font_tiny.get_linesize() + 2

    else:
        draw_text(
            "All resources looking healthy.",
            font_tiny,
            food_colour,
            window_x + 14,
            text_y
        )


# draw the random event popup
# The popup stays on screen until the small x in the corner is clicked.
def draw_event_popup():

    global event_popup_close_rect

    if event_popup_active:

        popup_width = 780
        popup_x = (screen_width - popup_width) // 2
        text_width = popup_width - 58

        title_lines = wrap_text(event_popup_title, font_medium, text_width - 35)
        description_lines = wrap_text(event_popup_description, font_small, text_width)

        title_line_height = font_medium.get_linesize() + 2
        description_line_height = font_small.get_linesize() + 5

        subtitle_height = font_tiny.get_linesize() + 8

        popup_height = (
            25
            + len(title_lines) * title_line_height
            + 18
            + subtitle_height
            + 12
            + len(description_lines) * description_line_height
            + 22
        )

        popup_height = max(220, popup_height)
        popup_height = min(screen_height - 50, popup_height)

        popup_y = (screen_height - popup_height) // 2

        # Darken the game slightly behind the popup.
        popup_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        popup_overlay.fill((0, 0, 0, 155))
        screen.blit(popup_overlay, (0, 0))

        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        draw_retro_panel(popup_rect, alpha=248)

        # Event title.
        title_y = popup_y + 17

        for title_line in title_lines:
            draw_text(title_line, font_medium, text_colour, popup_x + 25, title_y)
            title_y += title_line_height

        # Small close button in the top-right corner.
        event_popup_close_rect = pygame.Rect(
            popup_x + popup_width - 43,
            popup_y + 12,
            28,
            28
        )

        mouse_position = pygame.mouse.get_pos()

        if event_popup_close_rect.collidepoint(mouse_position):
            close_colour = warning_colour
        else:
            close_colour = muted_colour

        close_surface = font_medium.render("x", True, close_colour)
        close_rect = close_surface.get_rect(center=event_popup_close_rect.center)
        screen.blit(close_surface, close_rect)

        # Divider beneath the title.
        divider_y = popup_y + 20 + len(title_lines) * title_line_height + 5

        pygame.draw.line(
            screen,
            line_colour,
            (popup_x + 25, divider_y),
            (popup_x + popup_width - 25, divider_y),
            1
        )

        # Colour the subtitle according to the event's effect.
        subtitle_colour = highlight_colour

        if "increased" in event_popup_subtitle.lower():
            subtitle_colour = food_colour

        elif (
            "decreased" in event_popup_subtitle.lower()
            or "destroyed" in event_popup_subtitle.lower()
            or "emptied" in event_popup_subtitle.lower()
        ):
            subtitle_colour = warning_colour

        elif event_popup_subtitle == "No change":
            subtitle_colour = muted_colour

        subtitle_y = divider_y + 12

        draw_text(
            event_popup_subtitle,
            font_tiny,
            subtitle_colour,
            popup_x + 25,
            subtitle_y
        )

        # Event description.
        description_y = subtitle_y + subtitle_height

        available_description_height = popup_y + popup_height - 18 - description_y
        maximum_description_lines = max(
            1,
            available_description_height // description_line_height
        )

        if len(description_lines) > maximum_description_lines:
            description_lines = description_lines[:maximum_description_lines]
            final_line = description_lines[-1]

            while final_line and font_small.size(final_line + "...")[0] > text_width:
                final_line = final_line[:-1]

            description_lines[-1] = final_line.rstrip() + "..."

        for line in description_lines:
            draw_text(line, font_small, text_colour, popup_x + 25, description_y)
            description_y += description_line_height


# set up the clickable compass
compass_centre_x = 1050
compass_centre_y = 390

compass_rects = {
    "north": pygame.Rect(compass_centre_x - 28, compass_centre_y - 94, 55, 55),
    "west": pygame.Rect(compass_centre_x - 94, compass_centre_y - 28, 55, 55),
    "east": pygame.Rect(compass_centre_x + 39, compass_centre_y - 28, 55, 55),
    "south": pygame.Rect(compass_centre_x - 28, compass_centre_y + 39, 55, 55)
}

# draw the compass
def draw_compass():
    mouse_position = pygame.mouse.get_pos()

    draw_centred_text("MOVE: WASD / ARROWS", font_tiny, muted_colour, compass_centre_x, 255)

    direction_labels = {
        "north": "N",
        "west": "W",
        "east": "E",
        "south": "S"
    }

    for direction in compass_rects:
        button_rect = compass_rects[direction]

        if button_rect.collidepoint(mouse_position):
            button_colour = (82, 54, 28)
            border_colour = highlight_colour
        else:
            button_colour = panel_colour
            border_colour = line_colour

        pygame.draw.rect(screen, button_colour, button_rect)
        pygame.draw.rect(screen, border_colour, button_rect, width=2)
        draw_centred_text(direction_labels[direction], font_medium, text_colour, button_rect.centerx, button_rect.y + 14)

    pygame.draw.circle(screen, line_colour, (compass_centre_x, compass_centre_y), 19, 2)
    pygame.draw.circle(screen, highlight_colour, (compass_centre_x, compass_centre_y), 4)

# set up the action buttons
action_rects = {
    "mine_water": pygame.Rect(580, 520, 300, 42),
    "mine_ore": pygame.Rect(910, 520, 300, 42),
    "probe": pygame.Rect(580, 570, 300, 42),
    "rest": pygame.Rect(910, 570, 300, 42),
    "build_base": pygame.Rect(580, 620, 630, 42)
}

action_labels = {
    "mine_water": "MINE WATER",
    "mine_ore": "MINE ORE",
    "probe": "PROBE",
    "rest": "REST",
    "build_base": "BUILD BASE"
}

# draw the action buttons
def draw_action_buttons():
    mouse_position = pygame.mouse.get_pos()

    for action_name in action_rects:
        button_rect = action_rects[action_name]

        if button_rect.collidepoint(mouse_position):
            button_colour = (82, 54, 28)
            border_colour = highlight_colour
        else:
            button_colour = panel_colour
            border_colour = line_colour

        pygame.draw.rect(screen, button_colour, button_rect)
        pygame.draw.rect(screen, border_colour, button_rect, width=2)

        inner_button_rect = button_rect.inflate(-7, -7)
        pygame.draw.rect(screen, line_colour, inner_button_rect, width=1)

        draw_centred_text(
            action_labels[action_name],
            font_small,
            text_colour,
            button_rect.centerx,
            button_rect.centery - font_small.get_linesize() // 2
        )

# draw everything
def draw_interface():
    screen.fill(background_colour)

    # Stretch mars.jpg over the complete left-hand surface.
    # The map and its framed information panels are drawn over the image.
    if mars_background is not None:
        screen.blit(mars_background, (0, 0))
    else:
        # Fallback surface colour if mars.jpg has not been supplied yet.
        pygame.draw.rect(screen, (76, 39, 25), (0, 0, 540, 720))

    # A subtle divider separates the Mars display from the mission controls.
    pygame.draw.line(screen, highlight_colour, (540, 22), (540, 698), 2)
    pygame.draw.line(screen, line_colour, (545, 22), (545, 698), 1)

    # Box containing the Mars title and current turn.
    title_panel_rect = pygame.Rect(28, 20, 484, 82)
    draw_retro_panel(title_panel_rect, alpha=220)
    draw_centred_text(
        "MARS - TURN " + str(day),
        font_big,
        highlight_colour,
        title_panel_rect.centerx,
        title_panel_rect.y + 23
    )

    # The biome grid sits above the Mars background inside its own frame.
    map_panel_rect = pygame.Rect(28, 112, 484, 484)
    draw_retro_panel(map_panel_rect, alpha=55)
    draw_map()
    pygame.draw.rect(screen, highlight_colour, map_panel_rect, 2)

    # A separate framed biome key sits beneath the map, still above mars.jpg.
    legend_panel_rect = pygame.Rect(28, 606, 484, 96)
    draw_retro_panel(legend_panel_rect, alpha=225)
    draw_text("BIOME KEY", font_tiny, highlight_colour, 43, 612)

    legend_items = [
        ("Rocky Plains", biome_colours["Rocky Plains"]),
        ("Desert", biome_colours["Desert"]),
        ("Crater", biome_colours["Crater"]),
        ("Volcano", biome_colours["Volcano"]),
        ("Water", biome_colours["Water"]),
        ("Base", biome_colours["Base"])
    ]

    legend_positions = [
        (44, 638),
        (204, 638),
        (364, 638),
        (44, 663),
        (204, 663),
        (364, 663)
    ]

    for index in range(len(legend_items)):
        biome_name = legend_items[index][0]
        biome_colour = legend_items[index][1]
        legend_x = legend_positions[index][0]
        legend_y = legend_positions[index][1]

        pygame.draw.rect(screen, biome_colour, (legend_x, legend_y, 12, 12))
        pygame.draw.rect(screen, highlight_colour, (legend_x, legend_y, 12, 12), 1)
        draw_text(biome_name, font_tiny, muted_colour, legend_x + 18, legend_y - 2)

    draw_text(
        "BASE MARKERS   GOLD: 1   CYAN: NEW",
        font_tiny,
        text_colour,
        43,
        681
    )

    # Mission heading and balance sit together in a single instrument panel.
    heading_panel_rect = pygame.Rect(565, 18, 690, 62)
    draw_retro_panel(heading_panel_rect, alpha=232)

    draw_text("MISSION STATUS", font_big, highlight_colour, 585, 27)

    pygame.draw.line(
        screen,
        line_colour,
        (585, 70),
        (1235, 70),
        1
    )

    draw_resources()
    draw_notifications()
    draw_compass()
    draw_action_buttons()

    # Standard death screen.
    # Both the heading and the reason are red, matching the Mars warning style.
    if game_over:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        death_red = (235, 75, 65)

        draw_centred_text(
            "YOU DIED",
            font_big,
            death_red,
            screen_width // 2,
            285
        )

        death_reason_lines = wrap_text(
            status_message,
            font_medium,
            screen_width - 180
        )

        death_line_height = font_medium.get_linesize() + 7
        death_text_start_y = 355

        for death_line in death_reason_lines:
            draw_centred_text(
                death_line,
                font_medium,
                death_red,
                screen_width // 2,
                death_text_start_y
            )

            death_text_start_y = death_text_start_y + death_line_height

        draw_centred_text(
            "PRESS ESC OR ENTER TO RETURN",
            font_tiny,
            muted_colour,
            screen_width // 2,
            650
        )

    # Do not draw a random-event popup over the death screen.
    if not game_over:
        draw_event_popup()

    pygame.display.update()



def run_phase3(screen_surface):
    """Run the Mars exploration phase using the shared Pygame display."""
    global screen, running, event_popup_active
    global money, food, water, oxygen, energy, power, inventory

    screen = screen_surface
    running = True
    phase3_window_closed = False

    # phase3.py is imported at launch, so refresh these values now that
    # Phase 1 and the flight stage have updated the shared game state.
    money = global_variables.money
    food = global_variables.food
    water = global_variables.water
    oxygen = global_variables.oxygen
    energy = global_variables.energy
    power = global_variables.power
    inventory = global_variables.inventory

    # Inventory changes during Phase 1, after this module was imported.
    # Validate the latest purchases only now that Phase 3 is starting.
    check_starting_survival_requirements()

    if os.path.isfile(martian_music_path):
        pygame.mixer.music.load(martian_music_path)
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1)
    else:
        print("Could not find audio file: martian.mp3")

    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                phase3_window_closed = True
                running = False

            # While an event popup is open, only its x button can be clicked.
            elif event_popup_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if event_popup_close_rect.collidepoint(event.pos):
                            play_button_sound()
                            event_popup_active = False

            # Let the player leave a failed start instead of trapping them
            # on the death overlay until they close the whole window.
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER
                ):
                    running = False

            # Normal movement and actions are available when no popup is open.
            elif not game_over:

                # Both WASD and the arrow keys move around Mars.
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        move_player("north")
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        move_player("south")
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        move_player("west")
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        move_player("east")

                # use the mouse for the compass and action buttons
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_position = event.pos

                        # check the compass first
                        for direction in compass_rects:
                            if compass_rects[direction].collidepoint(mouse_position):
                                play_button_sound()
                                move_player(direction)
                                break

                        else:
                            # otherwise check the action buttons
                            for action_name in action_rects:
                                if action_rects[action_name].collidepoint(mouse_position):
                                    play_button_sound()

                                    if action_name == "mine_water":
                                        mine_water()
                                    elif action_name == "mine_ore":
                                        mine_ore()
                                    elif action_name == "probe":
                                        probe()
                                    elif action_name == "rest":
                                        rest()
                                    elif action_name == "build_base":
                                        build_base()

                                    break

        draw_interface()

    # Put the values back into the shared variables.
    global_variables.money = money
    global_variables.food = food
    global_variables.water = water
    global_variables.oxygen = oxygen
    global_variables.energy = energy
    global_variables.power = power
    global_variables.rad = rad
    global_variables.inventory = inventory

    pygame.mixer.music.fadeout(1000)
    return not phase3_window_closed

