
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from src.core.procesador import ProcesadorSolicitudes
from src.data_structures.cola_prioridad import ColaPrioridad
from src.data_structures.lista_simple import ListaSimple
from src.parser.parser import ParserXML
from src.models.data_center import DataCenter
from src.models.maquina_virtual import MaquinaVirtual
from src.models.contenedor import Contenedor
from src.models.solicitud import Solicitud


# Rutas de exporte
RUTAREPORTES = "src/reportes"
RUTATESTS = "src/tests"


# -------------------------
# Historial
# -------------------------
class Operacion:
    def __init__(self, fecha, accion, detalle):
        self.fecha = fecha
        self.accion = accion
        self.detalle = detalle

    def __str__(self):
        return "[" + str(self.fecha) + "] " + str(self.accion) + " -> " + str(self.detalle)


def registrar_operacion(historial, accion, detalle):
    try:
        fecha = datetime.now().isoformat()
    except:
        fecha = "sin_fecha"
    historial.insertar_final(Operacion(fecha, accion, detalle))


def contiene(texto, patron):
    if texto is None or patron is None:
        return False
    return str(patron).lower() in str(texto).lower()


# -------------------------
# Menús
# -------------------------
def mostrar_menu_principal():
    print("\n===================================")
    print("  CLOUDSYNC MANAGER - SISTEMA DE NUBE")
    print("===================================")
    print("1. Cargar Archivo XML")
    print("2. Gestión de Centros de Datos")
    print("3. Gestión de Maquinas Virtuales")
    print("4. Gestión de Contenedores")
    print("5. Gestión de Solicitudes")
    print("6. Reportes Graphviz")
    print("7. Generar XML de Salida")
    print("8. Historial de Operaciones")
    print("9. Salir")
    print("===================================")


# -------------------------
# XML de salida
# -------------------------
def porcentaje(usado, total):
    if total == 0:
        return "0.00%"
    p = (usado / total) * 100
    return format(p, ".2f") + "%"


def indentar_xml(elem, nivel=0):
    salto = "\n" + ("  " * nivel)
    if len(elem) > 0:
        if elem.text is None or elem.text == "":
            elem.text = salto + "  "
        for h in elem:
            indentar_xml(h, nivel + 1)
        if elem.tail is None or elem.tail == "":
            elem.tail = salto
    else:
        if nivel > 0 and (elem.tail is None or elem.tail == ""):
            elem.tail = salto


def generar_xml_salida(listaCentros):
    if not os.path.exists(RUTATESTS):
        os.makedirs(RUTATESTS)

    ruta = os.path.join(RUTATESTS, "resultadoCloudSync.xml")

    raiz = ET.Element("resultadoCloudSync")
    ET.SubElement(raiz, "timestamp").text = datetime.now().isoformat()

    estadoCentros = ET.SubElement(raiz, "estadoCentros")

    totalVms = 0
    totalCont = 0
    vmsActivas = 0

    nodoCentro = listaCentros.inicio
    while nodoCentro is not None:
        dc = nodoCentro.dato

        nodoDc = ET.SubElement(estadoCentros, "centro", Id=str(dc.id))
        ET.SubElement(nodoDc, "nombre").text = dc.nombre

        rec = ET.SubElement(nodoDc, "recursos")

        # recursos del centro
        cput = dc.cpu_total
        ramt = dc.ram_total

        cpus = dc.cpu_usado
        rams = dc.ram_usado

        cpud = cput - cpus
        ramd = ramt - rams

        if cpud < 0:
            cpud = 0
        if ramd < 0:
            ramd = 0

        ET.SubElement(rec, "cpuTotal").text = str(cput)
        ET.SubElement(rec, "cpuDisponible").text = str(cpud)
        ET.SubElement(rec, "cpuUtilizacion").text = porcentaje(cpus, cput)

        ET.SubElement(rec, "ramTotal").text = str(ramt)
        ET.SubElement(rec, "ramDisponible").text = str(ramd)
        ET.SubElement(rec, "ramUtilizacion").text = porcentaje(rams, ramt)

        cantVms = dc.maquinas_virtuales.contar()
        cantCont = 0

        nodoVm = dc.maquinas_virtuales.inicio
        while nodoVm is not None:
            vm = nodoVm.dato
            cantCont = cantCont + vm.contenedores.contar()

            if vm.estado == "Activa":
                vmsActivas = vmsActivas + 1

            nodoVm = nodoVm.siguiente

        ET.SubElement(nodoDc, "cantidadVms").text = str(cantVms)
        ET.SubElement(nodoDc, "cantidadContenedores").text = str(cantCont)

        totalVms = totalVms + cantVms
        totalCont = totalCont + cantCont

        nodoCentro = nodoCentro.siguiente

    if vmsActivas == 0:
        vmsActivas = totalVms

    est = ET.SubElement(raiz, "estadisticas")
    ET.SubElement(est, "vmsActivas").text = str(vmsActivas)
    ET.SubElement(est, "contenedoresTotales").text = str(totalCont)

    indentar_xml(raiz)
    arbol = ET.ElementTree(raiz)

    try:
        arbol.write(ruta, encoding="utf-8", xml_declaration=True)
        print("XML de salida generado correctamente")
        print("Ruta:", ruta)
        return True
    except:
        print("No se pudo generar el XML")
        return False


