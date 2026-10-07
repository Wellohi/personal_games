import time
import msvcrt
import random
import json
import os
from collections import deque
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console, Group
from rich.prompt import Prompt
from engine import Player, Monster, Item, CombatLog

# Global Events
WORLD_EVENTS = {
    "Blood Moon": {"atk_mult": 1.2, "gold_mult": 2.0, "desc": "Monsters hit harder but drop double gold!", "color": "red"},
    "Mana Storm": {"int_mult": 2.0, "desc": "Intelligence effects are doubled!", "color": "cyan"},
    "Void Rift": {"dodge_chance": 0.1, "desc": "Monsters have a chance to vanish (dodge)!", "color": "magenta"},
    "Golden Age": {"gold_mult": 3.0, "desc": "Everything is profitable! Triple gold!", "color": "gold1"},
}

SAVE_FILE = "savegame.json"

SHOP_ITEMS = {
    "Warrior": [
        # Tier 1 (Lvl 1-5)
        Item("Iron Sword", "Weapon", "Attack", 15, "Warrior", cost=50, min_level=1),
        Item("Padded Armor", "Armor", "HP", 40, "Warrior", cost=40, min_level=1),
        Item("Wooden Shield", "Shield", "HP", 20, "Warrior", cost=30, min_level=1),
        Item("Leather Boots", "Boots", "HP", 10, "Warrior", cost=20, min_level=1),
        Item("Rusty Helm", "Helmet", "Defense", 5, "Warrior", cost=30, min_level=1),
        # Tier 2 (Lvl 6-15)
        Item("Steel Blade", "Weapon", "Attack", 40, "Warrior", cost=200, min_level=6),
        Item("Chainmail", "Armor", "HP", 120, "Warrior", cost=150, min_level=6),
        Item("Iron Aegis", "Shield", "HP", 60, "Warrior", cost=120, min_level=6),
        Item("Steel Boots", "Boots", "HP", 30, "Warrior", cost=80, min_level=6),
        Item("Iron Helm", "Helmet", "Defense", 15, "Warrior", cost=100, min_level=6),
        # Tier 3 (Lvl 16-30)
        Item("Mithril Claymore", "Weapon", "Attack", 100, "Warrior", cost=600, min_level=16),
        Item("Plate Armor", "Armor", "HP", 300, "Warrior", cost=500, min_level=16),
        Item("Titan Shield", "Shield", "HP", 150, "Warrior", cost=400, min_level=16),
        Item("Mithril Boots", "Boots", "HP", 80, "Warrior", cost=300, min_level=16),
        Item("Royal Helm", "Helmet", "Defense", 40, "Warrior", cost=350, min_level=16),
        # Tier 4 (Lvl 31+)
        Item("Dragon-Slayer's Edge", "Weapon", "Attack", 250, "Warrior", cost=2000, min_level=31),
        Item("Eternal Bastion", "Armor", "HP", 800, "Warrior", cost=1500, min_level=31),
        Item("God-King's Shield", "Shield", "HP", 400, "Warrior", cost=1200, min_level=31),
        Item("Divine Boots", "Boots", "HP", 200, "Warrior", cost=800, min_level=31),
        Item("Emperor's Crown", "Helmet", "Defense", 100, "Warrior", cost=1000, min_level=31),
        # Tier 5 (Lvl 50-100)
        Item("Sun-Shatter Hammer", "Weapon", "Attack", 400, "Warrior", "crit_multiplier", cost=5000, min_level=50, set_name="Sun-Shatter"),
        Item("Plate of the Immortal", "Armor", "HP", 1500, "Warrior", "thorns", cost=4000, min_level=50, set_name="Plate of Immortal"),
        Item("Aegis of Eternity", "Shield", "HP", 500, "Warrior", "damage_mult", cost=3000, min_level=50, set_name="Sun-Shatter"),
        Item("Storm-Strider Greaves", "Boots", "HP", 200, "Warrior", "speed_mult", cost=2000, min_level=50, set_name="Sun-Shatter"),
        Item("Crown of the Warlord", "Helmet", "Defense", 150, "Warrior", "crit_chance", cost=2500, min_level=50, set_name="Plate of Immortal"),
        # Tier 6 (Lvl 100+)
        Item("World-Ender Blade", "Weapon", "Attack", 1000, "Warrior", "lifesteal", cost=15000, min_level=100, set_name="World-Ender"),
        Item("Void-Steel Mail", "Armor", "HP", 4000, "Warrior", "thorns", cost=12000, min_level=100, set_name="World-Ender"),
        Item("Cosmic Bulwark", "Shield", "HP", 1200, "Warrior", "damage_mult", cost=10000, min_level=100, set_name="World-Ender"),
        Item("God-Step Sabatons", "Boots", "HP", 500, "Warrior", "speed_mult", cost=8000, min_level=100, set_name="World-Ender"),
        Item("Helm of Absolute Power", "Helmet", "Defense", 400, "Warrior", "crit_multiplier", cost=9000, min_level=100, set_name="World-Ender"),
    ],
    "Mage": [
        # Tier 1 (Lvl 1-5)
        Item("Oak Staff", "Weapon", "Attack", 10, "Mage", cost=40, min_level=1),
        Item("Linen Robe", "Armor", "HP", 20, "Mage", cost=30, min_level=1),
        Item("Glass Bead", "Accessory", "Attack", 5, "Mage", cost=20, min_level=1),
        Item("Cloth Shoes", "Boots", "HP", 10, "Mage", cost=20, min_level=1),
        Item("Felt Hat", "Helmet", "Defense", 2, "Mage", cost=20, min_level=1),
        # Tier 2 (Lvl 6-15)
        Item("Ebony Wand", "Weapon", "Attack", 30, "Mage", cost=180, min_level=6),
        Item("Mystic Cloak", "Armor", "HP", 80, "Mage", cost=120, min_level=6),
        Item("Mana Crystal", "Accessory", "Attack", 15, "Mage", cost=100, min_level=6),
        Item("Silk Shoes", "Boots", "HP", 30, "Mage", cost=80, min_level=6),
        Item("Wizard Hat", "Helmet", "Defense", 10, "Mage", cost=100, min_level=6),
        # Tier 3 (Lvl 16-30)
        Item("Arcane Scepter", "Weapon", "Attack", 80, "Mage", cost=500, min_level=16),
        Item("Sage's Vestments", "Armor", "HP", 250, "Mage", cost=400, min_level=16),
        Item("Void Orb", "Accessory", "Attack", 40, "Mage", cost=300, min_level=16),
        Item("Enchanted Boots", "Boots", "HP", 100, "Mage", cost=300, min_level=16),
        Item("Archmage Crown", "Helmet", "Defense", 30, "Mage", cost=350, min_level=16),
        # Tier 4 (Lvl 31+)
        Item("Staff of Eternity", "Weapon", "Attack", 200, "Mage", cost=1800, min_level=31),
        Item("Astral Raiment", "Armor", "HP", 700, "Mage", cost=1200, min_level=31),
        Item("Eye of the Cosmos", "Accessory", "Attack", 100, "Mage", cost=800, min_level=31),
        Item("Celestial Boots", "Boots", "HP", 200, "Mage", cost=800, min_level=31),
        Item("Cosmic Tiara", "Helmet", "Defense", 80, "Mage", cost=1000, min_level=31),
        # Tier 5 (Lvl 50-100)
        Item("Staff of the Astral Void", "Weapon", "Attack", 300, "Mage", "damage_mult", cost=5000, min_level=50, set_name="Astral Void"),
        Item("Robe of Seven Stars", "Armor", "HP", 1000, "Mage", "hp_regen", cost=4000, min_level=50, set_name="Astral Void"),
        Item("Eye of the Abyss", "Accessory", "Attack", 100, "Mage", "crit_chance", cost=3000, min_level=50, set_name="Astral Void"),
        Item("Ether-Walkers", "Boots", "HP", 150, "Mage", "speed_mult", cost=2000, min_level=50, set_name="Astral Void"),
        Item("Hat of Infinite Wisdom", "Helmet", "Defense", 80, "Mage", "crit_multiplier", cost=2500, min_level=50, set_name="Astral Void"),
        # Tier 6 (Lvl 100+)
        Item("Cosmic Singularity Wand", "Weapon", "Attack", 800, "Mage", "damage_mult", cost=15000, min_level=100, set_name="Cosmic Singularity"),
        Item("Mantel of the Universe", "Armor", "HP", 3000, "Mage", "hp_regen", cost=12000, min_level=100, set_name="Cosmic Singularity"),
        Item("Heart of the Nebula", "Accessory", "Attack", 400, "Mage", "crit_chance", cost=10000, min_level=100, set_name="Cosmic Singularity"),
        Item("Stellar-Step Slippers", "Boots", "HP", 400, "Mage", "speed_mult", cost=8000, min_level=100, set_name="Cosmic Singularity"),
        Item("Crown of the Arcane God", "Helmet", "Defense", 300, "Mage", "crit_multiplier", cost=9000, min_level=100, set_name="Cosmic Singularity"),
    ],
    "Rogue": [
        # Tier 1 (Lvl 1-5)
        Item("Rusty Shank", "Weapon", "Attack", 12, "Rogue", cost=40, min_level=1),
        Item("Cloth Wrap", "Armor", "HP", 20, "Rogue", cost=30, min_level=1),
        Item("Leather Pouch", "Accessory", "Attack", 8, "Rogue", cost=20, min_level=1),
        Item("Soft Boots", "Boots", "HP", 10, "Rogue", cost=20, min_level=1),
        Item("Mask", "Helmet", "Defense", 2, "Rogue", cost=20, min_level=1),
        # Tier 2 (Lvl 6-15)
        Item("Steel Daggers", "Weapon", "Attack", 35, "Rogue", cost=160, min_level=6),
        Item("Studded Leather", "Armor", "HP", 100, "Rogue", cost=120, min_level=6),
        Item("Shadow Cloak", "Accessory", "Attack", 20, "Rogue", cost=100, min_level=6),
        Item("Quiet Boots", "Boots", "HP", 40, "Rogue", cost=80, min_level=6),
        Item("Thief's Hood", "Helmet", "Defense", 12, "Rogue", cost=100, min_level=6),
        # Tier 3 (Lvl 16-30)
        Item("Obsidian Blades", "Weapon", "Attack", 90, "Rogue", cost=500, min_level=16),
        Item("Midnight Armor", "Armor", "HP", 280, "Rogue", cost=400, min_level=16),
        Item("Phantom Ring", "Accessory", "Attack", 50, "Rogue", cost=300, min_level=16),
        Item("Shadow-Step Boots", "Boots", "HP", 120, "Rogue", cost=300, min_level=16),
        Item("Assassin's Mask", "Helmet", "Defense", 35, "Rogue", cost=350, min_level=16),
        # Tier 4 (Lvl 31+)
        Item("Soul-Reaper's Edge", "Weapon", "Attack", 220, "Rogue", cost=1700, min_level=31),
        Item("Void-Walker's Suit", "Armor", "HP", 750, "Rogue", cost=1100, min_level=31),
        Item("Eternal Stealth", "Accessory", "Attack", 120, "Rogue", cost=900, min_level=31),
        Item("Ghost-Walk Boots", "Boots", "HP", 200, "Rogue", cost=800, min_level=31),
        Item("Night-Slayer's Hood", "Helmet", "Defense", 90, "Rogue", cost=1000, min_level=31),
        # Tier 5 (Lvl 50-100)
        Item("Ghost-Steel Daggers", "Weapon", "Attack", 350, "Rogue", "crit_chance", cost=5000, min_level=50, set_name="Ghost-Steel"),
        Item("Shroud of Shadows", "Armor", "HP", 800, "Rogue", "speed_dodge_mult", cost=4000, min_level=50, set_name="Ghost-Steel"),
        Item("Nightshade Ring", "Accessory", "Attack", 120, "Rogue", "poison", cost=3000, min_level=50, set_name="Ghost-Steel"),
        Item("Wind-Runner Boots", "Boots", "HP", 150, "Rogue", "speed_mult", cost=2000, min_level=50, set_name="Ghost-Steel"),
        Item("Mask of the Unseen", "Helmet", "Defense", 70, "Rogue", "crit_multiplier", cost=2500, min_level=50, set_name="Ghost-Steel"),
        # Tier 6 (Lvl 100+)
        Item("Dimensional Ripper", "Weapon", "Attack", 900, "Rogue", "crit_chance", cost=15000, min_level=100, set_name="Dimensional"),
        Item("Void-Stalker Suit", "Armor", "HP", 2500, "Rogue", "speed_dodge_mult", cost=12000, min_level=100, set_name="Dimensional"),
        Item("Eye of the Serpent", "Accessory", "Attack", 450, "Rogue", "poison", cost=10000, min_level=100, set_name="Dimensional"),
        Item("Phase-Shift Boots", "Boots", "HP", 400, "Rogue", "speed_mult", cost=8000, min_level=100, set_name="Dimensional"),
        Item("Hood of Eternal Night", "Helmet", "Defense", 250, "Rogue", "crit_multiplier", cost=9000, min_level=100, set_name="Dimensional"),
    ],
}

