# functions relating to the system menu
# Created by team E04
# Created date: 10/04/24
# Cersion 1.0
from control.normal_operation import normal_operation
from lib import quit_program

from .data_observation import data_observation
from .maintenance_adjustment import maintenance_adjustment

# possible mode options
modeOptions = {
    1: "Normal Operation",
    2: "Data Observation",
    3: "Maintenance Adjustment",
}

currentChoice = None


def display_main_menu():
    """Displays main menu with available modes
    no parameters
    no returns:
    """
    print("Main Menu")
    print("-------------------------")
    for key, value in modeOptions.items():
        print(f"{key}: {value} Mode")
    print("Press Ctrl+C to quit")


def get_menu_choice() -> int:
    """gets user input for menu choices
    parameters: input(option:)
    no returns
    """
    while True:
        try:
            choice = int(input("Option: "))
            if choice in modeOptions.keys():
                return choice
            else:
                print("Error: Invalid option")
        except ValueError:
            print("Error: Only numbers are accepted")
        except KeyboardInterrupt:
            quit_program()
        except RuntimeError:
            quit_program()


def change_mode(choice):
    """allows user to change mode
    parameters: user input
    no returns
    """
    global currentChoice
    if not currentChoice == choice:
        match choice:
            case 1:
                normal_operation()
            case 2:
                data_observation()
            case 3:
                maintenance_adjustment()


def run_menu():
    """displays main menu
    no parameters
    no returns
    """
    while True:
        display_main_menu()
        choice = get_menu_choice()
        change_mode(choice)


def run_lock_out_menu():
    """Displays main menu and allows user to select mode"""
    while True:
        display_main_menu()
        choice = get_menu_choice()
        if choice == 1:
            normal_operation()
        elif choice == 2:
            data_observation()
        else:
            print(
                "Invalid option. Please choose Normal Operation (1) or Data Observation (2)."
            )
            break
