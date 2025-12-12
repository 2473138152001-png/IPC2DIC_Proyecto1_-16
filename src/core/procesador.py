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

            print("no se ha seleccionado ninguna cola de solicitudes")
            return

        if cantidad <= 0:
            print("error, la cantidad debe ser mayor a 0")
            return

        print("Procesando", cantidad, "solicitudes")


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
            if actual.dato.id == id_dc:
                data_center = actual.dato
                break
            actual = actual.siguiente

        if data_center is None:
            print("No se encontró el DataCenter:", id_dc)
            return

        # Ya tengo el DataCenter, ahora creo la VM.
        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error importando MaquinaVirtual")
            return

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
            
    def cargar_solicitudes_xml(self, ruta):
        # Este método sirve para leer las solicitudes (Deploy / Backup)
        # y meterlas a la cola de prioridad.

        if self.cola_solicitudes is None:
            print("No se ha asignado una cola de prioridad.")
            return

        try:
            arbol = ET.parse(ruta)
            raiz = arbol.getroot()
        except:
            print("No se pudo leer el archivo de solicitudes.")
            return

        # Recorro cada solicitud del XML
        for solicitud in raiz.findall("Solicitud"):

            tipo = solicitud.get("tipo")  # Deploy o Backup

            # Aqui voy a guardar toda la información de la solicitud
            datos = {}

            # Recorro los hijos (idVM, cpu, ram, dataCenter, etc.)
            for nodo in solicitud:
                etiqueta = nodo.tag
                valor = nodo.text
                datos[etiqueta] = valor

            # Ya tengo tipo y datos, ahora lo mando a la cola
            self.cola_solicitudes.agregar_solicitud(tipo, datos)

            print("Solicitud leída del XML ->", tipo)

        print("Carga de solicitudes completada.")
    def procesar_backup(self, datos):
        # Según el PDF, un Backup crea una nueva VM en estado suspendido
        # y se asigna al data center con más recursos disponibles

        id_vm = datos.get("idVM", "")
        cpu = datos.get("cpu", "0")
        ram = datos.get("ram", "0")
        almacenamiento = datos.get("almacenamiento", "0")

        # Buscar el DataCenter con más recursos disponibles
        actual = self.data_centers.inicio
        data_center_elegido = None
        mayor_cpu = -1

        while actual is not None:

            dc = actual.dato
            # Usamos solo CPU para comparar, de forma simple
            if dc.cpu_disponible > mayor_cpu:
                mayor_cpu = dc.cpu_disponible
                data_center_elegido = dc

            actual = actual.siguiente

        if data_center_elegido is None:
            print("No se encontró ningún DataCenter disponible para Backup.")
            return

        # Importamos la clase MaquinaVirtual
        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error importando MaquinaVirtual para Backup.")
            return

        # Creamos la VM en estado suspendido
        nueva_vm = MaquinaVirtual(
            id_vm,
            "VM_Backup_" + id_vm,
            "Sistema_Backup"
        )

        # Asignamos recursos (de forma sencilla)
        nueva_vm.cpu = cpu
        nueva_vm.ram = ram
        nueva_vm.almacenamiento = almacenamiento
        nueva_vm.estado = "SUSPENDIDA"

        # Agregamos la VM al DataCenter elegido
        data_center_elegido.agregar_vm(nueva_vm)

        print("Backup creado correctamente:")
        print("VM:", id_vm)
        print("Estado: SUSPENDIDA")
        print("Asignada al DataCenter:", data_center_elegido.id)

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
        # Este método crea una VM directamente desde una instrucción
        # No pasa por la cola, se ejecuta de inmediato

        # Leo los datos del XML
        centro_nodo = nodo.find("centro")
        vmid_nodo = nodo.find("vmId")
        cpu_nodo = nodo.find("cpu")
        ram_nodo = nodo.find("ram")
        alm_nodo = nodo.find("almacenamiento")

        if centro_nodo is None or vmid_nodo is None:
            print("La instrucción crearVM está incompleta.")
            return

        id_dc = centro_nodo.text
        id_vm = vmid_nodo.text

        cpu = cpu_nodo.text if cpu_nodo is not None else "0"
        ram = ram_nodo.text if ram_nodo is not None else "0"
        almacenamiento = alm_nodo.text if alm_nodo is not None else "0"

        # Busco el DataCenter donde se va a crear la VM
        actual = self.data_centers.inicio
        data_center = None

        while actual is not None:
            if actual.dato.id == id_dc:
                data_center = actual.dato
                break
            actual = actual.siguiente

        if data_center is None:
            print("No se encontró el DataCenter:", id_dc)
            return

        # Importo la clase MaquinaVirtual
        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error al importar MaquinaVirtual.")
            return

        # Creo la VM
        nueva_vm = MaquinaVirtual(
            id_vm,
            "VM_" + id_vm,
            "SO_Desconocido"
        )

        # Asigno los recursos
        nueva_vm.cpu = cpu
        nueva_vm.ram = ram
        nueva_vm.almacenamiento = almacenamiento

        # Agrego la VM al DataCenter
        data_center.agregar_vm(nueva_vm)

        print("VM creada correctamente:")
        print("ID:", id_vm)
        print("DataCenter:", id_dc)

    def migrar_vm(self, nodo):
        # Este método mueve una VM de un DataCenter a otro

        # Leo los datos del XML
        vmid_nodo = nodo.find("vmId")
        origen_nodo = nodo.find("origen")
        destino_nodo = nodo.find("destino")

        if vmid_nodo is None or origen_nodo is None or destino_nodo is None:
            print("La instrucción migrarVM está incompleta.")
            return

        id_vm = vmid_nodo.text
        id_origen = origen_nodo.text
        id_destino = destino_nodo.text

        data_center_origen = None
        data_center_destino = None
        vm_encontrada = None

        # Busco el DataCenter origen y destino
        actual = self.data_centers.inicio

        while actual is not None:
            dc = actual.dato

            if dc.id == id_origen:
                data_center_origen = dc

            if dc.id == id_destino:
                data_center_destino = dc

            actual = actual.siguiente

        if data_center_origen is None:
            print("No se encontró el DataCenter origen:", id_origen)
            return

        if data_center_destino is None:
            print("No se encontró el DataCenter destino:", id_destino)
            return

        # Busco la VM dentro del DataCenter origen
        actual_vm = data_center_origen.maquinas_virtuales.inicio

        while actual_vm is not None:
            if actual_vm.dato.id == id_vm:
                vm_encontrada = actual_vm.dato
                break
            actual_vm = actual_vm.siguiente

        if vm_encontrada is None:
            print("No se encontró la VM", id_vm, "en el DataCenter", id_origen)
            return

        # Quito la VM del DataCenter origen
        data_center_origen.eliminar_vm(id_vm)

        # Agrego la VM al DataCenter destino
        data_center_destino.agregar_vm(vm_encontrada)

        print("Migración realizada correctamente:")
        print("VM:", id_vm)
        print("De:", id_origen)
        print("A:", id_destino)
