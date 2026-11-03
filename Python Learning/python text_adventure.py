import sys


class Player:
    def __init__(self):
        self.inventory = []
        self.current_room = None
        self.alive = True

    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            print(f"\nYou move {direction}...\n")
            print(self.current_room.get_details())
        else:
            print("\nYou can't go that way!")

    def take_item(self, item_name):
        # Check if item is in room
        item_found = None
        for item in self.current_room.items:
            if item.name.lower() == item_name.lower():
                item_found = item
                break

        if item_found:
            self.inventory.append(item_found)
            self.current_room.items.remove(item_found)
            print(f"\nYou picked up: {item_found.name}")
        else:
            print("\nThat item isn't here.")


class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []

    def add_exit(self, direction, room):
        self.exits[direction] = room

    def add_item(self, item):
        self.items.append(item)

    def get_details(self):
        details = f"--- {self.name} ---\n{self.description}\n"
        if self.items:
            details += "You see here: " + ", ".join([item.name for item in self.items]) + "\n"
        details += "Exits: " + ", ".join(self.exits.keys())
        return details


def main():
    # Setup Game World
    start_room = Room("Dungeon Entrance", "You are standing at the entrance of a dark dungeon. The air is cold.")
    hallway = Room("Long Hallway", "A narrow, torch-lit hallway stretching into the darkness.")
    treasure_room = Room("Treasure Room", "A glittering room filled with gold! But the door is locked.")
    trap_room = Room("Pit of Spikes", "Oh no! It's a trap!")

    # Connect Rooms
    start_room.add_exit("north", hallway)
    hallway.add_exit("south", start_room)
    hallway.add_exit("east", treasure_room)
    # Trap logic could be extended, currently just a room you can enter
    hallway.add_exit("west", trap_room)
    trap_room.add_exit("east", hallway)

    # Add Items
    key = Item("Golden Key", "A shiny golden key that looks important.")
    start_room.add_item(key)

    msg = Item("Note", "It says: 'Beware of the west wing!'")
    hallway.add_item(msg)

    # Setup Player
    player = Player()
    player.current_room = start_room

    print("Welcome to The Lost Treasure of Pythonia!")
    print(player.current_room.get_details())

    while player.alive:
        command = input("> ").lower().split()

        if not command:
            continue

        action = command[0]

        if action == "quit":
            print("Thanks for playing!")
            break

        elif action == "move" or action == "go":
            if len(command) > 1:
                player.move(command[1])
            else:
                print("Move where?")

        elif action in ["north", "south", "east", "west"]:
            player.move(action)

        elif action == "look":
            print(player.current_room.get_details())

        elif action == "inventory" or action == "i":
            if player.inventory:
                print("\nYou are carrying:")
                for item in player.inventory:
                    print(f"- {item.name}: {item.description}")
            else:
                print("\nYou are not carrying anything.")

        elif action == "take" or action == "get":
            if len(command) > 1:
                item_name = " ".join(command[1:])
                player.take_item(item_name)
            else:
                print("Take what?")

        else:
            print("I don't understand that command.")

        # Logic for Treasure Room Interaction (Win Condition)
        if player.current_room == treasure_room:
            has_key = any(item.name == "Golden Key" for item in player.inventory)
            if has_key:
                print("\nCongratulations! You used the Golden Key to unlock the chest and found the treasure!")
                print("You Win!")
                break
            else:
                print("\nThe door is locked tight. You need a key.")
                # Bounce back to hallway if no key
                print("You return to the hallway.")
                player.current_room = hallway


if __name__ == "__main__":
    main()
