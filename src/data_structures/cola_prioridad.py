# Cola de prioridad básica.
# Lo que hago es insertar según prioridad (mientras más pequeño el número,
# más "prioridad" tiene).
# No es la súper estructura, pero funciona para lo que necesito.

class NodoPrioridad:
    def __init__(self, dato, prioridad):
        self.dato = dato
        self.prioridad = prioridad
        self.sig = None


class ColaPrioridad:
    def __init__(self):
        self.inicio = None

    def encolar(self, dato, prioridad):
        nuevo = NodoPrioridad(dato, prioridad)

        # si está vacía
        if self.inicio is None:
            self.inicio = nuevo
            return

        # si el nuevo tiene más prioridad que el primero
        if prioridad < self.inicio.prioridad:
            nuevo.sig = self.inicio
            self.inicio = nuevo
            return

        # si no, busco dónde meterlo
        actual = self.inicio
        while actual.sig is not None and actual.sig.prioridad <= prioridad:
            actual = actual.sig

        nuevo.sig = actual.sig
        actual.sig = nuevo

    def desencolar(self):
        # devuelve el dato del primero
        if self.inicio is None:
            return None

        dato = self.inicio.dato
        self.inicio = self.inicio.sig
        return dato

    def mostrar(self):
        actual = self.inicio
        while actual is not None:
            print(f"{actual.dato} (prio {actual.prioridad})")
            actual = actual.sig
