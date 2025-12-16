class NodoCola:
    def __init__(self, solicitud):
        self.solicitud= solicitud
        self.siguiente= None
class ColaPrioridad:
    def __init__(self):
        self.inicio=None
        
    def agregar_solicitud(self, solicitud):
        nuevo = NodoCola(solicitud)
        if self.inicio is None or solicitud.prioridad< self.inicio.solicitud.prioridad:
            nuevo.siguiente= self.inicio
            self.inicio = nuevo
            return
        actual = self.inicio
        while actual.siguiente is not None and actual.siguiente.solicitud.prioridad <= solicitud.prioridad:
            actual= actual.siguiente
        nuevo.siguiente = actual.siguiente
        actual.siguiente = nuevo
        
    def sacar_siguiente(self):
        if self.inicio is None:
            return None 
        solicitud = self.inicio.solicitud
        self.inicio = self.inicio.siguiente
        return solicitud
    
    def esta_vacia(self):
        return self.inicio is None
    
    def mostrar_cola(self):
        print("Contenido actual de la cola en orden:")
        actual = self.inicio
        if actual is None:
            print("La cola está vacia")
            return

        while actual is not None:
            s = actual.solicitud
            print(
                "- ID:", s.id,
                "| Tipo:", s.tipo,
                "| Prioridad:", s.prioridad
            )
            actual = actual.siguiente