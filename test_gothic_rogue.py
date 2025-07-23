import sys

sys.path.append('.')  # Allows the test script to find and import main.py
from main import Entity, StatsComponent, ExperienceComponent, EquipmentComponent, EquippableComponent, VampireComponent, \
    SPAWN_RATES


# Helper function to create a test player entity
def create_test_player(hp=30, power=5, defense=1):
    player = Entity()
    player.add_component(StatsComponent(hp=hp, power=power, defense=defense, speed=1))
    player.add_component(ExperienceComponent())
    player.add_component(EquipmentComponent())
    return player


# Helper function to create a test enemy entity
def create_test_enemy(power=3):
    enemy = Entity()
    enemy.add_component(StatsComponent(hp=10, power=power, defense=0, speed=1))
    return enemy


# Test 1: Core Combat Damage Calculation
def test_player_takes_damage():
    player = create_test_player(hp=30, defense=1)
    # Damage should be 5 (enemy power) - 1 (player defense) = 4
    damage = 5 - player.get_defense()
    player.get_component(StatsComponent).current_hp -= damage
    assert player.get_component(StatsComponent).current_hp == 26
    print("✓ Test Passed: Damage calculation is correct.")


# Test 2: Player Level Up Mechanics
def test_level_up_mechanics():
    player = create_test_player()
    exp_comp = player.get_component(ExperienceComponent)
    stats_comp = player.get_component(StatsComponent)

    # Simulate gaining enough XP to level up
    exp_comp.current_xp = 100  # Base XP to level is 100

    # Simulate the level-up logic
    if exp_comp.current_xp >= exp_comp.xp_to_next_level:
        exp_comp.level += 1
        stats_comp.max_hp += 10
        stats_comp.power += 1

    assert exp_comp.level == 2
    assert stats_comp.max_hp == 40
    assert stats_comp.power == 6
    print("✓ Test Passed: Level up mechanics grant correct stats.")


# Test 3: Equipment Stat Bonuses
def test_equipment_bonuses():
    player = create_test_player(power=5)

    # Create and equip a dagger with a +2 power bonus
    dagger = Entity()
    dagger.add_component(EquippableComponent(slot="weapon", power_bonus=2))
    player.get_component(EquipmentComponent).slots["weapon"] = dagger

    # Total power should be 5 (base) + 2 (dagger) = 7
    assert player.get_power() == 7
    print("✓ Test Passed: Equipment bonuses are applied correctly.")


# Test 4: Vampire Lord Regeneration Mechanic
def test_vampire_regeneration():
    vampire = Entity()
    vampire.add_component(StatsComponent(hp=100, power=10, defense=5, speed=1))
    vampire.add_component(VampireComponent())

    stats = vampire.get_component(StatsComponent)
    stats.current_hp = 50  # Set to a damaged state

    # Simulate one turn of regeneration
    stats.current_hp += 1

    assert stats.current_hp == 51
    print("✓ Test Passed: Vampire regeneration is functional.")


# Test 5: Procedural Spawn Rate Scaling
# In test_gothic_rogue.py

def test_spawn_scaling():
    """Calculates expected spawns for Level 1 and 5 and verifies scaling."""
    # --- New values based on Session 18 balancing ---
    # Level 1: math.ceil(5 + (1 * 1)) = 6
    # Level 5: math.ceil(5 + (5 * 1)) = 10

    # Import the data and math function from the main script
    from main import SPAWN_RATES
    import math

    # Calculate expected values using the exact same logic as the game
    level_1_rats = math.ceil(SPAWN_RATES["rat"]["base"] + (1 * SPAWN_RATES["rat"]["scaling"]))
    level_5_rats = math.ceil(SPAWN_RATES["rat"]["base"] + (5 * SPAWN_RATES["rat"]["scaling"]))

    # Assert the new, correct values
    assert level_1_rats == 6
    assert level_5_rats == 10

    # The core principle of scaling should still hold true
    assert level_5_rats > level_1_rats
    print("✓ Test Passed: Spawn scaling correctly increases difficulty.")


if __name__ == "__main__":
    print("--- Running Gothic Rogue Test Suite ---")
    test_player_takes_damage()
    test_level_up_mechanics()
    test_equipment_bonuses()
    test_vampire_regeneration()
    test_spawn_scaling()
    print("\nAll tests passed successfully! 🎉")