# -------------------------
# Historial menu, export
# -------------------------
def exportar_historial_xml(historial):
    if not os.path.exists(RUTATESTS):
        os.makedirs(RUTATESTS)

    ruta = os.path.join(RUTATESTS, "historialOperaciones.xml")

    raiz = ET.Element("historialOperaciones")
    ET.SubElement(raiz, "timestamp").text = datetime.now().isoformat()
    ops = ET.SubElement(raiz, "operaciones")

    actual = historial.inicio
    while actual is not None:
        op = actual.dato
        nodo = ET.SubElement(ops, "operacion")
        ET.SubElement(nodo, "fecha").text = str(op.fecha)
        ET.SubElement(nodo, "accion").text = str(op.accion)
        ET.SubElement(nodo, "detalle").text = str(op.detalle)
        actual = actual.siguiente

    indentar_xml(raiz)
    try:
        ET.ElementTree(raiz).write(ruta, encoding="utf-8", xml_declaration=True)
        print("Historial exportado correctamente")
        print("Ruta:", ruta)
        return True
    except Exception as e:
        print("No se pudo exportar el historial:", e)
        return False


def menu_historial(historial):
    while True:
        print("\n=== HISTORIAL DE OPERACIONES ===")
        print("1. Ver todo")
        print("2. Buscar (por palabra)")
        print("3. Exportar a XML")
        print("4. Limpiar historial")
        print("5. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            if historial.inicio is None:
                print("No hay operaciones registradas")
            else:
                actual = historial.inicio
                n = 1
                while actual is not None:
                    print(str(n) + ". " + str(actual.dato))
                    n = n + 1
                    actual = actual.siguiente

        elif op == "2":
            palabra = input("Palabra a buscar: ")
            if palabra == "":
                print("Busqueda vacía")
                continue

            actual = historial.inicio
            enc = 0
            while actual is not None:
                opx = actual.dato
                if contiene(opx.fecha, palabra) or contiene(opx.accion, palabra) or contiene(opx.detalle, palabra):
                    print(opx)
                    enc = enc + 1
                actual = actual.siguiente

            if enc == 0:
                print("No se encontraron coincidencias")

        elif op == "3":
            exportar_historial_xml(historial)

        elif op == "4":
            historial.inicio = None
            print("Historial limpiado correctamente")

        elif op == "5":
            break
        else:
            print("Opcion invalida")


# -------------------------
# funciones de Graphviz 
# -------------------------
def escape_label(texto):
    if texto is None:
        return ""
    return str(texto)

def dot_header(titulo):
    d = "digraph CloudSync {\n"
    d += "rankdir=LR;\n"
    d += 'labelloc="t";\n'
    d += 'label="' + escape_label(titulo) + '";\n'
    d += "fontsize=18;\n"
    
    d += "\n"
    return d


def dot_footer():
    return "\n}\n"


def guardar_dot_y_png(dot_texto, nombreBase):
    if not os.path.exists(RUTAREPORTES):
        os.makedirs(RUTAREPORTES)

    rutaDot = os.path.join(RUTAREPORTES, nombreBase + ".dot")
    rutaPng = os.path.join(RUTAREPORTES, nombreBase + ".png")

    try:
        f = open(rutaDot, "w", encoding="utf-8")
        f.write(dot_texto)
        f.close()
    except Exception as e:
        print("No se pudo crear el archivo .dot:", e)
        print("Intento:", rutaDot)
        return

   
    prueba = os.system("dot -V")
    if prueba != 0:
        print("Se creo el .dot pero no se pudo generar el .png (Graphviz no está en PATH)")
        print("DOT:", rutaDot)
        return

    comando = 'dot -Tpng "' + rutaDot + '" -o "' + rutaPng + '"'
    res = os.system(comando)
    if res == 0:
        print("Reporte generado correctamente")
        print("DOT:", rutaDot)
        print("PNG:", rutaPng)
    else:
        print("Se creo el .dot pero falló la generación del .png")
        print("Comando:", comando)


def reporte_general(listaCentros, colaSol):
    dot = dot_header("Reporte General: Centros -> Vms -> Contenedores")

    nodoCentro = listaCentros.inicio
    while nodoCentro is not None:
        dc = nodoCentro.dato

        dcId = escape_label(dc.id)
        dot += 'DC_' + dcId + ' [shape=folder, label="Centro ' + dcId + "\\n" + escape_label(dc.nombre) + "\\n" + escape_label(dc.ubicacion) + '"];\n'

        nodoVm = dc.maquinas_virtuales.inicio
        while nodoVm is not None:
            vm = nodoVm.dato

            vmId = escape_label(vm.id)

            dot += (
                'VM_' + vmId +
                ' [shape=box3d, label="Vm ' + vmId +
                "\\nSo: " + escape_label(vm.sistema_operativo) +
                "\\nEstado: " + escape_label(vm.estado) + '"];\n'
            )
            dot += "DC_" + dcId + " -> VM_" + vmId + ";\n"

            nodoCont = vm.contenedores.inicio
            while nodoCont is not None:
                ct = nodoCont.dato

                ctId = escape_label(ct.id)
                ctNom = escape_label(ct.nombre)
                ctImg = escape_label(ct.imagen)

                dot += (
                    'CT_' + ctId +
                    ' [shape=component, label="Cont ' + ctId +
                    "\\n" + ctNom +
                    "\\n" + ctImg + '"];\n'
                )
                dot += "VM_" + vmId + " -> CT_" + ctId + ";\n"

                nodoCont = nodoCont.siguiente

            nodoVm = nodoVm.siguiente

        nodoCentro = nodoCentro.siguiente


   
    if colaSol is not None:
        if colaSol.inicio is not None:
            dot += "\nsubgraph cluster_cola {\n"
            dot += 'label="Cola de Solicitudes (prioridad)";\n'
            dot += "style=dashed;\n"

            actual = colaSol.inicio
            i = 1
            prev = ""
            while actual is not None:
                s = actual.solicitud
                sid = escape_label(s.id)
                st = escape_label(s.tipo)
                sp = escape_label(s.prioridad)

                nodo = "SOL_" + str(i)
                dot += nodo + ' [shape=note, label="' + sid + "\\n" + st + "\\nPrioridad: " + sp + '"];\n'
                if prev != "":
                    dot += prev + " -> " + nodo + ";\n"
                prev = nodo

                i = i + 1
                actual = actual.siguiente

            dot += "}\n"

    dot += dot_footer()
    guardar_dot_y_png(dot, "reporte_1_general")


def reporte_vms_por_centro(listaCentros, centroId):
    dot = dot_header("Reporte: Vms del Centro " + str(centroId))

    centro = None
    actual = listaCentros.inicio
    while actual is not None:
        if str(actual.dato.id) == str(centroId):
            centro = actual.dato
            break
        actual = actual.siguiente

    if centro is None:
        dot += 'X [shape=box, label="No existe el centro ' + escape_label(centroId) + '"];\n'
        dot += dot_footer()
        guardar_dot_y_png(dot, "reporte_2_vms_centro_" + str(centroId))
        print("No existe un centro con ese Id")
        return

    dcId = escape_label(centro.id)
    dot += 'DC_' + dcId + ' [shape=folder, label="Centro ' + dcId + "\\n" + escape_label(centro.nombre) + '"];\n'

    nodoVm = centro.maquinas_virtuales.inicio
    if nodoVm is None:
        dot += 'V0 [shape=box, label="Este centro no tiene Vms"];\n'
        dot += "DC_" + dcId + " -> V0;\n"
    else:
        while nodoVm is not None:
            vm = nodoVm.dato
            vmId = escape_label(vm.id)
            dot += 'VM_' + vmId + ' [shape=box3d, label="Vm ' + vmId + "\\nSo: " + escape_label(vm.sistema_operativo) + "\\nEstado: " + escape_label(vm.estado) + '"];\n'
            dot += "DC_" + dcId + " -> VM_" + vmId + ";\n"
            nodoVm = nodoVm.siguiente

    dot += dot_footer()
    guardar_dot_y_png(dot, "reporte_2_vms_centro_" + str(centroId))


def reporte_contenedores_por_vm(listaCentros, vmIdBuscar):
    dot = dot_header("Reporte: Contenedores de la Vm " + str(vmIdBuscar))

    vmEncontrada = None
    dcDueno = None

    nodoCentro = listaCentros.inicio
    while nodoCentro is not None and vmEncontrada is None:
        dc = nodoCentro.dato
        nodoVm = dc.maquinas_virtuales.inicio
        while nodoVm is not None:
            vm = nodoVm.dato
            if str(vm.id) == str(vmIdBuscar):
                vmEncontrada = vm
                dcDueno = dc
                break
            nodoVm = nodoVm.siguiente
        nodoCentro = nodoCentro.siguiente

    if vmEncontrada is None:
        dot += 'X [shape=box, label="No existe la Vm ' + escape_label(vmIdBuscar) + '"];\n'
        dot += dot_footer()
        guardar_dot_y_png(dot, "reporte_3_contenedores_vm_" + str(vmIdBuscar))
        print("Vm no encontrada")
        return

    dcId = escape_label(dcDueno.id)
    vmId = escape_label(vmEncontrada.id)

    dot += 'DC_' + dcId + ' [shape=folder, label="Centro ' + dcId + "\\n" + escape_label(dcDueno.nombre) + '"];\n'
    dot += 'VM_' + vmId + ' [shape=box3d, label="Vm ' + vmId + "\\nSo: " + escape_label(vmEncontrada.sistema_operativo) + "\\nEstado: " + escape_label(vmEncontrada.estado) + '"];\n'
    dot += "DC_" + dcId + " -> VM_" + vmId + ";\n"

    nodoCont = vmEncontrada.contenedores.inicio
    if nodoCont is None:
        dot += 'C0 [shape=box, label="Esta Vm no tiene contenedores"];\n'
        dot += "VM_" + vmId + " -> C0;\n"
    else:
        while nodoCont is not None:
            ct = nodoCont.dato
            ctId = escape_label(ct.id)
            ctNom = escape_label(ct.nombre)
            ctImg = escape_label(ct.imagen)
            ctEst = escape_label(ct.estado)
            dot += 'CT_' + ctId + ' [shape=component, label="Cont ' + ctId + "\\n" + ctNom + "\\n" + ctImg + "\\nEstado: " + ctEst + '"];\n'
            dot += "VM_" + vmId + " -> CT_" + ctId + ";\n"
            nodoCont = nodoCont.siguiente

    dot += dot_footer()
    guardar_dot_y_png(dot, "reporte_3_contenedores_vm_" + str(vmIdBuscar))


def reporte_cola_solicitudes(colaSol):
    dot = dot_header("Reporte: Cola de Solicitudes (prioridad)")

    if colaSol is None or colaSol.inicio is None:
        dot += 'X [shape=box, label="La cola está vacía o no existe"];\n'
        dot += dot_footer()
        guardar_dot_y_png(dot, "reporte_4_cola_solicitudes")
        print("La cola está vacía o no existe")
        return

    actual = colaSol.inicio
    i = 1
    prev = ""
    while actual is not None:
        s = actual.solicitud
        sid = escape_label(s.id)
        st = escape_label(s.tipo)
        sp = escape_label(s.prioridad)

        nodo = "N" + str(i)
        dot += nodo + ' [shape=record, label="{ ' + sid + " | " + st + " | P:" + sp + ' }"];\n'
        if prev != "":
            dot += prev + " -> " + nodo + ";\n"
        prev = nodo

        i = i + 1
        actual = actual.siguiente

    dot += dot_footer()
    guardar_dot_y_png(dot, "reporte_4_cola_solicitudes")


def menu_reportes_graphviz(listaCentros, colaSol, historial):
    while True:
        print("\n=== REPORTES GRAPHVIZ ===")
        print("1. Reporte general (Centros -> Vms -> Contenedores)")
        print("2. Reporte de Vms por Centro (por Id)")
        print("3. Reporte de Contenedores por Vm (por Id)")
        print("4. Reporte de Cola de Solicitudes")
        print("5. Generar todos")
        print("6. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            reporte_general(listaCentros, colaSol)
            registrar_operacion(historial, "Reportes", "Se genero reporte general")

        elif op == "2":
            centroId = input("Ingrese el Id del centro (ej: DC001): ")
            reporte_vms_por_centro(listaCentros, centroId)
            registrar_operacion(historial, "Reportes", "Se genero reporte de Vms por centro: " + str(centroId))

        elif op == "3":
            vmId = input("Ingrese el Id de la Vm (ej: VM001): ")
            reporte_contenedores_por_vm(listaCentros, vmId)
            registrar_operacion(historial, "Reportes", "Se genero reporte de contenedores por Vm: " + str(vmId))

        elif op == "4":
            reporte_cola_solicitudes(colaSol)
            registrar_operacion(historial, "Reportes", "Se genero reporte de cola de solicitudes")

        elif op == "5":
            reporte_general(listaCentros, colaSol)
            centroId = input("Id centro para reporte 2 (ej: DC001): ")
            reporte_vms_por_centro(listaCentros, centroId)
            vmId = input("Id Vm para reporte 3 (ej: VM001): ")
            reporte_contenedores_por_vm(listaCentros, vmId)
            reporte_cola_solicitudes(colaSol)
            registrar_operacion(historial, "Reportes", "Se generaron todos los reportes")

        elif op == "6":
            break
        else:
            print("Opcion invalida")


# -------------------------
# Menús de gestión
# -------------------------
def menu_centros(listaCentros):
    while True:
        print("\n=== GESTIÓN DE CENTROS DE DATOS ===")
        print("1. Listar todos los centros")
        print("2. Buscar centro por Id")
        print("3. Ver centro con más cpu disponible")
        print("4. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            actual = listaCentros.inicio
            if actual is None:
                print("No hay centros registrados")
            else:
                n = 1
                while actual is not None:
                    dc = actual.dato
                    print("\n" + str(n) + ". Centro: " + str(dc.nombre) + " (" + str(dc.id) + ")")
                    print("Ubicación:", dc.ubicacion)
                    print("Cpu disponible:", dc.cpu_total - dc.cpu_usado)
                    print("Ram disponible:", dc.ram_total - dc.ram_usado)
                    print("Almacenamiento disponible:", dc.alm_total - dc.alm_usado)
                    print("Vms registradas:", dc.maquinas_virtuales.contar())
                    n = n + 1
                    actual = actual.siguiente

        elif op == "2":
            buscado = input("Ingrese el Id del centro (ej: DC001): ")
            actual = listaCentros.inicio
            enc = False
            while actual is not None:
                dc = actual.dato
                if str(dc.id) == str(buscado):
                    print("\nCentro encontrado")
                    print("Id:", dc.id)
                    print("Nombre:", dc.nombre)
                    print("Ubicación:", dc.ubicacion)
                    print("Cpu disponible:", dc.cpu_total - dc.cpu_usado)
                    print("Ram disponible:", dc.ram_total - dc.ram_usado)
                    print("Almacenamiento disponible:", dc.alm_total - dc.alm_usado)
                    print("Vms registradas:", dc.maquinas_virtuales.contar())
                    enc = True
                    break
                actual = actual.siguiente
            if not enc:
                print("No existe centro con ese Id")

        elif op == "3":
            actual = listaCentros.inicio
            if actual is None:
                print("No hay centros registrados")
                continue

            mejor = actual.dato
            actual = actual.siguiente

            while actual is not None:
                dc = actual.dato
                cpuMejor = mejor.cpu_total - mejor.cpu_usado
                cpuAct = dc.cpu_total - dc.cpu_usado
                if cpuAct > cpuMejor:
                    mejor = dc
                actual = actual.siguiente

            print("\nCentro con mas cpu disponible")
            print("Id:", mejor.id)
            print("Nombre:", mejor.nombre)
            print("Ubicación:", mejor.ubicacion)
            print("Cpu disponible:", mejor.cpu_total - mejor.cpu_usado)
            print("Ram disponible:", mejor.ram_total - mejor.ram_usado)
            print("Almacenamiento disponible:", mejor.alm_total - mejor.alm_usado)

        elif op == "4":
            break
        else:
            print("Opcion invalida")


def menu_vms(listaCentros):
    while True:
        print("\n=== GESTIÓN DE MÁQUINAS VIRTUALES ===")
        print("1. Buscar Vm por Id")
        print("2. Listar Vms de un centro")
        print("3. Migrar Vm entre centros")
        print("4. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            buscada = input("Id de la Vm a buscar: life's ")
            
            vmEncontrada = None
            dcDueno = None

            nodoCentro = listaCentros.inicio
            while nodoCentro is not None and vmEncontrada is None:
                dc = nodoCentro.dato
                nodoVm = dc.maquinas_virtuales.inicio
                while nodoVm is not None:
                    vm = nodoVm.dato
                    if str(vm.id) == str(buscada):
                        vmEncontrada = vm
                        dcDueno = dc
                        break
                    nodoVm = nodoVm.siguiente
                nodoCentro = nodoCentro.siguiente

            if vmEncontrada is None:
                print("No existe Vm con ese Id")
            else:
                print("\n--- Vm encontrada ---")
                print("Id:", vmEncontrada.id)
                print("Sistema Operativo:", vmEncontrada.sistema_operativo)
                print("Cpu:", vmEncontrada.cpu)
                print("Ram:", vmEncontrada.ram)
                print("Almacenamiento:", vmEncontrada.almacenamiento)
                print("Estado:", vmEncontrada.estado)
                print("Centro asignado:", dcDueno.id)

                print("Contenedores:")
                if vmEncontrada.contenedores.contar() == 0:
                    print("No hay contenedores")
                else:
                    nodoC = vmEncontrada.contenedores.inicio
                    while nodoC is not None:
                        cont = nodoC.dato
                        print("- " + str(cont.id) + " | " + str(cont.nombre) + " | " + str(getattr(cont, "imagen", "")))
                        nodoC = nodoC.siguiente

        elif op == "2":
            centroId = input("Id del centro (ej: DC001): ")
            dc = None
            actual = listaCentros.inicio
            while actual is not None:
                if str(actual.dato.id) == str(centroId):
                    dc = actual.dato
                    break
                actual = actual.siguiente

            if dc is None:
                print("No existe un centro con ese Id")
            else:
                print("\n--- Vms en el centro " + str(dc.id) + " ---")
                if dc.maquinas_virtuales.contar() == 0:
                    print("No hay Vms en este centro")
                else:
                    nodoVm = dc.maquinas_virtuales.inicio
                    n = 1
                    while nodoVm is not None:
                        vm = nodoVm.dato
                        print(str(n) + ". Vm: " + str(vm.id))
                        print("   Sistema Operativo:", vm.sistema_operativo)
                        print("   Cpu:", vm.cpu)
                        print("   Ram:", vm.ram)
                        print("   Almacenamiento:", vm.almacenamiento)
                        print("   Estado:", vm.estado)
                        print("   Contenedores:", vm.contenedores.contar())
                        n = n + 1
                        nodoVm = nodoVm.siguiente

        elif op == "3":
            vmId = input("Id de la Vm a migrar: ")
            destinoId = input("Centro destino (ej: DC002): ")

            centroOrigen = None
            centroDestino = None
            vmEncontrada = None

            # buscar centro destino
            actual = listaCentros.inicio
            while actual is not None:
                if str(actual.dato.id) == str(destinoId):
                    centroDestino = actual.dato
                    break
                actual = actual.siguiente

            if centroDestino is None:
                print("Centro destino no existe")
                continue

            # buscar Vm y origen
            actual = listaCentros.inicio
            while actual is not None and vmEncontrada is None:
                dc = actual.dato
                nodoVm = dc.maquinas_virtuales.inicio
                while nodoVm is not None:
                    if str(nodoVm.dato.id) == str(vmId):
                        vmEncontrada = nodoVm.dato
                        centroOrigen = dc
                        break
                    nodoVm = nodoVm.siguiente
                actual = actual.siguiente

            if vmEncontrada is None:
                print("Vm no encontrada")
                continue

            if str(centroOrigen.id) == str(centroDestino.id):
                print("La Vm ya se encuentra en el centro destino")
                continue

            # validar recursos del centro destino
            cpuDisp = centroDestino.cpu_total - centroDestino.cpu_usado
            ramDisp = centroDestino.ram_total - centroDestino.ram_usado
            almDisp = centroDestino.alm_total - centroDestino.alm_usado

            if cpuDisp < vmEncontrada.cpu or ramDisp < vmEncontrada.ram or almDisp < vmEncontrada.almacenamiento:
                print("Recursos insuficientes en el centro destino")
                continue

            # migrar: eliminar en origen y agregar en destino
            centroOrigen.eliminar_vm(vmEncontrada.id)
            centroOrigen.cpu_usado = centroOrigen.cpu_usado - vmEncontrada.cpu
            centroOrigen.ram_usado = centroOrigen.ram_usado - vmEncontrada.ram
            centroOrigen.alm_usado = centroOrigen.alm_usado - vmEncontrada.almacenamiento

            centroDestino.maquinas_virtuales.insertar_final(vmEncontrada)
            centroDestino.cpu_usado = centroDestino.cpu_usado + vmEncontrada.cpu
            centroDestino.ram_usado = centroDestino.ram_usado + vmEncontrada.ram
            centroDestino.alm_usado = centroDestino.alm_usado + vmEncontrada.almacenamiento

            print("Vm migrada correctamente de", centroOrigen.id, "a", centroDestino.id)

        elif op == "4":
            break
        else:
            print("Opcion invalida")


def menu_contenedores(listaCentros):
    while True:
        print("\n=== GESTIÓN DE CONTENEDORES ===")
        print("1. Listar contenedores de una Vm")
        print("2. Desplegar contenedor en Vm")
        print("3. Cambiar estado de contenedor")
        print("4. Eliminar contenedor")
        print("5. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            vmId = input("Id de la Vm: ")
            vmEncontrada = None

            nodoCentro = listaCentros.inicio
            while nodoCentro is not None and vmEncontrada is None:
                dc = nodoCentro.dato
                nodoVm = dc.maquinas_virtuales.inicio
                while nodoVm is not None:
                    if str(nodoVm.dato.id) == str(vmId):
                        vmEncontrada = nodoVm.dato
                        break
                    nodoVm = nodoVm.siguiente
                nodoCentro = nodoCentro.siguiente

            if vmEncontrada is None:
                print("Vm no encontrada")
            else:
                print("\n--- CONTENEDORES EN Vm " + str(vmEncontrada.id) + " ---")
                if vmEncontrada.contenedores.contar() == 0:
                    print("No hay contenedores en esta Vm")
                else:
                    nodoCont = vmEncontrada.contenedores.inicio
                    while nodoCont is not None:
                        print(nodoCont.dato)
                        nodoCont = nodoCont.siguiente

        elif op == "2":
            vmId = input("Id de la Vm destino: ")
            contId = input("Id del contenedor: ")
            nombre = input("Nombre del contenedor: ")
            imagen = input("Imagen (ej: nginx:latest): ")

            try:
                cpu = int(input("Cpu requerida: "))
                ram = int(input("Ram requerida: "))
            except:
                print("Cpu y Ram deben ser numeros")
                continue

            vmEncontrada = None
            nodoCentro = listaCentros.inicio
            while nodoCentro is not None and vmEncontrada is None:
                dc = nodoCentro.dato
                nodoVm = dc.maquinas_virtuales.inicio
                while nodoVm is not None:
                    if str(nodoVm.dato.id) == str(vmId):
                        vmEncontrada = nodoVm.dato
                        break
                    nodoVm = nodoVm.siguiente
                nodoCentro = nodoCentro.siguiente

            if vmEncontrada is None:
                print("Vm no encontrada")
                continue

            if cpu > vmEncontrada.cpu or ram > vmEncontrada.ram:
                print("Falta de recursos en la Vm")
                continue

            nuevo = Contenedor(contId, nombre, imagen, cpu, ram)
            vmEncontrada.cpu = vmEncontrada.cpu - cpu
            vmEncontrada.ram = vmEncontrada.ram - ram
            vmEncontrada.contenedores.insertar_final(nuevo)

            print("Contenedor desplegado correctamente en la Vm", vmId)

        elif op == "3":
            contId = input("Id del contenedor: ")
            contEncontrado = None

            nodoCentro = listaCentros.inicio
            while nodoCentro is not None and contEncontrado is None:
                dc = nodoCentro.dato
                nodoVm = dc.maquinas_virtuales.inicio

                while nodoVm is not None and contEncontrado is None:
                    vm = nodoVm.dato
                    nodoCont = vm.contenedores.inicio

                    while nodoCont is not None:
                        if str(nodoCont.dato.id) == str(contId):
                            contEncontrado = nodoCont.dato
                            break
                        nodoCont = nodoCont.siguiente

                    nodoVm = nodoVm.siguiente

                nodoCentro = nodoCentro.siguiente

            if contEncontrado is None:
                print("Contenedor no encontrado")
                continue

            print("\nEstado actual:", contEncontrado.estado)
            print("1. Activo")
            print("2. Pausado")
            print("3. Detenido")
            opEst = input("Seleccione nuevo estado: ")

            if opEst == "1":
                contEncontrado.estado = "Activo"
            elif opEst == "2":
                contEncontrado.estado = "Pausado"
            elif opEst == "3":
                contEncontrado.estado = "Detenido"
            else:
                print("Estado invalido")
                continue

            print("Estado actualizado:", contEncontrado.estado)

        elif op == "4":
            contId = input("Id del contenedor a eliminar: ")
            eliminado = False

            nodoCentro = listaCentros.inicio
            while nodoCentro is not None and not eliminado:
                dc = nodoCentro.dato
                nodoVm = dc.maquinas_virtuales.inicio

                while nodoVm is not None and not eliminado:
                    vm = nodoVm.dato
                    nodoCont = vm.contenedores.inicio
                    ant = None

                    while nodoCont is not None:
                        cont = nodoCont.dato
                        if str(cont.id) == str(contId):
                            # devolver recursos
                            vm.cpu = vm.cpu + cont.cpu
                            vm.ram = vm.ram + cont.ram

                            if ant is None:
                                vm.contenedores.inicio = nodoCont.siguiente
                            else:
                                ant.siguiente = nodoCont.siguiente

                            eliminado = True
                            print("Contenedor eliminado correctamente")
                            break

                        ant = nodoCont
                        nodoCont = nodoCont.siguiente

                    nodoVm = nodoVm.siguiente

                nodoCentro = nodoCentro.siguiente

            if not eliminado:
                print("Contenedor no encontrado")

        elif op == "5":
            break
        else:
            print("Opcion invalida")


def menu_solicitudes(procesador):
    while True:
        print("\n=== GESTIÓN DE SOLICITUDES ===")
        print("1. Agregar nueva solicitud")
        print("2. Procesar solicitud de mayor prioridad")
        print("3. Procesar N solicitudes")
        print("4. Ver cola de solicitudes")
        print("5. Volver")
        op = input("Seleccione una opcion: ")

        if op == "1":
            solId = input("Id de la solicitud: ")
            cliente = input("Cliente: ")
            tipo = input("Tipo (Deploy / Backup): ")

            try:
                prioridad = int(input("Prioridad (1 a 10): "))
            except:
                print("La prioridad debe ser un número")
                continue

            if prioridad < 1 or prioridad > 10:
                print("La prioridad debe estar entre 1 y 10")
                continue

            desc = "Cliente: " + str(cliente)
            nueva = Solicitud(solId, tipo, prioridad, desc)
            procesador.cola_solicitudes.agregar_solicitud(nueva)
            print("Solicitud agregada a la cola")

        elif op == "2":
            if procesador.cola_solicitudes.esta_vacia():
                print("No hay solicitudes en la cola")
                continue

            sol = procesador.cola_solicitudes.sacar_siguiente()
            print("Procesando solicitud:")
            print(sol)

            try:
                if sol.tipo == "Deploy":
                    procesador.procesar_deploy(sol)
                elif sol.tipo == "Backup":
                    procesador.procesar_backup(sol)
                else:
                    print("Tipo de solicitud desconocido")
                    continue
                print("Solicitud procesada correctamente")
            except:
                print("Error al procesar la solicitud")

        elif op == "3":
            try:
                cant = int(input("Cantidad de solicitudes a procesar: "))
            except:
                print("Debe ingresar un numero")
                continue

            proc, comp, fall = procesador.procesar_solicitudes(cant)
            print("\nResumen del procesamiento")
            print("Procesadas:", proc)
            print("Completadas:", comp)
            print("Fallidas:", fall)

        elif op == "4":
            if procesador.cola_solicitudes.esta_vacia():
                print("No hay solicitudes en la cola")
            else:
                procesador.cola_solicitudes.mostrar_cola()

        elif op == "5":
            break
        else:
            print("Opcion invalida")


# -------------------------
# Main
# -------------------------
def main():
    parser = None
    datosCargados = False

    listaCentros = None
    procesador = None
    cola = None

    historial = ListaSimple()

    while True:
        mostrar_menu_principal()
        opcion = input("Seleccione una opcion: ")

        # 1) Cargar XML
        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML: ")
            parser = ParserXML()

            if parser.cargar_archivo_xml(ruta):
                print("\nCargando archivo...")

                # construir lista de centros
                listaCentros = ListaSimple()
                nodoDc = parser.datacenters.inicio
                while nodoDc is not None:
                    dcObj = nodoDc.dato

                    nuevoDc = DataCenter(dcObj.id, dcObj.nombre, dcObj.ubicacion)
                    nuevoDc.cpu_total = dcObj.cpu_total
                    nuevoDc.ram_total = dcObj.ram_total
                    nuevoDc.alm_total = dcObj.alm_total

                    nuevoDc.cpu_usado = 0
                    nuevoDc.ram_usado = 0
                    nuevoDc.alm_usado = 0

                    listaCentros.insertar_final(nuevoDc)
                    nodoDc = nodoDc.siguiente

                # cargar Vms a su centro
                nodoVm = parser.maquinas_virtuales.inicio
                while nodoVm is not None:
                    vmObj = nodoVm.dato
                    centroId = str(vmObj.centro_asignado)

                    actualCentro = listaCentros.inicio
                    while actualCentro is not None:
                        dc = actualCentro.dato
                        if str(dc.id) == str(centroId):
                            nuevaVm = MaquinaVirtual(vmObj.id, vmObj.nombre, vmObj.sistema_operativo)
                            nuevaVm.cpu = vmObj.cpu
                            nuevaVm.ram = vmObj.ram
                            nuevaVm.almacenamiento = vmObj.almacenamiento
                            nuevaVm.estado = vmObj.estado
                            # sumar uso al centro
                            dc.maquinas_virtuales.insertar_final(nuevaVm)
                            dc.cpu_usado = dc.cpu_usado + nuevaVm.cpu
                            dc.ram_usado = dc.ram_usado + nuevaVm.ram
                            dc.alm_usado = dc.alm_usado + nuevaVm.almacenamiento
                            break

                        actualCentro = actualCentro.siguiente

                    nodoVm = nodoVm.siguiente

                # cargar contenedores
                nodoCont = parser.contenedores.inicio
                while nodoCont is not None:
                    ctObj = nodoCont.dato
                    vmIdDestino = str(ctObj.vm_asignada)
                    
                    nodoCentro = listaCentros.inicio
                    while nodoCentro is not None:
                        dc = nodoCentro.dato
                        nodoVm2 = dc.maquinas_virtuales.inicio

                        while nodoVm2 is not None:
                            vm = nodoVm2.dato
                            if str(vm.id) == str(vmIdDestino):
                                nuevoCont = Contenedor(ctObj.id, ctObj.nombre, ctObj.imagen, ctObj.cpu, ctObj.ram)
                                vm.contenedores.insertar_final(nuevoCont)
                                break
                            nodoVm2 = nodoVm2.siguiente

                        nodoCentro = nodoCentro.siguiente

                    nodoCont = nodoCont.siguiente

                # cola de solicitudes
                cola = ColaPrioridad()
                nodoSol = parser.solicitudes.inicio
                while nodoSol is not None:
                    cola.agregar_solicitud(nodoSol.dato)
                    nodoSol = nodoSol.siguiente

                procesador = ProcesadorSolicitudes(listaCentros)
                procesador.asignar_cola(cola)

                datosCargados = True
                print("Datos cargados correctamente.\n")
                registrar_operacion(historial, "Carga XML", "Se cargo el archivo: " + str(ruta))

                # ejecutar instrucciones
                print("\n=== Ejecutando instrucciones ===")
                nodoInst = parser.instrucciones.inicio
                while nodoInst is not None:
                    inst = nodoInst.dato
                    tipoInst = inst.tipo

                    if tipoInst == "crearVM":
                        print("Instrucción crearVm detectada (en este parser solo se registró el tipo)")
                        registrar_operacion(historial, "Instruccion", "Se detecto crearVm")

                    elif tipoInst == "migrarVM":
                        print("Instrucción migrarVm detectada (en este parser solo se registró el tipo)")
                        registrar_operacion(historial, "Instruccion", "Se detectó migrarVm")

                    elif tipoInst == "procesarSolicitudes":
                        # procesar todas las que existan en cola 
                        cant = 0
                        aux = procesador.cola_solicitudes.inicio
                        while aux is not None:
                            cant = cant + 1
                            aux = aux.siguiente

                        proc, comp, fall = procesador.procesar_solicitudes(cant)
                        print("Procesadas:", proc, "Completadas:", comp, "Fallidas:", fall)

                        registrar_operacion(
                            historial,
                            "Procesar solicitudes",
                            "Cantidad: " + str(cant) + " | Procesadas: " + str(proc) + " | Completadas: " + str(comp) + " | Fallidas: " + str(fall)
                        )

                    nodoInst = nodoInst.siguiente

                print("\nArchivo XML cargado exitosamente\n")

            else:
                print("No se pudo cargar el archivo")

        # 2) Centros
        elif opcion == "2":
            if not datosCargados:
                print("Primero cargue un archivo XML")
            else:
                menu_centros(listaCentros)

        # 3) Vms
        elif opcion == "3":
            if not datosCargados:
                print("Primero cargue un archivo XML")
            else:
                menu_vms(listaCentros)

        # 4) Contenedores
        elif opcion == "4":
            if not datosCargados:
                print("Primero cargue un archivo XML")
            else:
                menu_contenedores(listaCentros)

        # 5) Solicitudes
        elif opcion == "5":
            if not datosCargados or procesador is None:
                print("Primero cargue un archivo XML")
            else:
                menu_solicitudes(procesador)

        # 6) Reportes
        elif opcion == "6":
            if not datosCargados or listaCentros is None:
                print("Primero cargue un archivo XML")
            else:
                colaReal = None
                if procesador is not None:
                    colaReal = procesador.cola_solicitudes
                menu_reportes_graphviz(listaCentros, colaReal, historial)

        # 7) XML salida
        elif opcion == "7":
            if not datosCargados or listaCentros is None:
                print("Primero cargue un archivo XML")
            else:
                ok = generar_xml_salida(listaCentros)
                if ok:
                    registrar_operacion(historial, "XML de salida", "Se generó el XML de salida")
                else:
                    registrar_operacion(historial, "XML de salida", "Falló la generación del XML de salida")

        # 8) Historial
        elif opcion == "8":
            menu_historial(historial)

        # 9) Salir
        elif opcion == "9":
            registrar_operacion(historial, "Salir", "El usuario salió del sistema")
            print("Saliendo del sistema...")
            break

        else:
            print("Opcion invalida. Intente de nuevo.")


if __name__ == "__main__":
    main()
