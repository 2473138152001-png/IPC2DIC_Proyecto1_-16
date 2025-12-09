# Lista doble enlazada
# Igual que la simple pero cada nodo tiene anterior y siguiente.
# Esto sirve por si necesito recorrer hacia atrás también.

class NodoDoble:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None
        self.ant = None


class ListaDoble:
    def __init__(self):
        self.inicio = None

    def agregar(self, dato):
        nuevo = NodoDoble(dato)

        # si está vacía
        if self.inicio is None:
            self.inicio = nuevo
            return

        # buscar el último
        actual = self.inicio
        while actual.sig is not None:
            actual = actual.sig

        actual.sig = nuevo
        nuevo.ant = actual

    def mostrar(self):
        actual = self.inicio
        while actual is not None:
            print(actual.dato)
            actual = actual.sig
