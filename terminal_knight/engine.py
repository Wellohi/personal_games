import math
import random
from enum import Enum, auto

class DamageType(Enum):
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    LIGHTNING = auto()
    VOID = auto()

class Damage:
    def __init__(self, value, damage_type=DamageType.PHYSICAL):
        self.value = value
        self.type = damage_type

RARITY_MULTIPLIERS = {
    "Common": 1.0,
    "Rare": 1.2,
    "Epic": 1.5,
    "Legendary": 2.0
}

class Ability:
    def __init__(self, name, cooldown, power_multiplier=1.0, damage_type=DamageType.PHYSICAL):
        self.name = name
        self.cooldown = cooldown
        self.current_cooldown = 0.0
        self.power_multiplier = power_multiplier
        self.damage_type = damage_type

    def execute(self, player, target):
        # Base implementation to be overridden by subclasses
        return None

class WarriorAbility(Ability):
    def execute(self, player, target):
        # Double Hit: Hit twice for slightly reduced damage
        hits = 2
        total_dmg = 0
        for _ in range(hits):
            dmg, _ = player.calculate_attack()
            # dmg is a Damage object; multiply its value
            reduced_dmg = Damage(dmg.value * 0.75, dmg.type)
            actual = target.take_damage(reduced_dmg, attacker=player)
            total_dmg += actual
        return f"Ability: Double Hit! Dealt total {int(total_dmg)} damage!"

class MageAbility(Ability):
    def execute(self, player, target):
        # Arcane Blast: High damage Fire attack
        dmg, _ = player.calculate_attack()
        final_dmg = Damage(dmg * self.power_multiplier, DamageType.FIRE)
        actual = target.take_damage(final_dmg, attacker=player)
        return f"Ability: Arcane Blast! Dealt {int(actual)} Fire damage!"

class RogueAbility(Ability):
    def execute(self, player, target):
        # Shadow Step: Invulnerability for a few turns (managed via player state)
        player.invulnerable_turns = 2
        return "Ability: Shadow Step! You are invulnerable for 2 attacks!"

class CombatLog:

    TEMPLATES = {
        "player_hit": [
            "⚔️ You strike {target} for {dmg}!",
            "⚔️ A powerful blow deals {dmg} to {target}!",
            "⚔️ You deliver a surprisingly competent blow of {dmg} to {target}!",
            "⚔️ You hit {target}, and they look mildly inconvenienced by the {dmg} damage.",
            "⚔️ A solid hit! You can almost hear {target}'s confidence wavering. ({dmg} dmg)"
        ],
        "monster_hit": [
            "💥 {attacker} lashes out for {dmg}!",
            "💥 {attacker} claws you for {dmg}!",
            "💥 {attacker} hits you, and it actually kind of hurts! ({dmg} dmg)",
            "💥 The enemy connects with a clumsy but effective blow for {dmg}!",
            "💥 You take a hit from {attacker}, but you've had worse. ({dmg} dmg)"
        ],
        "crit": [
            "🔥 [bold red]CRITICAL HIT![/]",
            "🔥 [bold red]A devastating strike![/]",
            "🔥 [bold red]Direct hit![/]",
            "🔥 [bold red]KABOOM! You hit a vital organ![/]",
            "🔥 [bold red]Absolute carnage![/]",
            "🔥 [bold red]You found a weak spot! Ouch.[/]"
        ],
        "dodge": [
            "💨 You dance out of the way with grace (mostly).",
            "💨 The enemy swings and hits nothing but air.",
            "💨 Whoosh! You're too fast for them!",
            "💨 A clumsy attempt by the monster. You barely move an inch."
        ],
        "ability_used": [
            "✨ You unleash your inner power!",
            "✨ A flurry of activity! You're unstoppable!",
            "✨ Magic/Steel/Cunning in action!",
            "✨ You execute a masterful maneuver!"
        ],
        "debuff_applied": [
            "🌀 The monster's attack leaves you feeling sluggish!",
            "🌀 A strange energy clings to you, weakening your resolve!",
            "🌀 You feel a sudden chill... your power is waning!",
            "🌀 The enemy's scream rattles your brain!"
        ],
        "lifesteal": [
            "❤️ Lifesteal healed you for {amt} HP!",
            "❤️ You drain some vitality from the enemy: +{amt} HP!",
            "❤️ A bit of health returns to you as you strike: +{amt} HP!"
        ],
        "thorns": [
            "🌵 Your armor spikes deal {dmg} back to {target}!",
            "🌵 The enemy hurts themselves attacking you! {dmg} dmg",
            "🌵 Thorns reflect {dmg} damage back to {target}!"
        ]
    }

    def get_message(self, event, **kwargs):
        templates = self.TEMPLATES.get(event, ["..."])
        return random.choice(templates).format(**kwargs)

