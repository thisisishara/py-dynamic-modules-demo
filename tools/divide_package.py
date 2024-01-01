class Divide:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def perform_division(self):
        if self.b == 0:
            return 'Cannot divide by zero'
        return self.b / self.a