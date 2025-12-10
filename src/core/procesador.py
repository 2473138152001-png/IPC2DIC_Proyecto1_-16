# Este archivo es el procesador de solicitudes e instrucciones.


import xml.etree.ElementTree as ET

class ProcesadorSolicitudes:

    def __init__(self, lista_data_centers):
        # Esta lista viene del parser
        self.data_centers = lista_data_centers

        # Aquí voy a conectar la cola de prioridad que hicimos
        self.cola_solicitudes = None

    def asignar_cola(self, cola):
        # Simplemente guardo la cola que me pasen
        self.cola_solicitudes = cola

    def procesar_solicitudes(self, cantidad):
        if self.cola_solicitudes is None:
            print("No se ha asignado ninguna cola de solicitudes.")
            return

        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0.")
            return

        print("Procesando", cantidad, "solicitudes...")

        # Saco una por una
        for i in range(cantidad):
            solicitud = self.cola_solicitudes.sacar_siguiente()

            if solicitud is None:
                print("La cola ya no tiene más solicitudes.")
                break

            tipo = solicitud.tipo     
            datos = solicitud.data    

            print("Solicitud procesada:", tipo)

            if tipo == "Deploy":
                self.procesar_deploy(datos)

            elif tipo == "Backup":
                self.procesar_backup(datos)

            else:
                print("Solicitud desconocida:", tipo)

        print("Fin del procesamiento de solicitudes.")

    
        def procesar_deploy(self, datos):
        

            id_vm = datos.get("idVM", "")
            id_dc = datos.get("dataCenter", "")
            cpu = datos.get("cpu", "")
            ram = datos.get("ram", "")
            almacenamiento = datos.get("almacenamiento", "")

            # Primero busco el DataCenter donde se va a crear la VM
            data_center = None
            actual = self.data_centers.inicio  # porque es lista simple

            while actual is not None:
                if actual.valor.id == id_dc:
                    data_center = actual.valor
                    break
                actual = actual.siguiente

            if data_center is None:
                print("No se encontró el DataCenter:", id_dc)
                return

            # Ya tengo el DataCenter, ahora creo la VM.
            # Como aún no definimos bien la clase MaquinaVirtual para Deploy,
            # solo uso lo básico.
            try:
                from src.models.maquina_virtual import MaquinaVirtual
            except:
                print("Error importando MaquinaVirtual")
                return

            # Creo la VM con los datos de la solicitud
            nueva_vm = MaquinaVirtual(
                id_vm,
                "VM_" + id_vm,        # Nombre simple estilo estudiante
                "SO_Desconocido"      # Por ahora no viene en la solicitud
            )

            # También le asigno los recursos (como atributos)
            nueva_vm.cpu = cpu
            nueva_vm.ram = ram
            nueva_vm.almacenamiento = almacenamiento

            # Ahora agrego la VM a la lista del DataCenter
            data_center.agregar_vm(nueva_vm)

            print("VM creada por solicitud Deploy ->", id_vm,
                "en DataCenter:", id_dc)


    def procesar_backup(self, datos):
        # Aquí luego pondremos la lógica del backup
        print("Se debería hacer un backup con estos datos:", datos)

    def cargar_solicitudes(self, ruta_xml):
        try:
            arbol = ET.parse(ruta_xml)
            raiz = arbol.getroot()
        except:
            print("No se pudo leer el archivo de solicitudes.")
            return

        # Recorro cada instrucción
        for instruccion in raiz.findall("instruccion"):
            tipo = instruccion.get("tipo")

            print("Leyendo instrucción:", tipo)

            # Dependiendo del tipo llamo a una función
            if tipo == "crearVM":
                self.crear_vm(instruccion)

            elif tipo == "migrarVM":
                self.migrar_vm(instruccion)

            elif tipo == "procesarSolicitudes":
                
                cantidad_nodo = instruccion.find("cantidad")
                if cantidad_nodo is not None:
                    try:
                        cantidad = int(cantidad_nodo.text)
                    except:
                        cantidad = 0
                else:
                    cantidad = 0

                self.procesar_solicitudes(cantidad)

            else:
                print("Instrucción desconocida:", tipo)

    def crear_vm(self, nodo):
        # Esto lo llenaremos despues
        print("Se recibió una instrucción para crear una VM (falta implementar).")

    def migrar_vm(self, nodo):
        # se hara después, aun falta
        print("Se recibió una instrucción para migrar una VM (falta implementar).")
