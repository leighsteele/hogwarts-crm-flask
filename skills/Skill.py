class Skill:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __str__(self):
        return str.format("Skill: {}, Level: {}", self.name, self.level)

    def get_name(self):
        return self.name