class Contenedor:

    def __init__(self, id, nombre, imagen, cpu=0, ram=0):
        self.id = id
        self.nombre = nombre
        self.imagen = imagen
        self.cpu = cpu
        self.ram = ram
        self.estado = "Activo"   

    def __str__(self):
        return (
            f"Contenedor {self.id} | {self.nombre} | {self.imagen} | "
            f"CPU: {self.cpu} | RAM: {self.ram} | Estado: {self.estado}"
        )
