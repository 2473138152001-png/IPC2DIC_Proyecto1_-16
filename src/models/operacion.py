class Operacion:
    def __init__(self, fecha, action, detalles):
        self.fecha = fecha
        self.action = action
        self.detalles = detalles

    def __str__(self):
        return f"[{self.fecha}] {self.action} -> {self.detalles}"