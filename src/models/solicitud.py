class Solicitud:
    
    def __init__(self, id, tipo, prioridad, descripcion):
        self.id = id
        self.tipo = tipo
        self.prioridad = prioridad  
        self.descripcion = descripcion

    def __str__(self):
        return "Solicitud " + str(self.id) + " | tipo: " + self.tipo + " | prioridad: " + str(self.prioridad)
