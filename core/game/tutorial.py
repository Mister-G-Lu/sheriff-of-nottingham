"""
Interactive Tutorial - Sandbox-style learning with replay capability
Players can try different choices, skip scenarios, and learn at their own pace
All content loaded from data/tutorial_content.json for easy editing
"""

import json
from pathlib import Path

from core.game.inspection_display import (
    show_bag_contents,
    show_bluff_succeeded,
    show_honest_verdict,
    show_inspection_footer,
    show_inspection_header,
    show_lying_verdict,
    show_merchant_sold_goods,
)
from core.mechanics.goods import GOOD_BY_ID
from core.mechanics.inspection import handle_inspection, handle_pass_without_inspection
from core.players.merchants import Merchant
from core.players.sheriff import Sheriff
from core.systems.game_stats import GameStats
from core.systems.reputation import update_sheriff_reputation
from ui.narration import show_inspection_result


def load_tutorial_content():
    """Load tutorial content from JSON file."""
    content_file = (
        Path(__file__).parent.parent.parent / "data" / "tutorial_content.json"
    )
    with open(content_file, encoding="utf-8") as f:
        return json.load(f)


def parse_scenario(scenario_data):
    """Parse scenario data and convert good names to Good objects."""
    scenario = scenario_data.copy()
    scenario["actual_goods"] = [
        GOOD_BY_ID[good_id] for good_id in scenario_data["actual_goods"]
    ]
    return scenario


def print_tutorial_welcome():
    """Print tutorial welcome message."""
    content = load_tutorial_content()
    welcome = content["welcome"]

    print("\n" + "=" * 70)
    print(welcome["header"])
    print("=" * 70)
    print(f"\n{welcome['description']}")
    print("You can:")
    for feature in welcome["features"]:
        print(f"  - {feature}")
    print(f"\n{welcome['encouragement']}")
    print("=" * 70)
    input(f"\n{welcome['prompt']}")


def print_scenario_header(scenario, content):
    """Print scenario introduction."""
    header = content["scenario_header"]
    print("\n" + "=" * 70)
    print(
        f"{header['prefix']} {scenario['id']}{header['separator']}{len(content['scenarios'])}: {scenario['name']}"
    )
    print("=" * 70)
    print(f"\n{scenario['intro']}")
    if "narrator_note" in scenario:
        print(f"\n{scenario['narrator_note']}")
    print("\n" + "-" * 70)


def show_merchant_arrival(scenario, content):
    """Show merchant arrival and declaration."""
    arrival = content["merchant_arrival"]
    print(f"\n{scenario['merchant_name']} {arrival['approaches']}")
    print(f"   {arrival['tell_label']} {scenario['tell']}")
    print(
        f"\n'{scenario['merchant_name']} {arrival['declares']} {scenario['declaration']['count']} {scenario['declaration']['good_id']}'"
    )

    if scenario["has_bribe"]:
        print(
            f"\n{scenario['merchant_name']} {arrival['bribe_offer']} {scenario['bribe_amount']}g bribe..."
        )


def show_tutorial_menu(scenario, content):
    """Show tutorial menu and get player choice."""
    menu = content["menu"]
    choices_text = menu["choices"]

    print("\n" + "-" * 70)
    print(menu["header"])
    print("-" * 70)
    print(f"1. {choices_text['pass']}")
    print(f"2. {choices_text['inspect']}")
    print(f"3. {choices_text['threaten']}")
    if scenario["has_bribe"]:
        print(f"4. {choices_text['accept_bribe']}")
        print(f"5. {choices_text['skip']}")
        print(f"6. {choices_text['exit']}")
    else:
        print(f"4. {choices_text['skip']}")
        print(f"5. {choices_text['exit']}")
    print("-" * 70)

    while True:
        choice = input(f"\n{menu['prompt']} (1-6): ").strip()
        if scenario["has_bribe"]:
            if choice in ["1", "2", "3", "4", "5", "6"]:
                return {
                    "1": "pass",
                    "2": "inspect",
                    "3": "threaten",
                    "4": "accept_bribe",
                    "5": "skip",
                    "6": "exit",
                }[choice]
        else:
            if choice in ["1", "2", "3", "4", "5"]:
                return {
                    "1": "pass",
                    "2": "inspect",
                    "3": "threaten",
                    "4": "skip",
                    "5": "exit",
                }[choice]
        print(content["messages"]["invalid_choice"])


