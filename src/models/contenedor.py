class Contenedor:
    
    def __init__(self, id, nombre, tipo):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo  

    def __str__(self):
        return "Contenedor: " + str(self.id) + " - " + self.nombre + " (" + self.tipo + ")"