def save_game(player):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(player.to_dict(), f)
        return True
    except Exception:
        return False

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return Player.from_dict(data)
    except Exception:
        return None

def generate_loot(player):
    player_class = player.player_class
    all_items = SHOP_ITEMS[player_class]

    eligible = [item for item in all_items if item.min_level <= player.total_levels]
    advanced = [item for item in all_items if item.min_level > player.total_levels]

    if not eligible and not advanced:
        return None

    # 80% chance for eligible, 20% for advanced (if any)
    if advanced and random.random() < 0.2:
        template = random.choice(advanced)
    elif eligible:
        template = random.choice(eligible)
    else:
        template = random.choice(advanced)

    # Roll for rarity
    rarity_roll = random.random()
    if rarity_roll < 0.05:
        rarity = "Legendary"
    elif rarity_roll < 0.15:
        rarity = "Epic"
    elif rarity_roll < 0.40:
        rarity = "Rare"
    else:
        rarity = "Common"

    return Item(
        template.name,
        template.item_type,
        template.bonus_type,
        template.bonus_value,
        template.required_class,
        template.passive,
        template.cost,
        template.min_level,
        rarity=rarity
    )


def make_lobby_panel(player):
    content = (
        f"[center][bold magenta]Welcome to the Hero's Lodge[/]\n"
        f"[center]----------------------------------\n"
        f" [bold cyan]Hero:[/ ] {player.name} | [bold cyan]Class:[/ ] {player.player_class}\n"
        f" [bold cyan]Total Level:[/ ] {player.total_levels} | [bold cyan]Gold:[/ ] {player.gold}\n"
        f"----------------------------------\n"
        f"[bold yellow]Ready for a challenge?[/]\n"
        f"Press [bold green]'b'[/] to begin a Battle Run\n"
        f"Press [bold green]'s'[/] for the Shop\n"
        f"Press [bold green]'e'[/] for Equipment\n"
        f"Press [bold green]'q'[/] to Quit\n"
        f"\n[dim]In menus, press 'b' to return here. In battle, press 'r' to retreat.[/]"
    )
    return Panel(content, title="Lobby")

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", size=30),
        Layout(name="footer", size=8)
    )
    return layout