def execute_tutorial_choice(choice, scenario, sheriff, stats, content):
    """Execute player's choice and show outcome with learning points."""
    exec_text = content["execution"]
    print("\n" + "=" * 70)
    print(f"{exec_text['header']}: {choice.upper().replace('_', ' ')}")
    print("=" * 70)

    merchant = Merchant(
        id="tutorial",
        name=scenario["merchant_name"],
        intro=scenario["description"],
        tells_honest=["calm"],
        tells_lying=["nervous"],
        bluff_skill=5,
        risk_tolerance=5,
        greed=5,
        honesty_bias=5,
    )

    actual_goods = scenario["actual_goods"]
    declaration = scenario["declaration"]
    all(g.id == declaration["good_id"] for g in actual_goods)

    if choice == "pass":
        result = handle_pass_without_inspection(
            merchant,
            actual_goods,
            {"good_id": declaration["good_id"], "count": declaration["count"]},
        )
        stats.record_pass(result["was_honest"])
        show_inspection_result(merchant, False, False)

        goods_value = sum(g.value for g in result["goods_passed"])
        merchant.gold += goods_value
        show_merchant_sold_goods(merchant.name, goods_value, merchant.gold)

        update_sheriff_reputation(
            sheriff, False, result["was_honest"], stats, actual_goods
        )

    elif choice == "inspect":
        result = handle_inspection(
            merchant,
            actual_goods,
            {"good_id": declaration["good_id"], "count": declaration["count"]},
            sheriff,
        )
        stats.record_inspection(result["was_honest"], result["caught_lie"])
        show_inspection_result(merchant, True, result["caught_lie"])

        show_inspection_header(
            merchant.name, declaration["count"], declaration["good_id"]
        )
        show_bag_contents(actual_goods)

        if not result["was_honest"] and not result["caught_lie"]:
            goods_value = sum(g.value for g in result["goods_passed"])
            merchant.gold += goods_value
            show_bluff_succeeded(merchant.name, goods_value, merchant.gold)
        elif result["was_honest"]:
            goods_value = sum(g.value for g in result["goods_passed"])
            merchant.gold += goods_value
            show_honest_verdict(
                len(result["goods_passed"]), goods_value, merchant.name, merchant.gold
            )
        else:
            show_lying_verdict(
                result["goods_passed"],
                result["goods_confiscated"],
                result["penalty_paid"],
                merchant.name,
                merchant.gold,
            )

        show_inspection_footer()
        update_sheriff_reputation(
            sheriff, True, result["was_honest"], stats, actual_goods
        )

    elif choice == "threaten":
        print(
            f"\n{content['messages']['threaten_bribe_increase'].format(name=merchant.name, amount=scenario.get('bribe_amount', 0) + 5)}"
            if scenario["has_bribe"]
            else content["messages"]["threaten_no_bribe"].format(name=merchant.name)
        )

    elif choice == "accept_bribe":
        bribe_amount = scenario["bribe_amount"]
        print(
            f"\n{content['messages']['accept_bribe_action'].format(amount=bribe_amount, name=merchant.name)}"
        )
        sheriff.gold += bribe_amount
        sheriff.reputation = max(0, sheriff.reputation - 1)
        stats.record_bribe(bribe_amount)

        result = handle_pass_without_inspection(
            merchant,
            actual_goods,
            {"good_id": declaration["good_id"], "count": declaration["count"]},
        )
        stats.record_pass(result["was_honest"])

        goods_value = sum(g.value for g in result["goods_passed"])
        merchant.gold += goods_value

        print(
            f"   {content['messages']['sheriff_gold'].format(gold=sheriff.gold, amount=bribe_amount)}"
        )
        print(
            f"   {content['messages']['sheriff_reputation'].format(reputation=sheriff.reputation)}"
        )
        show_merchant_sold_goods(merchant.name, goods_value, merchant.gold)

    # Show current stats
    labels = exec_text["stats_labels"]
    print("\n" + "-" * 70)
    print(f"{exec_text['stats_header']}")
    print(f"   {labels['reputation']}: {sheriff.reputation}/5")
    print(f"   {labels['gold']}: {sheriff.gold}g")
    print(f"   {labels['bribes']}: {stats.bribes_accepted}")
    print(f"   {labels['inspections']}: {stats.inspections_made}")
    print("-" * 70)

    # Show learning point
    print("\n" + "=" * 70)
    print(f"{exec_text['learning_header']}")
    print("=" * 70)
    print(scenario["learning_points"][choice])
    print("=" * 70)

    # Check for game over
    if sheriff.reputation <= 0:
        game_over = content["game_over"]
        print("\n" + "!" * 70)
        print(game_over["header"])
        print("!" * 70)
        print(f"\n{game_over['message']}")
        print(game_over["restoration"])
        print(f"\n{game_over['tip']}")
        print("!" * 70)
        sheriff.reputation = 5
        input(f"\n{game_over['prompt']}")


