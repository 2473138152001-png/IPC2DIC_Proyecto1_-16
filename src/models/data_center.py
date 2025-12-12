# esta es la clase data center que en pocas palabras es donde estan los datos del individuo tanto el id, nombre y ubicacion
#y donde los agregamos a la lista simple llamada maquinas virtuales

from src.data_structures.lista_simple import ListaSimple

class DataCenter:
    
    def __init__(self, id, nombre, ubicacion):
        self.id = id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.maquinas_virtuales = ListaSimple()
        self.cpu_disponible = 0

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