def make_skill_table(player):
    table = Table(title="Skills", expand=True)
    table.add_column("Skill")
    table.add_column("Level")
    table.add_column("Progress")

    for name, skill in player.skills.items():
        bar_width = 20
        filled = int(skill.progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        skill_display = f"[bold cyan]{name}[/]" if name == player.active_skill_name else name
        table.add_row(skill_display, str(skill.level), bar)

    return table

def make_shop_panel(player):
    skill_table = Table(title="Skill Upgrades", expand=True)
    skill_table.add_column("Skill")
    skill_table.add_column("Current Mult")
    skill_table.add_column("Cost")
    skill_table.add_column("Key")

    skills_list = ["Strength", "Agility", "Intelligence", "Constitution"]
    for i, name in enumerate(skills_list, 1):
        skill = player.skills[name]
        cost = skill.level * 10 + 20
        skill_table.add_row(name, f"{skill.multiplier:.2f}x", f"{cost} Gold", str(i))

    item_table = Table(title="Equipment Shop (Level-Locked)", expand=True)
    item_table.add_column("Item")
    item_table.add_column("Type")
    item_table.add_column("Bonus")
    item_table.add_column("Cost")
    item_table.add_column("Key")

    # Filter items by level and sort by level (highest first)
    class_items = SHOP_ITEMS.get(player.player_class, [])
    available_items = [item for item in class_items if item.min_level <= player.total_levels]
    available_items.sort(key=lambda x: x.min_level, reverse=True)

    # Show only up to 5 items to fit keys 5-9
    display_items = available_items[:5]
    for i, item in enumerate(display_items, 5):
        # Shop items are Common by default
        item_table.add_row(item.name, item.item_type, f"{item.bonus_type} +{item.bonus_value}", f"{item.cost} Gold", str(i))

    sell_table = Table(title="Sell Items (Press 'x' to sell first item)", expand=True)
    sell_table.add_column("No.")
    sell_table.add_column("Item")
    sell_table.add_column("Sell Price")

    for i, item in enumerate(player.inventory, 1):
        price = 10 + (item.bonus_value * 2)
        # Color the item name by rarity
        rarity_color = {
            "Common": "white",
            "Rare": "blue",
            "Epic": "purple",
            "Legendary": "orange"
        }.get(item.rarity, "white")
        item_display = f"[{rarity_color}]{item.name}[/]"
        sell_table.add_row(str(i), item_display, f"{price} Gold")

    if not player.inventory:
        sell_table.add_row("-", "No items to sell", "-")

    return Panel(Group(skill_table, item_table, sell_table), title="General Store")

def make_combat_panel(player, monsters, wave):
    if not monsters:
        return Panel("[center]Preparing for battle...[/]", title=f"Combat - Wave {wave}")

    p_hp_pct = player.hp / player.max_hp
    p_bar_width = 20
    p_bar = "█" * int(p_hp_pct * p_bar_width) + "░" * (p_bar_width - int(p_hp_pct * p_bar_width))

    content = f"Player (Lvl {player.total_levels}) HP: [{p_bar}] {int(player.hp)}/{player.max_hp}\n\n"

    for i, m in enumerate(monsters):
        m_hp_pct = m.hp / m.max_hp
        m_bar = "█" * int(m_hp_pct * 20) + "░" * (20 - int(m_hp_pct * 20))
        # Highlight the targeted monster
        marker = "[bold red]> [/]" if i == 0 else "  "
        content += f"{marker}Enemy {i+1} ({m.name} Lvl {m.level}) HP: [{m_bar}] {int(m.hp)}/{int(m.max_hp)}\n"

    content += "\n[bold yellow]Battle in progress...[/]"
    return Panel(content, title=f"Combat - Wave {wave}")


def make_equipment_panel(player):
    eq_table = Table(title="Equipped Items", expand=True)
    eq_table.add_column("Slot")
    eq_table.add_column("Item")
    eq_table.add_column("Bonus")

    has_equipment = False
    for slot, item in player.equipment.items():
        if item:
            rarity_color = {
                "Common": "white",
                "Rare": "blue",
                "Epic": "purple",
                "Legendary": "orange"
            }.get(item.rarity, "white")
            item_display = f"[{rarity_color}]{item.name}[/]"
            eq_table.add_row(slot, item_display, f"{item.bonus_type} +{item.effective_bonus}")
            has_equipment = True

    if not has_equipment:
        eq_table.add_row("-", "No items equipped", "-")

    inv_table = Table(title="Inventory (Press 1-9 to equip)", expand=True)
    inv_table.add_column("No.")
    inv_table.add_column("Item")
    inv_table.add_column("Type")
    inv_table.add_column("Bonus")

    for i, item in enumerate(player.inventory, 1):
        rarity_color = {
            "Common": "white",
            "Rare": "blue",
            "Epic": "purple",
            "Legendary": "orange"
        }.get(item.rarity, "white")
        item_display = f"[{rarity_color}]{item.name}[/]"
        inv_table.add_row(str(i), item_display, item.item_type, f"{item.bonus_type} +{item.effective_bonus}")

    if not player.inventory:
        inv_table.add_row("-", "No items in inventory", "-", "-")

    return Panel(Group(eq_table, inv_table), title="Equipment & Inventory")

def pick_class():
    console = Console()
    console.print("[bold magenta]Welcome to Terminal Knight![/]\n")
    console.print("Choose your class:")
    console.print("1. [bold green]Warrior[/] (Stronger Strength & Constitution)")
    console.print("2. [bold blue]Mage[/] (Stronger Intelligence)")
    console.print("3. [bold yellow]Rogue[/] (Stronger Agility)")

    choice = Prompt.ask("Enter 1, 2, or 3", choices=["1", "2", "3"])
    classes = {"1": "Warrior", "2": "Mage", "3": "Rogue"}
    return classes[choice]

def main():
    console = Console()
    combat_log = CombatLog()

    player = None
    if os.path.exists(SAVE_FILE):

        load_choice = Prompt.ask("Save game found! Load it?", choices=["y", "n"])
        if load_choice == "y":
            player = load_game()
            if player:
                console.print("[bold green]Game loaded successfully![/]")
                player.heal()

    if player is None:
        player_class = pick_class()
        player = Player("Hero", player_class)
        player.heal()

    layout = make_layout()
    last_time = time.time()
    log_queue = deque([f"Welcome, {player.name}!", "1-4: Switch skills | b: Battle (when in lobby) | s: Shop | e: Equip | b: Back to lobby | a: Ability | r: Retreat (in battle) |q: Quit"])
    display_log = []

    game_state = "LOBBY" # "LOBBY", "BATTLE_RUN", "SHOP", or "EQUIPMENT"
    current_monsters = []
    target_index = 0
    run_wave = 1
    combat_timer = 0
    monster_ability_timer = 0
    poison_ticks = 0
    regen_timer = 0
    active_event = None
    event_timer = 0

    with Live(layout, refresh_per_second=10, screen=True):
        while True:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            if game_state == "LOBBY":
                pass # No automatic updates in lobby

            elif game_state == "BATTLE_RUN":
                if not player.hp > 0:
                    log_queue.append("[bold red]You were defeated![/]")
                    log_queue.append("Returning to lobby to recover...")
                    current_monsters = []
                    game_state = "LOBBY"
                    run_wave = 1
                    player.heal()
                    player.invulnerable_turns = 0
                    poison_ticks = 0
                    active_event = None
                elif current_monsters:
                    # Update targeting: default to lowest HP
                    if not (0 <= target_index < len(current_monsters)):
                        target_index = 0

                    # target = current_monsters[target_index]

                    combat_timer += delta_time
                    regen_timer += delta_time
                    monster_ability_timer += delta_time
                    player.update_cooldowns(delta_time)

                    # World Event Logic
                    if active_event:
                        event_timer -= delta_time
                        if event_timer <= 0:
                            log_queue.append(f"[bold yellow]The {active_event} has ended.[/]")
                            active_event = None

                    # Trigger event every 100 waves (chance-based)
                    if run_wave % 100 == 0 and active_event is None:
                        if random.random() < 0.3: # 30% chance to trigger event at 100-wave marks
                            active_event = random.choice(list(WORLD_EVENTS.keys()))
                            event_timer = 30 # Event lasts 30 seconds
                            event_data = WORLD_EVENTS[active_event]
                            log_queue.append(f"[bold {event_data['color']}]WORLD EVENT: {active_event}![/]")
                            log_queue.append(f"[dim]{event_data['desc']}[/]")

                    # Periodic effects (Every 1.0s)
                    if regen_timer >= 1.0:
                        regen_timer = 0
                        # HP Regen
                        regen_val = player.get_total_passive("hp_regen")
                        if active_event == "Mana Storm":
                            regen_val *= WORLD_EVENTS["Mana Storm"]["int_mult"]
                        if regen_val > 0:
                            player.current_hp = min(player.max_hp, player.current_hp + regen_val)
                            log_queue.append(f"You regenerated {int(regen_val)} HP!")

                        # Poison DoT
                        if poison_ticks > 0:
                            if current_monsters:
                                target = current_monsters[target_index] if (0 <= target_index < len(current_monsters)) else current_monsters[0]
                                poison_dmg = 5 + (target.level * 2)
                                actual_poison_dmg = target.take_damage(poison_dmg)
                                log_queue.append(f"{target.name} takes {actual_poison_dmg} poison damage!")
                            poison_ticks -= 1

                        # Debuff Ticking
                        for debuff in player.active_debuffs[:]:
                            debuff["duration"] -= 1
                            if debuff["duration"] <= 0:
                                player.active_debuffs.remove(debuff)

                    # Monster Ability Logic
                    if monster_ability_timer >= 2.0:
                        monster_ability_timer = 0
                        # Every monster gets a chance to use an ability
                        for monster in current_monsters:
                            available_abilities = [a for a in monster.abilities if monster.ability_cooldowns.get(a["name"], 0) <= 0]
                            if available_abilities:
                                ability = random.choice(available_abilities)
                                monster.ability_cooldowns[ability["name"]] = ability["cooldown"]

                                log_queue.append(f"[bold red]{monster.name} uses {ability['name']}![/]")

                                if ability["type"] == "atk_reduction":
                                    player.apply_debuff("atk_reduction", ability["value"], ability["duration"])
                                    log_queue.append(combat_log.get_message("debuff_applied"))
                                elif ability["type"] == "dmg_reduction":
                                    player.apply_debuff("dmg_reduction", ability["value"], ability["duration"])
                                    log_queue.append(f"The enemy shields themselves! Damage reduced.")
                                elif ability["type"] == "heal":
                                    heal_amt = monster.max_hp * ability["value"]
                                    monster.hp = min(monster.max_hp, monster.hp + heal_amt)
                                    log_queue.append(f"{monster.name} drains your life to heal {int(heal_amt)} HP!")

                    # Attack Speed calculation
                    base_interval = 1.0 / (1 + (player.skills["Agility"].level * 0.1))
                    speed_mult = player.get_total_passive("speed_mult") + player.get_total_passive("speed_dodge_mult")
                    attack_interval = max(0.2, base_interval / (1 + speed_mult))

                    if combat_timer >= attack_interval:
                        combat_timer = 0

                        if not (0 <= target_index < len(current_monsters)):
                            target_index = 0
                        target = current_monsters[target_index]

                        dmg_obj, is_crit = player.calculate_attack()
                        actual_dmg = target.take_damage(dmg_obj, attacker=player)

                        log_msg = combat_log.get_message("player_hit", target=target.name, dmg=actual_dmg)
                        if is_crit:
                            log_msg += f" [bold red]{combat_log.get_message('crit')}[/]"
                        log_queue.append(log_msg)

                        # Lifesteal Logic
                        lifesteal_mult = player.get_total_passive("lifesteal")
                        if lifesteal_mult > 0:
                            heal_amt = actual_dmg * lifesteal_mult
                            player.current_hp = min(player.max_hp, player.current_hp + heal_amt)
                            log_queue.append(combat_log.get_message("lifesteal", amt=int(heal_amt)))

                        # Poison Application
                        poison_chance = player.get_total_passive("poison")
                        if random.random() < poison_chance:
                            poison_ticks = 5
                            log_queue.append(f"[bold green]You poisoned {target.name}![/]")

                        # Dodge Logic
                        dodge_chance = (player.skills["Agility"].level * 0.01) + \
                                       player.get_total_passive("dodge_mult") + \
                                       player.get_total_passive("speed_dodge_mult")

                        dodge_chance = min(0.5, dodge_chance)

                        if random.random() < dodge_chance:
                            log_queue.append(combat_log.get_message("dodge"))
                        else:
                            # All monsters in the group get a chance to attack back
                            for monster in current_monsters:
                                p_dmg = monster.attack
                                if active_event == "Blood Moon":
                                    p_dmg *= WORLD_EVENTS["Blood Moon"]["atk_mult"]

                                # Monster event dodge
                                if active_event == "Void Rift" and random.random() < WORLD_EVENTS["Void Rift"]["dodge_chance"]:
                                    log_queue.append(f"[bold magenta]The monster vanishes into the rift![/]")
                                else:
                                    player.take_damage(p_dmg, attacker=monster)
                                    log_queue.append(combat_log.get_message("monster_hit", attacker=monster.name, dmg=p_dmg))

                        if target.hp <= 0:
                            # Victory Rewards
                            gold_mult = player.get_total_passive("gold_mult")
                            if active_event:
                                gold_mult += WORLD_EVENTS[active_event].get("gold_mult", 1.0) - 1.0

                            gold_won = int(target.gold_reward * (1 + gold_mult))
                            player.gold += gold_won
                            player.monsters_killed += 1

                            # Grant XP to active skill (and a bit to others)
                            xp_gain = 20 + (target.level * 5)
                            success, new_lvl = player.grant_xp(player.active_skill_name, xp_gain)
                            if success:
                                log_queue.append(f"[bold green]Level Up! {player.active_skill_name} is now level {new_lvl}![/]")

                            # Loot Roll (20% chance, but guaranteed Legendary for Super Bosses)
                            if (target.is_super_boss if hasattr(target, 'is_super_boss') else False) or random.random() < 0.2:
                                loot = generate_loot(player)
                                if hasattr(target, 'is_super_boss') and target.is_super_boss:
                                    loot.rarity = "Legendary"
                                player.inventory.append(loot)
                                log_queue.append(f"[bold gold1]Loot found: {loot.name} ([{loot.rarity}])![/]")

                            log_queue.append(f"[bold green]Victory! Gained {gold_won} gold and {xp_gain} XP![/]")

                            # Remove monster and adjust target
                            current_monsters.remove(target)
                            if not current_monsters:
                                # Prepare next wave
                                run_wave += 1
                                log_queue.append(f"[bold magenta]Entering Wave {run_wave}...[/]")
                                player.invulnerable_turns = 0
                                poison_ticks = 0
                            else:
                                # Target the next available monster (clamp index)
                                target_index = min(target_index, len(current_monsters) - 1)
                                log_queue.append(f"[bold magenta]Targeting {current_monsters[target_index].name}...[/]")
                else:
                    # Spawn next monster based on run_wave
                    is_super_boss = run_wave % 500 == 0
                    is_boss = (run_wave % 10 == 0) and not is_super_boss
                    monster_lvl = 1 + (run_wave // 3)
                    m_name = random.choice([
                        "Slime", "Goblin", "Skeleton", "Orc",
                        "Dire Wolf", "Shadow Stalker", "Void Wraith",
                        "Stone Golem", "Fungal Horror", "Blood Bat"
                    ])
                    if is_super_boss:
                        m_name = f"Primordial {m_name}"
                        log_queue.append(f"[bold gold1]A SUPER BOSS APPEARS: {m_name} (Lvl {monster_lvl})![/]")
                    elif is_boss:
                        m_name = f"Elite {m_name}"
                        log_queue.append(f"[bold red]A BOSS APPEARS: {m_name} (Lvl {monster_lvl})![/]")
                    else:
                        log_queue.append(f"A wild {m_name} (Lvl {monster_lvl}) appeared!")

                    # FIX: Append to list instead of assigning to local variable
                    current_monsters.append(Monster(m_name, monster_lvl, is_boss=is_boss, is_super_boss=is_super_boss, wave=run_wave))

                    player.invulnerable_turns = 0

            if msvcrt.kbhit():
                raw_key = msvcrt.getch()
                # Handle special keys (arrows, etc) which start with 0x00 or 0xE0
                if raw_key in (b'\x00', b'\xe0'):
                    # Consume the second byte of the sequence
                    second_byte = msvcrt.getch()
                    key = f"special_{raw_key.hex()}_{second_byte.hex()}"
                else:
                    try:
                        key = raw_key.decode('utf-8').lower()
                    except UnicodeDecodeError:
                        key = 'unknown'
                if key == 'q':
                    save_game(player)
                    break
                elif key == 'b':
                    if game_state == "LOBBY":
                        game_state = "BATTLE_RUN"
                        run_wave = 1
                        current_monsters = [] # Will spawn in next frame
                        log_queue.append("[bold magenta]Starting a Battle Run! Good luck, Hero![/]")
                    elif game_state in ["SHOP", "EQUIPMENT"]:
                        game_state = "LOBBY"
                        log_queue.append("Returned to the lobby.")
                elif key == 'r':
                    if game_state == "BATTLE_RUN":
                        game_state = "LOBBY"
                        current_monsters = []
                        log_queue.append("[bold yellow]Retreated to the lobby with your spoils![/]")
                        player.heal()
                        player.invulnerable_turns = 0
                        poison_ticks = 0
                elif key == 's':
                    game_state = "SHOP"
                    log_queue.append("Entered the Shop.")
                elif key == 'e':
                    game_state = "EQUIPMENT"
                    log_queue.append("Opened equipment menu.")

                elif key == 'a':
                    if game_state == "BATTLE_RUN" and current_monsters:
                        if not (0 <= target_index < len(current_monsters)):
                            target_index = 0
                        target = current_monsters[target_index]

                        ability = player.use_ability(0)
                        if ability:
                            result = ability.execute(player, target)
                            log_queue.append(f"[bold magenta]{result}[/]")
                        else:
                            log_queue.append("[red]Ability on cooldown![/]")

                elif key == 'h':
                    if game_state == "BATTLE_RUN":
                        # Find first healing consumable in inventory
                        consumable = next((item for item in player.inventory if item.item_type == "Consumable" and item.bonus_type == "Heal"), None)
                        if consumable:
                            player.inventory.remove(consumable)
                            result = consumable.use(player)
                            log_queue.append(f"[bold green]{result}[/]")
                        else:
                            log_queue.append("[red]No healing potions left![/]")
                elif key == 'h':
                    if game_state == "BATTLE_RUN":
                        # Find first healing consumable in inventory
                        consumable = next((item for item in player.inventory if item.item_type == "Consumable" and item.bonus_type == "Heal"), None)
                        if consumable:
                            player.inventory.remove(consumable)
                            result = consumable.use(player)
                            log_queue.append(f"[bold green]{result}[/]")
                        else:
                            log_queue.append("[red]No healing potions left![/]")
                elif key in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    idx = int(key) - 1
                    if game_state == "SHOP":
                        if idx < 4: # Skill upgrades
                            success, cost, levels = player.buy_upgrade(["Strength", "Agility", "Intelligence", "Constitution"][idx])
                            if success:
                                msg = f"Upgraded {['Strength', 'Agility', 'Intelligence', 'Constitution'][idx]} for {cost} gold!"
                                if levels > 0:
                                    msg += f" [bold green]Instantly gained {levels} level(s)![/]"
                                log_queue.append(msg)
                            else:
                                log_queue.append("Not enough gold!")
                        elif idx < 9: # Equipment shop
                            item_idx = idx - 4
                            class_items = SHOP_ITEMS.get(player.player_class, [])
                            available_items = [item for item in class_items if item.min_level <= player.total_levels]
                            available_items.sort(key=lambda x: x.min_level, reverse=True)
                            display_items = available_items[:5]

                            if item_idx < len(display_items):
                                item = display_items[item_idx]
                                cost = item.cost
                                if player.gold >= cost:
                                    player.gold -= cost
                                    new_item = Item(item.name, item.item_type, item.bonus_type, item.bonus_value, item.required_class, item.passive, item.cost, item.min_level)
                                    player.inventory.append(new_item)
                                    log_queue.append(f"Bought {item.name} for {cost} gold!")
                                else:
                                    log_queue.append("Not enough gold!")
                            else:
                                log_queue.append("Item not available!")
                    elif game_state == "EQUIPMENT":
                        if idx < len(player.inventory):
                            item = player.inventory.pop(idx)
                            slot = item.item_type
                            old_item = player.equipment[slot]
                            if old_item:
                                player.inventory.append(old_item)
                            player.equipment[slot] = item
                            log_queue.append(f"Equipped {item.name}!")
                        else:
                            log_queue.append("Nothing to equip at this slot!")
                    else:
                        # Default training skill switch
                        if idx < 4:
                            player.set_active_skill(["Strength", "Agility", "Intelligence", "Constitution"][idx])
                        else:
                            log_queue.append("Invalid skill key!")
                elif key == 'x':
                    if game_state == "SHOP":
                        success, name, price = player.sell_item(0)
                        if success: log_queue.append(f"Sold {name} for {price} gold!")
                        else: log_queue.append("Nothing to sell!")

            # Process log queue to make messages appear one by one
            if log_queue:
                display_log.append(log_queue.popleft())
                if len(display_log) > 10:
                    display_log.pop(0)

            layout["header"].update(Panel(f"Player: [bold yellow]{player.name}[/] | Class: [bold magenta]{player.player_class}[/] | Total Level: [bold green]{player.total_levels}[/] | Gold: [bold gold1]{player.gold}[/]" + (f" | [bold {WORLD_EVENTS[active_event]['color']}]EVENT: {active_event}[/]" if active_event else "")))

            if game_state == "LOBBY":
                layout["main"].update(make_lobby_panel(player))
            elif game_state == "SHOP":
                layout["main"].update(make_shop_panel(player))
            elif game_state == "EQUIPMENT":
                layout["main"].update(make_equipment_panel(player))
            else:
                layout["main"].update(make_combat_panel(player, current_monsters, run_wave))


            layout["footer"].update(Panel("\n".join(display_log), title="Log"))
            time.sleep(0.1)

if __name__ == "__main__":
    main()