def ask_retry(content):
    """Ask if player wants to try again."""
    retry = content["retry"]
    print("\n" + "-" * 70)
    print(retry["question"])
    print(f"   {retry['note']}")
    print("-" * 70)
    print(f"1. {retry['choices']['retry']}")
    print(f"2. {retry['choices']['next']}")
    print(f"3. {retry['choices']['exit']}")
    print("-" * 70)

    while True:
        choice = input(f"\n{retry['prompt']} (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return {"1": "retry", "2": "next", "3": "exit"}[choice]
        print(content["messages"]["invalid_choice"])


def print_tutorial_complete(content):
    """Print tutorial completion message."""
    complete = content["complete"]
    print("\n" + "=" * 70)
    print(complete["header"])
    print("=" * 70)
    print(f"\n{complete['summary']}")
    for lesson in complete["lessons"]:
        print(f"  - {lesson}")
    print(f"\n{complete['ready']}")
    print("=" * 70)


def run_interactive_tutorial():
    """Run the complete interactive tutorial."""
    content = load_tutorial_content()

    print_tutorial_welcome()

    sheriff = Sheriff()
    stats = GameStats()

    scenarios = [parse_scenario(s) for s in content["scenarios"]]

    for scenario in scenarios:
        print_scenario_header(scenario, content)

        while True:
            show_merchant_arrival(scenario, content)

            choice = show_tutorial_menu(scenario, content)

            if choice == "skip":
                print(f"\n{content['messages']['skipping']}")
                break
            elif choice == "exit":
                print(f"\n{content['messages']['exiting']}")
                return False

            execute_tutorial_choice(choice, scenario, sheriff, stats, content)

            retry_choice = ask_retry(content)

            if retry_choice == "retry":
                print(f"\n{content['messages']['resetting']}\n")
                sheriff = Sheriff()
                stats = GameStats()
                continue
            elif retry_choice == "next":
                break
            else:
                print(f"\n{content['messages']['exiting']}")
                return False

    print_tutorial_complete(content)

    complete = content["complete"]
    print("\n" + "=" * 70)
    print(complete["start_prompt"])
    print("=" * 70)
    print(f"1. {complete['start_choices']['yes']}")
    print(f"2. {complete['start_choices']['no']}")
    print("=" * 70)

    while True:
        choice = input("\nYour choice (1-2): ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        print(content["messages"]["invalid_choice"])
