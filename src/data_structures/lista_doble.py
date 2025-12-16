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
        if self.inicio is None:
            self.inicio = nuevo
            return
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