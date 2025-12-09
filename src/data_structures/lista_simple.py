# Esta es una lista simplemente enlazada.
# La hice lo más básica posible porque para el proyecto no necesito más.
# Tiene agregar al final y un método para mostrarla.

from .nodo import Nodo

class ListaSimple:
    def __init__(self):
        self.inicio = None

    def agregar(self, dato):
        nuevo = Nodo(dato)

        # si la lista está vacia, este será el primero
        if self.inicio is None:
            self.inicio = nuevo
            return

        # si no, recorro hasta encontrar el último
        actual = self.inicio
        while actual.siguiente is not None:
            actual = actual.siguiente

        actual.siguiente = nuevo

    def mostrar(self):
        # recorre e imprime, nada complicado
        actual = self.inicio
        while actual is not None:
            print(actual.dato)
            actual = actual.siguiente