class Skill:
    def __init__(self, name, base_gain_rate=0.1):
        self.name = name
        self.level = 1
        self.progress = 0.0  # 0.0 to 1.0
        self.base_gain_rate = base_gain_rate
        self.multiplier = 1.0

    def get_xp_required(self):
        return 10 * (1.15 ** (self.level - 1))

    def add_xp(self, amount):
        gain = self.base_gain_rate * self.multiplier * amount
        self.progress += gain / self.get_xp_required()

        levels_gained = 0
        while self.progress >= 1.0:
            self.progress -= 1.0
            self.level += 1
            levels_gained += 1

        return levels_gained

    def boost_progress(self, percent):
        self.progress += percent
        levels_gained = 0
        while self.progress >= 1.0:
            self.progress -= 1.0
            self.level += 1
            levels_gained += 1
        return levels_gained

    def to_dict(self):
        return {
            "level": self.level,
            "progress": self.progress,
            "multiplier": self.multiplier
        }

    @classmethod
    def from_dict(cls, name, data):
        skill = cls(name)
        skill.level = data["level"]
        skill.progress = data["progress"]
        skill.multiplier = data["multiplier"]
        return skill

class Item:
    def __init__(self, name, item_type, bonus_type, bonus_value, required_class=None, passive=None, cost=0, min_level=1, rarity="Common", set_name=None):
        self.name = name
        self.item_type = item_type  # "Weapon", "Armor", "Shield", "Accessory", "Helmet", "Boots", "Consumable"
        self.bonus_type = bonus_type  # "Attack", "HP", "Defense", "Heal"
        self.bonus_value = bonus_value
        self.required_class = required_class  # "Warrior", "Mage", "Rogue", or None
        self.passive = passive  # e.g., "critical", "lifesteal", "thorns"
        self.cost = cost
        self.min_level = min_level
        self.rarity = rarity
        self.set_name = set_name

    @property
    def effective_bonus(self):
        return self.bonus_value * RARITY_MULTIPLIERS.get(self.rarity, 1.0)

    def to_dict(self):
        return {
            "name": self.name,
            "item_type": self.item_type,
            "bonus_type": self.bonus_type,
            "bonus_value": self.bonus_value,
            "required_class": self.required_class,
            "passive": self.passive,
            "cost": self.cost,
            "min_level": self.min_level,
            "rarity": self.rarity,
            "set_name": self.set_name
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["item_type"],
            data["bonus_type"],
            data["bonus_value"],
            data.get("required_class"),
            data.get("passive"),
            data.get("cost", 0),
            data.get("min_level", 1),
            data.get("rarity", "Common"),
            data.get("set_name")
        )

class Consumable(Item):
    def use(self, player):
        if self.bonus_type == "Heal":
            heal_amount = self.effective_bonus
            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
            return f"Used {self.name}, healed for {int(heal_amount)} HP!"
        return "Item had no usable effect."

