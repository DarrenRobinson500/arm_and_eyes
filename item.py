# items = []

class Item:
    def __init__(self, app, values):
        # values = label, i1, x1, y1, i2, x2, y2
        self.number = len(app.items)
        self.time_count = 0
        self.app = app

        self.x = 0
        self.y = 0
        self.z = 0

        self.update(values)
        app.items.append(self)

    def __str__(self):
        return f"Item: {self.label} {self.i1} {self.i2}"

    def update(self, values):
        self.label, self.i1, self.x1, self.y1, self.i2, self.x2, self.y2 = values
        self.label_text = self.app.model.get_label(self.label).name
        if self.app.model_active:
            self.x, self.y, self.z = self.app.scene.pos(self.x1, self.y1, self.x2, self.y2)
        self.values = [self.label_text, self.i1, self.x1, self.y1, self.i2, self.x2, self.y2, self.x, self.y, self.z]
        self.time_count = 0

def increment_items(app):
    # print("Increment items:")
    # print_items(app)
    for item in app.items:
        item.time_count += 1
        if item.time_count >= 4: app.items.remove(item)
        # print("Increment items:", item.number, item.time_count)

def print_items(app):
    text = ""
    for item in app.items:
        text += str(item) + "  "
    print(text)
    print()

