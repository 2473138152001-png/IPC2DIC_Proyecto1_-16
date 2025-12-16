from src.data_structures.lista_simple import ListaSimple

class DataCenter:
    def __init__(self, id, nombre, ubicacion):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.maquinas_virtuales = ListaSimple()
        self.cpu_total = 0
        self.ram_total = 0
        self.alm_total = 0
        self.cpu_usado = 0
        self.ram_usado = 0
        self.alm_usado = 0
    def agregar_vm(self, vm):
        self.maquinas_virtuales.insertar_final(vm)
    def eliminar_vm(self, id_vm):
        actual = self.maquinas_virtuales.inicio
        anterior = None
        while actual is not None:
            if actual.dato.id == id_vm:
                if anterior is None:
                    self.maquinas_virtuales.inicio = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                return True
            anterior = actual
            actual = actual.siguiente
        return False
    def __str__(self):
        return "DataCenter " + str(self.id) + ": " + self.nombre + " - " + self.ubicacion