class Monster:

    def __init__(self, name, level, is_boss=False, is_super_boss=False, wave=1):
        self.name = name
        self.level = level
        self.is_boss = is_boss
        self.is_super_boss = is_super_boss
        self.wave = wave

        # Define archetypes for variety
        archetypes = {
            "Brute": {"hp_mult": 1.5, "atk_mult": 1.0, "abilities": [{"name": "Shield", "cooldown": 12, "type": "dmg_reduction", "value": 0.4, "duration": 3}]},
            "Caster": {"hp_mult": 0.8, "atk_mult": 1.3, "abilities": [{"name": "Scream", "cooldown": 10, "type": "atk_reduction", "value": 0.3, "duration": 4}]},
            "Leech": {"hp_mult": 1.0, "atk_mult": 1.1, "abilities": [{"name": "Lifesteal", "cooldown": 12, "type": "heal", "value": 0.15}]},
            "Assassin": {"hp_mult": 0.9, "atk_mult": 1.4, "abilities": [{"name": "Shadow-step", "cooldown": 15, "type": "dmg_reduction", "value": 0.6, "duration": 2}]}
        }

        archetype_name = random.choice(list(archetypes.keys()))
        archetype = archetypes[archetype_name]

        # Assign abilities
        self.abilities = []
        self.ability_cooldowns = {}

        if is_boss:
            # Bosses get a mix of powerful abilities
            self.abilities = [
                {"name": "Scream", "cooldown": 8, "type": "atk_reduction", "value": 0.3, "duration": 4},
                {"name": "Shield", "cooldown": 12, "type": "dmg_reduction", "value": 0.5, "duration": 3},
                {"name": "Lifesteal", "cooldown": 10, "type": "heal", "value": 0.2}
            ]
        elif level > 5:
            # Regular monsters get their archetype ability
            self.abilities = archetype["abilities"]

        for abil in self.abilities:
            self.ability_cooldowns[abil["name"]] = 0

        # Resistances
        self.resistances = {
            DamageType.PHYSICAL: 1.0,
            DamageType.FIRE: 1.0,
            DamageType.ICE: 1.0,
            DamageType.LIGHTNING: 1.0,
            DamageType.VOID: 1.0,
        }
        # Randomize resistances slightly for variety
        for dtype in self.resistances:
            self.resistances[dtype] = random.uniform(0.8, 1.2)

        # Stats scale based on archetype, boss status, AND wave number
        # The wave_mult ensures that even if the level is similar, monsters in later waves are much tougher
        wave_hp_mult = 1 + (wave / 50)
        wave_atk_mult = 1 + (wave / 150)
        wave_def_mult = 1 + (wave / 500)

        hp_mult = (15 if is_super_boss else (3 if is_boss else 1)) * archetype["hp_mult"] * wave_hp_mult
        atk_mult = (5 if is_super_boss else (1.5 if is_boss else 1)) * archetype["atk_mult"] * wave_atk_mult
        gold_mult = 20 if is_super_boss else (3 if is_boss else 1)

        self.max_hp = (30 + (level * 15)) * hp_mult
        self.hp = self.max_hp
        self.attack = (2 + (level * 2)) * atk_mult
        self.defense = (0 + (level * 1)) * wave_def_mult
        self.gold_reward = (10 + (level * 10)) * gold_mult

    def take_damage(self, damage, attacker=None):
        if isinstance(damage, (int, float)):
            damage_val = damage
        elif isinstance(damage, Damage):
            # Apply elemental resistance
            mult = self.resistances.get(damage.type, 1.0) if hasattr(self, 'resistances') else 1.0
            damage_val = damage.value * mult
        else:
            damage_val = damage

        actual_damage = max(1, damage_val - self.defense)
        self.hp -= actual_damage
        return actual_damage

