class CommandHandler:
    def __init__(self):
        self.commands = {}

    def register_command(self, command: str, func):
        self.commands[command] = func

    def handle_command(self, command: str, *args):
        if command in self.commands:
            return self.commands[command](*args)
        else:
            print(f"Unknown command: {command}")
            return None