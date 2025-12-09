# Este es el nodo que voy a usar en las listas.
# La verdad solo lleva el dato y la referencia al siguiente.
# No tiene nada raro.

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None  # al inicio no apunta a nada

    def __str__(self):
        # solo para ver rápido el dato cuando imprima
        return str(self.dato)
