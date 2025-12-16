# Este archivo es el procesador de solicitudes e instrucciones.
import xml.etree.ElementTree as ET
from src.models.solicitud import Solicitud


class ProcesadorSolicitudes:

    def __init__(self, lista_data_centers):
        self.data_centers = lista_data_centers
        self.cola_solicitudes = None

    def asignar_cola(self, cola):
        self.cola_solicitudes = cola

    def procesar_solicitudes(self, cantidad):
        if self.cola_solicitudes is None:
            print("no se ha seleccionado ninguna cola de solicitudes")
            return 0, 0, 0
        if cantidad <= 0:
            print("error, la cantidad debe ser mayor a 0")
            return 0, 0, 0
        procesadas = 0
        completas = 0
        fallidas = 0
        print("Procesando", cantidad, "solicitudes")
        for i in range(cantidad):
            solicitud = self.cola_solicitudes.sacar_siguiente()

            if solicitud is None:
                print("La cola ya no tiene más solicitudes.")
                break
            procesadas+=1
            tipo = solicitud.tipo     
            try:
                if tipo == "Deploy":
                    self.procesar_deploy(solicitud)
                    completas+=1
                elif tipo == "Backup":
                    self.procesar_backup(solicitud)
                    completas+=1
                else:
                    print("Solicitud desconocida:", tipo)
                    fallidas+=1
            except Exception as e:
                fallidas +=1    
        print("Fin del procesamiento de solicitudes.")
        return procesadas, completas, fallidas
    def procesar_deploy(self, solicitud):
        id_vm = "VM_" + str(solicitud.id)
        id_dc = "DC001"
        actual = self.data_centers.inicio
        if actual is None:
            print("No hay DataCenters registrados")
            return

        data_center = actual.dato

        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error importando MaquinaVirtual")
            return

        nueva_vm = MaquinaVirtual(
            id_vm,
            "VM_" + id_vm,
            "SO_Desconocido"
        )
        nueva_vm.cpu = 1
        nueva_vm.ram = 1
        nueva_vm.almacenamiento = 10
        data_center.agregar_vm(nueva_vm)

        

            
    def cargar_solicitudes_xml(self, ruta):
        if self.cola_solicitudes is None:
            print("No se ha asignado una cola de prioridad")
            return
        try:
            arbol = ET.parse(ruta)
            raiz = arbol.getroot()
        except:
            print("No se pudo leer el archivo de solicitudes.")
            return
        for nodo in raiz.findall("Solicitud"):
            id_sol = nodo.get("id")  
            tipo = nodo.get("tipo")
            prioridad = nodo.get("prioridad")
            descripcion=""
            for hijo in nodo:
                descripcion+=hijo.tag + ": "+ hijo.text + " | "
            solicitud = Solicitud(id_sol, tipo, prioridad, descripcion)
            self.cola_solicitudes.agregar_solicitud(solicitud)
            print("Solicitud leida del XML ", solicitud)
        print("Carga de solicitudes completada.") 
    def procesar_backup(self, solicitud):
        actual = self.data_centers.inicio
        if actual is None:
            print("No hay DataCenters registrados")
            return
        data_center = actual.dato
        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error importando MaquinaVirtual")
            return
        id_vm = "VM_Backup_" + str(solicitud.id)

        nueva_vm = MaquinaVirtual(
            id_vm,
            "VM_Backup_" + id_vm,
            "Sistema_Backup"
        )

        nueva_vm.estado = "SUSPENDIDA"
        nueva_vm.cpu = 1
        nueva_vm.ram = 1
        nueva_vm.almacenamiento = 10
        data_center.agregar_vm(nueva_vm)
    def cargar_solicitudes(self, ruta_xml):
        try:
            arbol = ET.parse(ruta_xml)
            raiz = arbol.getroot()
        except:
            print("No se pudo leer el archivo de solicitudes.")
            return
        for instruccion in raiz.findall("instruccion"):
            tipo = instruccion.get("tipo")
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

                procesadas, completadas, fallidas =  self.procesar_solicitudes(cantidad)
                print(f"Procesadas: {procesadas}, Completadas: {completadas}, Fallidas: {fallidas}")
            else:
                print("Instrucción desconocida:", tipo)
    def crear_vm(self, nodo):
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
        try:
            from src.models.maquina_virtual import MaquinaVirtual
        except:
            print("Error al importar MaquinaVirtual.")
            return
        nueva_vm = MaquinaVirtual(
            id_vm,
            "VM_" + id_vm,
            "SO_Desconocido"
        )
        nueva_vm.cpu = cpu
        nueva_vm.ram = ram
        nueva_vm.almacenamiento = almacenamiento
        data_center.agregar_vm(nueva_vm)

        print("VM creada correctamente:")
        print("ID:", id_vm)
        print("DataCenter:", id_dc)

    def migrar_vm(self, nodo):
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
        actual_vm = data_center_origen.maquinas_virtuales.inicio
        while actual_vm is not None:
            if actual_vm.dato.id == id_vm:
                vm_encontrada = actual_vm.dato
                break
            actual_vm = actual_vm.siguiente
        if vm_encontrada is None:
            print("No se encontró la VM", id_vm, "en el DataCenter", id_origen)
            return
        data_center_origen.eliminar_vm(id_vm)
        data_center_destino.agregar_vm(vm_encontrada)

        print("Migración realizada correctamente:")
        print("VM:", id_vm)
        print("De:", id_origen)
        print("A:", id_destino)