class Player:
    CLASSES = {
        "Warrior": {"Strength": 1.5, "Agility": 1.0, "Intelligence": 0.7, "Constitution": 1.2},
        "Mage": {"Strength": 0.7, "Agility": 1.0, "Intelligence": 1.5, "Constitution": 0.8},
        "Rogue": {"Strength": 1.0, "Agility": 1.5, "Intelligence": 1.0, "Constitution": 0.9},
    }

    def __init__(self, name, player_class="Warrior"):
        self.name = name
        self.player_class = player_class
        self.skills = {
            "Strength": Skill("Strength", 0.2),
            "Agility": Skill("Agility", 0.2),
            "Intelligence": Skill("Intelligence", 0.2),
            "Constitution": Skill("Constitution", 0.2),
        }

        modifiers = self.CLASSES.get(player_class, self.CLASSES["Warrior"])
        for name, skill in self.skills.items():
            skill.base_gain_rate *= modifiers.get(name, 1.0)

        self.active_skill_name = "Strength"
        self.total_levels = 4
        self.gold = 0
        self.unlocked_milestones = []
        self.current_hp = 0
        self.monsters_killed = 0
        self.hit_count = 0
        self.ability_used = False
        self.invulnerable_turns = 0
        self.active_debuffs = []

        # Resistances
        self.resistances = {
            DamageType.PHYSICAL: 1.0,
            DamageType.FIRE: 1.0,
            DamageType.ICE: 1.0,
            DamageType.LIGHTNING: 1.0,
            DamageType.VOID: 1.0,
        }

        # Abilities
        self.abilities = []
        if player_class == "Warrior":
            self.abilities = [WarriorAbility("Double Hit", 10, 1.0)]
        elif player_class == "Mage":
            self.abilities = [MageAbility("Arcane Blast", 8, 1.5, DamageType.FIRE)]
        elif player_class == "Rogue":
            self.abilities = [RogueAbility("Shadow Step", 15)]

        # Equipment slots
        self.equipment = {
            "Weapon": None,
            "Armor": None,
            "Shield": None,
            "Accessory": None,
            "Helmet": None,
            "Off-hand": None,
            "Boots": None
        }
        self.inventory = []

    def apply_debuff(self, debuff_type, value, duration):
        self.active_debuffs.append({"type": debuff_type, "value": value, "duration": duration})

    def get_set_bonuses(self):
        sets = {}
        for item in self.equipment.values():
            if item and item.set_name:
                sets[item.set_name] = sets.get(item.set_name, 0) + 1

        bonuses = {}
        # Define bonuses for 3+ items of a set
        set_defs = {
            "Sun-Shatter": {"crit_multiplier": 0.1},
            "Plate of Immortal": {"hp_regen": 0.001},
            "Astral Void": {"damage_mult": 0.15},
            "World-Ender": {"crit_multiplier": 0.2},
            "Cosmic Singularity": {"damage_mult": 0.2},
            "Dimensional": {"speed_dodge_mult": 0.1},
        }

        for set_name, count in sets.items():
            if count >= 3 and set_name in set_defs:
                bonuses.update(set_defs[set_name])

        return bonuses

    def get_total_passive(self, passive_name):
        total = 0.0
        # Base passive regen for all classes scaling with Intelligence
        if passive_name == "hp_regen":
            total += (self.skills["Intelligence"].level * 0.002) * self.max_hp

        # Equipment passives
        for item in self.equipment.values():
            if item and item.passive == passive_name:
                total += item.effective_bonus

        # Set bonuses
        set_bonuses = self.get_set_bonuses()
        total += set_bonuses.get(passive_name, 0.0)

        return total


    def heal(self):
        self.current_hp = self.max_hp

    def take_damage(self, damage, attacker=None):
        if self.invulnerable_turns > 0:
            self.invulnerable_turns -= 1
            return max(0, self.current_hp)

        reduction = 0
        if self.equipment["Armor"]:
            reduction = self.equipment["Armor"].effective_bonus if self.equipment["Armor"].bonus_type == "Defense" else 0

        # Apply dmg_reduction debuffs (actually buffs)
        dmg_mult = 1.0
        for debuff in self.active_debuffs:
            if debuff["type"] == "dmg_reduction":
                dmg_mult *= (1 - debuff["value"])

        # Damage range: damage +/- 10%
        min_dmg = damage * 0.9
        max_dmg = damage * 1.1
        actual_dmg_val = random.uniform(min_dmg, max_dmg)

        # Elemental processing
        if isinstance(damage, Damage):
            res = self.resistances.get(damage.type, 1.0)
            actual_dmg_val *= res
            base_val = damage.value
        else:
            base_val = damage

        actual_damage = max(0, (actual_dmg_val * dmg_mult) - reduction)
        self.current_hp -= actual_damage

        # Calculate reflected damage (Thorns)
        reflected_damage = 0
        thorns_mult = self.get_total_passive("thorns")
        if thorns_mult > 0:
            reflected_damage = actual_damage * thorns_mult

        if attacker and reflected_damage > 0:
            # To avoid infinite recursion, we pass attacker=None to the reflected attack
            attacker.take_damage(int(reflected_damage), attacker=None)

        return max(0, self.current_hp)

    def update_cooldowns(self, delta_time):
        for ability in self.abilities:
            if ability.current_cooldown > 0:
                ability.current_cooldown -= delta_time
                if ability.current_cooldown < 0:
                    ability.current_cooldown = 0

    def use_ability(self, index):
        if 0 <= index < len(self.abilities):
            ability = self.abilities[index]
            if ability.current_cooldown <= 0:
                ability.current_cooldown = ability.cooldown
                return ability
        return None

    def get_active_skill(self):
        return self.skills[self.active_skill_name]

    def grant_xp(self, skill_name, amount):
        if skill_name in self.skills:
            skill = self.skills[skill_name]
            levels_gained = skill.add_xp(amount)
            if levels_gained > 0:
                self.total_levels += levels_gained
                return True, skill.level
        return False, 0

    def check_milestones(self):
        milestones_defs = [
            ("Strength", 5, "Power Lift", lambda p: setattr(p.skills["Strength"], "multiplier", p.skills["Strength"].multiplier * 1.2)),
            ("Intelligence", 5, "Quick Study", lambda p: setattr(p, "global_bonus", 1.1)),
            ("Constitution", 5, "Toughness", lambda p: setattr(p, "hp_bonus", 20)),
            ("Agility", 5, "Nimble", lambda p: setattr(p.skills["Agility"], "multiplier", p.skills["Agility"].multiplier * 1.2)),
        ]

        for skill_name, level, reward_name, effect in milestones_defs:
            if skill_name not in self.unlocked_milestones and self.skills[skill_name].level >= level:
                self.unlocked_milestones.append(skill_name)
                effect(self)
                return f"Unlocked Milestone: [bold gold1]{reward_name}[/]!"
        return None

    def set_active_skill(self, name):
        if name in self.skills:
            self.active_skill_name = name

    def buy_upgrade(self, skill_name):
        skill = self.skills[skill_name]
        cost = int(20 * (1.15 ** skill.level) + skill.level * 10)
        if self.gold >= cost:
            self.gold -= cost
            skill.multiplier += 0.2
            levels_gained = skill.boost_progress(0.2)
            return True, cost, levels_gained
        return False, cost, 0

    def buy_upgrade_bulk(self, skill_name, amount):
        skill = self.skills[skill_name]
        total_cost = 0
        levels_gained_total = 0

        # Calculate total cost for 'amount' upgrades
        # We must simulate the level increase for cost calculation
        temp_level = skill.level
        for _ in range(amount):
            current_cost = int(20 * (1.15 ** temp_level) + temp_level * 10)
            total_cost += current_cost
            temp_level += 1 # Approximate level increase for cost simulation

        if self.gold >= total_cost:
            self.gold -= total_cost
            for _ in range(amount):
                skill.multiplier += 0.2
                levels_gained_total += skill.boost_progress(0.2)
            return True, total_cost, levels_gained_total
        return False, total_cost, 0

    def sell_item(self, index):
        if 0 <= index < len(self.inventory):
            item = self.inventory.pop(index)
            price = int(item.cost * 0.5) if item.cost > 0 else 10 + int(item.bonus_value * 2)
            self.gold += price
            return True, item.name, price
        return False, None, 0

    @property
    def attack_power(self):
        bonus = 0
        for item in self.equipment.values():
            if item and item.bonus_type == "Attack":
                bonus += item.effective_bonus

        if self.player_class == "Mage":
            base_dmg = self.skills["Intelligence"].level * 10
        else:
            base_dmg = self.skills["Strength"].level * 10

        # Apply debuffs
        for debuff in self.active_debuffs:
            if debuff["type"] == "atk_reduction":
                base_dmg *= (1 - debuff["value"])

        return base_dmg + bonus

    def calculate_attack(self):
        """Returns (Damage object, is_critical)"""
        self.hit_count += 1

        # Damage range: base_power +/- 10%
        base_power = self.attack_power
        min_dmg = base_power * 0.9
        max_dmg = base_power * 1.1
        damage_val = random.uniform(min_dmg, max_dmg)

        is_crit = False

        # 1. Critical Hit Chance
        crit_chance = self.get_total_passive("crit_chance")
        if random.random() < crit_chance:
            is_crit = True

        # 2. Critical Hit Cycle (Overrides or complements default)
        cycle_val = self.get_total_passive("crit_cycle")
        if not is_crit:
            if cycle_val > 0:
                if self.hit_count % int(cycle_val) == 0:
                    is_crit = True
            elif self.equipment["Weapon"] and self.equipment["Weapon"].passive == "critical":
                if self.hit_count % 4 == 0:
                    is_crit = True

        if is_crit:
            damage_val *= (2 + self.get_total_passive("crit_multiplier"))

        # 3. Damage Multiplier
        dmg_mult = self.get_total_passive("damage_mult")
        damage_val *= (1 + dmg_mult)

        return Damage(int(damage_val), DamageType.PHYSICAL), is_crit

    @property
    def max_hp(self):
        bonus = 0
        if "Constitution" in self.unlocked_milestones:
            bonus = 20
        for item in self.equipment.values():
            if item and item.bonus_type == "HP":
                bonus += item.effective_bonus

        base_hp = 100 + (self.skills["Constitution"].level * 20)
        if self.player_class == "Mage":
            base_hp += self.skills["Strength"].level

        return base_hp + bonus

    @property
    def hp(self):
        return self.current_hp

    def to_dict(self):
        return {
            "name": self.name,
            "player_class": self.player_class,
            "gold": self.gold,
            "total_levels": self.total_levels,
            "active_skill_name": self.active_skill_name,
            "unlocked_milestones": self.unlocked_milestones,
            "monsters_killed": self.monsters_killed,
            "hit_count": self.hit_count,
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "equipment": {slot: item.to_dict() if item else None for slot, item in self.equipment.items()},
            "inventory": [item.to_dict() for item in self.inventory],
            "resistances": {dtype.name: val for dtype, val in self.resistances.items()},
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"], data["player_class"])
        player.gold = data["gold"]
        player.total_levels = data["total_levels"]
        player.active_skill_name = data["active_skill_name"]
        player.unlocked_milestones = data["unlocked_milestones"]
        player.monsters_killed = data.get("monsters_killed", 0)
        player.hit_count = data.get("hit_count", 0)

        for name, skill_data in data["skills"].items():
            skill = Skill(name, base_gain_rate=0.2)
            skill.level = skill_data["level"]
            skill.progress = skill_data["progress"]
            skill.multiplier = skill_data["multiplier"]
            modifiers = cls.CLASSES.get(player.player_class, cls.CLASSES["Warrior"])
            skill.base_gain_rate *= modifiers.get(name, 1.0)
            player.skills[name] = skill

        # Resistances (with backward compatibility)
        res_data = data.get("resistances", {})
        player.resistances = {
            DamageType[name]: res_data.get(name, 1.0) for name in DamageType.__members__
        }

        if "equipment" in data:
            for slot, item_data in data["equipment"].items():
                if item_data:
                    player.equipment[slot] = Item.from_dict(item_data)

        if "inventory" in data:
            player.inventory = [Item.from_dict(item_data) for item_data in data["inventory"]]

        return player
