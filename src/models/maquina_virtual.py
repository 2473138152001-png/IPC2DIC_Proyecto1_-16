from src.data_structures.lista_simple import ListaSimple

class MaquinaVirtual:
    
    def __init__(self, id, nombre, sistema_operativo):
        self.id = id
        self.nombre = nombre
        self.sistema_operativo = sistema_operativo
        self.contenedores = ListaSimple()  

    def agregar_contenedor(self, contenedor):
       
        self.contenedores.insertar_final(contenedor)

    def __str__(self):
        return "VM " + str(self.id) + " - " + self.nombre + " (" + self.sistema_operativo + ")"
