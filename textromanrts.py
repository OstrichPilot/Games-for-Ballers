import random
import time
import os

# Game constants
CITIES = ["Roma", "Capua", "Venetia"]
ROMAN_CITY_NAMES = ["Pompeii", "Ostia", "Neapolis", "Ravenna", "Brundisium", "Mediolanum", "Aquileia", "Syracusae", "Carthage", "Athens", "Sparta", "Constantinople", "Alexandria"]
gold = 100
food = 100
earn_rate = 15
turn = 0
famine_turns_left = 0
extreme_famine_turns_left = 0


# Unit and enemy data
units = []
enemies = []

# Each city starts under your control
city_control = {city: " Roman Control" for city in CITIES}

# Define unit templates
unit_types = {
    "Legion": {"cost_food": 20, "cost_gold": 20, "damage": 10, "kills_to_retire": 2},
    "Shieldwall": {"cost_food": 70, "cost_gold": 50, "damage": 20, "kills_to_retire": 3},
    "Plebian": {"cost_food": 15, "cost_gold": 15, "damage": 10, "kills_to_retire": 1},
}

enemy_types = {
    "Barbarian": {"hp": 20, "speed": "normal"},
    "Druid": {"hp": 1, "speed": "fast"},
    "Chieftain": {"hp": 100, "speed": "slightly fast"},
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_status():
    print(f"\n--- TURN {turn} ---")
    print(f"Gold: {gold} | Food: {food}")
    print(f"Cities:")
    for c in CITIES:
        owner = city_control[c]
        print(f"  - {c}: {'🏛️ ' + owner}")
    print(f"\nYour Units: {len(units)} | Enemy Units: {len(enemies)}")

def train_unit():
    global gold, food
    print("\nTrain which unit?")
    for name, u in unit_types.items():
        print(f"{name}: {u['cost_food']} Food, {u['cost_gold']} Gold")
    choice = input("→ ").capitalize()
    if choice in unit_types:
        cost = unit_types[choice]
        if gold >= cost["cost_gold"] and food >= cost["cost_food"]:
            gold -= cost["cost_gold"]
            food -= cost["cost_food"]
            units.append({"type": choice, "kills": 0})
            print(f"Trained {choice}.")
        else:
            print("Not enough resources!")
    else:
        print("Invalid choice.")

def check_for_famine():
    global famine_turns_left, extreme_famine_turns_left

    # Only roll for famine if none is active
    if famine_turns_left == 0 and extreme_famine_turns_left == 0:
        roll = random.random()

        if roll < 0.05:  # 5% chance of famine
            famine_turns_left = random.randint(1, 3)
            print(f"🌾 A famine has struck! Food production halted for {famine_turns_left} turns.")
        elif roll < 0.08:  # 3% chance of extreme famine
            extreme_famine_turns_left = random.randint(1, 2)
            print(f"🔥 An EXTREME FAMINE devastates your lands! Food consumption multiplied for {extreme_famine_turns_left} turns.")

def spawn_enemy():
    """Randomly spawns enemies targeting cities."""
    if random.random() < 0.6:  # 60% chance per turn
        enemy = random.choice(list(enemy_types.keys()))
        target = random.choice(CITIES)
        enemies.append({"type": enemy, "target": target, "hp": enemy_types[enemy]["hp"]})
        print(f"⚔️  A {enemy} is attacking {target}!")

def apply_upkeep():
    global food, units, extreme_famine_turns_left

    if not units:
        return

    # Base upkeep: 1 food per unit
    upkeep_cost = len(units)

    # Extreme famine effect
    if extreme_famine_turns_left > 0:
        upkeep_cost *= 5
        print(f"🔥 Extreme famine increases consumption to {upkeep_cost} food!")

    food -= upkeep_cost
    print(f"🍞 Your {len(units)} troops consumed {upkeep_cost} food this turn.")

    if food <= 0:
        food = 0
        print("⚠️ Your food stores are empty! Starvation begins to spread among your ranks.")
        if units:
            lost_unit = random.choice(units)
            units.remove(lost_unit)
            print(f"💀 A starving {lost_unit['type']} deserted your army.")

def battle_phase():
    """Simulates unit vs enemy combat and city attacks."""
    global city_control

    if not enemies:
        return

    # Units fight enemies
    for u in units:
        if not enemies:
            break
        enemy = random.choice(enemies)
        dmg = unit_types[u["type"]]["damage"]
        enemy["hp"] -= dmg
        if enemy["hp"] <= 0:
            print(f"💀 {u['type']} killed a {enemy['type']}.")
            u["kills"] += 1
            enemies.remove(enemy)
            if u["kills"] >= unit_types[u["type"]]["kills_to_retire"]:
                print(f"🏅 {u['type']} retired after glorious service.")
                units.remove(u)

    # Remaining enemies attack cities
    for e in enemies[:]:
        target = e["target"]
        if city_control[target] == " Roman Control":
            print(f"🔥 {target} has fallen to the {e['type']}s!")
            city_control[target] = "Barbarians"
            enemies.remove(e)

def check_game_over():
    if all(owner == "Barbarians" for owner in city_control.values()):
        print("\n💀 All your cities have fallen. Rome is lost.")
        return True
    return False

def build_city():
    global gold, food
    cost_gold = 300
    cost_food = 500

    if gold < cost_gold or food < cost_food:
        print("❌ Not enough resources to build a new city!")
        return

    available_names = [name for name in ROMAN_CITY_NAMES if name not in city_control]
    if not available_names:
        print("All possible Roman cities have already been founded!")
        return

    new_city = random.choice(available_names)
    gold -= cost_gold
    food -= cost_food
    city_control[new_city] = " Roman Control"
    CITIES.append(new_city)
    print(f"🏗️  A new city, {new_city}, has been founded!")


# --- MAIN LOOP ---
while True:
    clear()
    print_status()
    if check_game_over():
        break

    print("\nActions: [T]rain unit | [P]ass turn | [R]ecapture city | [B]uild city")
    action = input("→ ").lower()

    if action == "t":
        train_unit()
    elif action == "b":
        build_city()
    elif action == "r":
        cost = 50
        if gold < cost:
            print("❌ Not enough gold to recapture a city!")
        else:
            fallen = [c for c, owner in city_control.items() if owner == "Barbarians"]
            if fallen:
                city = random.choice(fallen)
                gold -= cost
                print(f"⚔️  You paid {cost} gold and marched on {city}, reclaiming it for Rome!")
                city_control[city] = " Roman Control"
            else:
                print("All cities are already under your control!")

        # End of player action block
    else:
        print("The turn passes.")

    # --- Turn resolution (must be inside the while loop) ---
    # Roll for famines BEFORE income
    check_for_famine()

    # Apply income (considering famine)
    gold += earn_rate
    if famine_turns_left > 0:
        famine_turns_left -= 1
        print("🌾 Famine continues — no food produced this turn.")
    elif extreme_famine_turns_left > 0:
        extreme_famine_turns_left -= 1
        print("🔥 Extreme famine continues — food stores strain under hunger.")
    else:
        food += earn_rate

    # Enemies spawn + battles
    spawn_enemy()
    battle_phase()

    # Upkeep (units consume food)
    apply_upkeep()

    # Advance the turn counter
    turn += 1

    # Pause so the player can read the turn output
    time.sleep(2)


    # Enemies spawn + battles
    spawn_enemy()
    battle_phase()
    apply_upkeep()

    time.sleep(2)
