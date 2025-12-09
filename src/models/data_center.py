from src.data_structures.lista_simple import ListaSimple

class DataCenter:
    
    def __init__(self, id, nombre, ubicacion):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.maquinas_virtuales = ListaSimple()  

    def agregar_vm(self, vm):
        self.maquinas_virtuales.insertar_final(vm)

    def __str__(self):
        return "DataCenter " + str(self.id) + ": " + self.nombre + " - " + self.ubicacion
