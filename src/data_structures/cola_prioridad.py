# Esta es la cola de prioridad para las solicitudes que vienen en el XML.


class Solicitud:
    # Esta clase solo la uso para guardar los datos de cada solicitud
    def __init__(self, tipo, data):
        self.tipo = tipo  
        self.data = data  

        # Asigno prioridades a lo simple:
        # Deploy = prioridad alta (1)
        # Backup = prioridad baja (2)
        if tipo == "Deploy":
            self.prioridad = 1
        else:
            self.prioridad = 2

class ColaPrioridad:

    def __init__(self):
        # Aquí voy guardando las solicitudes.
        
        self.lista = []

    def agregar_solicitud(self, tipo, data):
        # Creo un objeto solicitud con lo que vino del XML
        solicitud = Solicitud(tipo, data)
        self.lista.append(solicitud)

        # Ordeno la lista para que las solicitudes con menor número de prioridad
        
        self.lista.sort(key=lambda x: x.prioridad)

        print("Solicitud agregada:", tipo)

    def sacar_siguiente(self):
        # Saco la siguiente solicitud que tenga mayor prioridad
        if len(self.lista) > 0:
            return self.lista.pop(0)  
        else:
            return None

    def esta_vacia(self):
        return len(self.lista) == 0

    def mostrar_cola(self):
        # Esta función no es necesaria, pero la dejo por si quiero ver el contenido.
        print("Contenido actual de la cola (en orden):")
        for s in self.lista:
            print("- Tipo:", s.tipo, "| Prioridad:", s.prioridad, "| Datos:", s.data)
