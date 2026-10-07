# Gameplay Depth Implementation Plan - Terminal Knight

## Overview
This plan details the transition of Terminal Knight from a simple 1v1 combat system to a deeper tactical experience featuring a flexible ability system, elemental damage, consumables, and multi-monster encounters.

## 1. Ability System
### Goal: Move from hardcoded class abilities to a flexible `Ability` class.
- **New `Ability` Class**:
    - Attributes: `name`, `cooldown`, `current_cooldown`, `damage_multiplier`, `effect_type` (dmg, heal, buff, debuff), `element` (link to Elemental System).
    - Method: `use(user, target)` to execute the effect.
    - Method: `update(delta_time)` to reduce `current_cooldown`.
- **Player Integration**:
    - Replace `self.ability_used` (boolean) with `self.abilities = []` (list of equipped Ability objects).
    - Add `self.ability_slots = 3`.
    - Implement `use_ability(slot_index)` method in `Player` class.
- **Monster Integration**:
    - Convert the existing `self.abilities` (dicts) in `Monster` to `Ability` objects.
- **Main Loop**:
    - In `main.py`, call `ability.update(delta_time)` for all equipped abilities.

## 2. Elemental System
### Goal: Implement `DamageType` and resistances.
- **Damage Types**:
    - Create an Enum or constant mapping for `DamageType`: `PHYSICAL`, `FIRE`, `ICE`, `LIGHTNING`, `VOID`.
- **Resistances**:
    - Add `self.resistances = {DamageType.PHYSICAL: 1.0, ...}` to `Player` and `Monster`.
    - Resistance values: `0.5` (50% reduction), `1.0` (neutral), `1.5` (extra damage).
- **Combat Integration**:
    - Update `calculate_attack` in `Player` to return `(damage, is_critical, damage_type)`.
    - Update `take_damage` in `Player` and `Monster` to accept `damage_type` and apply the resistance multiplier.
    - Modify `Monster` archetypes to have innate resistances (e.g., Brute resists Physical, Caster resists Void).

## 3. Consumables
### Goal: One-time use items for healing and buffs.
- **New `Consumable` Class**:
    - Inherit from `Item` or create a separate class.
    - Attributes: `effect_value`, `effect_type` (healing, temp_buff), `duration` (for buffs).
- **Usage System**:
    - Add a `use_item(index)` method to `Player`.
    - Create a new menu or keybind in `main.py` (e.g., 'i' for items) to use consumables during battle.
- **Integration**:
    - Add consumables to the `SHOP_ITEMS` list.

## 4. Multi-Monster Encounters
### Goal: Transition from `current_monster` to a list of monsters.
- **Engine Changes**:
    - In `main.py`, change `current_monster = None` to `current_monsters = []`.
    - Update monster spawning logic to spawn 1-3 monsters per wave.
- **Targeting System**:
    - Add `self.target_index = 0` to the battle state.
    - Implement targeting logic:
        - Default: Target lowest HP monster.
        - Manual: Add keybinds (e.g., 't') to switch targets.
- **UI Updates**:
    - Update `make_combat_panel` in `main.py` to iterate through `current_monsters` and display HP bars for all.
    - Highlight the currently targeted monster in the UI.

## Implementation Strategy & Sequencing

### Phase 1: Foundation (Elemental & Ability Classes)
1. Define `DamageType` constants.
2. Implement the `Ability` class.
3. Update `Player` and `Monster` to hold resistances and `Ability` objects.

### Phase 2: Combat Overhaul (Elemental & Multi-Monster)
1. Update `calculate_attack` and `take_damage` to support elemental multipliers.
2. Refactor `main.py` to handle `current_monsters` list instead of a single object.
3. Implement basic targeting (lowest HP).
4. Update the combat UI to show multiple enemies.

### Phase 3: Ability & Consumable Integration
1. Replace hardcoded class abilities with `Ability` objects.
2. Implement the cooldown tracking using `delta_time` in the main loop.
3. Implement the `Consumable` class and the `use_item` logic.
4. Add consumables to the shop.

### Phase 4: Polish & Compatibility
1. **Save Game Compatibility**:
    - Update `Player.to_dict` and `Player.from_dict` to handle new fields (`resistances`, `abilities`).
    - Provide default values in `from_dict` for missing fields to avoid crashing on old save files (e.g., `data.get("resistances", default_resistances)`).
2. Balance testing for elemental resistances and multi-monster scaling.

## Critical Files for Implementation
- `engine.py`: Primary logic for `Player`, `Monster`, `Ability`, and `DamageType`.
- `main.py`: Game loop, UI panels, and combat state management.
EOF`
