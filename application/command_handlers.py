def add_item_handler():
    def handle(command):
      print('handling command', command)
    return handle