from .nodo import Nodo

class ListaSimple:
    def __init__(self):
        self.inicio = None

    def agregar(self, dato):
        nuevo = Nodo(dato)
        if self.inicio is None:
            self.inicio = nuevo
            return
        actual = self.inicio
        while actual.siguiente is not None:
            actual = actual.siguiente
        actual.siguiente = nuevo
    def insertar_final(self, dato):
        self.agregar(dato)

    def mostrar(self):
        
        actual = self.inicio
        while actual is not None:
            print(actual.dato)
            actual = actual.siguiente
            
    def contar(self):
        contador = 0
        actual = self.inicio

        while actual is not None:
            contador += 1
            actual = actual.siguiente

        return contador