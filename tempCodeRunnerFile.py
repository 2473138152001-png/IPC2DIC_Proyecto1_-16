# main.py
# CloudSync Manager - Sistema de Nube
# Menú principal según especificación del proyecto

import os
import xml.etree.ElementTree as ET
from datetime import datetime

from src.core.procesador import ProcesadorSolicitudes
from src.data_structures.cola_prioridad import ColaPrioridad
from src.models.solicitud import Solicitud
from src.parser.parser import ParserXML
from src.models.data_center import DataCenter
from src.data_structures.lista_simple import ListaSimple
from src.models.maquina_virtual import MaquinaVirtual


# ==========================
# CONFIG RUTAS FIJAS (SEGÚN USTED)
# ==========================
RUTA_REPORTES = r"C:\Users\macoe\OneDrive\Documentos\python\progra2Vaqueros\IPC2DIC_Proyecto1_-16\src\reportes"
RUTA_TESTS = r"C:\Users\macoe\OneDrive\Documentos\python\progra2Vaqueros\IPC2DIC_Proyecto1_-16\src\tests"


# ==========================
# HISTORIAL DE OPERACIONES (SEGÚN SU CLASE)
# ==========================
class Operacion:
    def __init__(self, fecha, action, detalles):
        self.fecha = fecha
        self.action = action
        self.detalles = detalles

    def __str__(self):
        return f"[{self.fecha}] {self.action} -> {self.detalles}"


def registrar_operacion(historial, action, detalles):
    try:
        fecha = datetime.now().isoformat()
    except:
        fecha = "sin_fecha"
    op = Operacion(fecha, str(action), str(detalles))
    historial.insertar_final(op)


def _contiene(texto, patron):
    if texto is None or patron is None:
        return False
    return str(patron).lower() in str(texto).lower()


def exportar_historial_xml(historial):
    os.makedirs(RUTA_TESTS, exist_ok=True)
    ruta_xml = os.path.join(RUTA_TESTS, "historialOperaciones.xml")

    root = ET.Element("historialOperaciones")
    ts = ET.SubElement(root, "timestamp")
    ts.text = datetime.now().isoformat()

    operaciones = ET.SubElement(root, "operaciones")

    actual = historial.inicio
    while actual is not None:
        opx = actual.dato
        nodo = ET.SubElement(operaciones, "operacion")
        ET.SubElement(nodo, "fecha").text = str(opx.fecha)
        ET.SubElement(nodo, "action").text = str(opx.action)
        ET.SubElement(nodo, "detalles").text = str(opx.detalles)
        actual = actual.siguiente

    _indent_xml(root)
    tree = ET.ElementTree(root)

    try:
        tree.write(ruta_xml, encoding="utf-8", xml_declaration=True)
        print("Historial exportado correctamente.")
        print("XML:", ruta_xml)
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
        op = input("Seleccione una opción: ").strip()

        if op == "1":
            if historial.inicio is None:
                print("No hay operaciones registradas.")
                continue

            actual = historial.inicio
            contador = 1
            while actual is not None:
                print(f"{contador}. {actual.dato}")
                contador += 1
                actual = actual.siguiente

        elif op == "2":
            palabra = input("Palabra a buscar: ").strip()
            if palabra == "":
                print("Busqueda vacia.")
                continue

            actual = historial.inicio
            encontrados = 0
            while actual is not None:
                opx = actual.dato
                if (_contiene(opx.fecha, palabra) or
                    _contiene(opx.action, palabra) or
                    _contiene(opx.detalles, palabra)):
                    print(opx)
                    encontrados += 1
                actual = actual.siguiente

            if encontrados == 0:
                print("No se encontraron coincidencias.")

        elif op == "3":
            exportar_historial_xml(historial)

        elif op == "4":
            historial.inicio = None
            print("Historial limpiado correctamente.")

        elif op == "5":
            break

        else:
            print("Opcion invalida.")


def mostrar_menu():
    print("\n===================================")
    print("  CLOUDSYNC MANAGER - SISTEMA DE NUBE")
    print("===================================")
    print("1. Cargar Archivo XML")
    print("2. Gestión de Centros de Datos")
    print("3. Gestión de Máquinas Virtuales")
    print("4. Gestión de Contenedores")
    print("5. Gestión de Solicitudes")
    print("6. Reportes Graphviz")
    print("7. Generar XML de Salida")
    print("8. Historial de Operaciones")
    print("9. Salir")
    print("===================================")


def _escape_label(texto):
    if texto is None:
        return ""
    return str(texto).replace('"', '\\"')


def _guardar_dot_y_png(dot_text, nombre_base):
    """
    Guarda .dot y .png en RUTA_REPORTES.
    nombre_base: ejemplo "reporte_general" => genera reporte_general.dot y reporte_general.png
    """
    os.makedirs(RUTA_REPORTES, exist_ok=True)

    ruta_dot = os.path.join(RUTA_REPORTES, f"{nombre_base}.dot")
    ruta_png = os.path.join(RUTA_REPORTES, f"{nombre_base}.png")

    try:
        with open(ruta_dot, "w", encoding="utf-8") as f:
            f.write(dot_text)
    except Exception as e:
        print("No se pudo crear el archivo .dot:", e)
        print("Intentó guardar en:", ruta_dot)
        return

    prueba = os.system("dot -V")
    if prueba != 0:
        print("Se creo el .dot pero NO se pudo generar el .png (Graphviz no está en PATH).")
        print("DOT:", ruta_dot)
        return

    comando = f'dot -Tpng "{ruta_dot}" -o "{ruta_png}"'
    resultado = os.system(comando)

    if resultado == 0:
        print("Reporte generado correctamente:")
        print("DOT:", ruta_dot)
        print("PNG:", ruta_png)
    else:
        print("Se creo el .dot pero NO se pudo generar el .png.")
        print("Comando:", comando)


# ==========================
# ✅ REPORTES GRAPHVIZ (4 MÍNIMO)
# ==========================
def _dot_header(titulo):
    dot = "digraph CloudSync {\n"
    dot += "rankdir=LR;\n"
    dot += 'labelloc="t";\n'
    dot += f'label="{_escape_label(titulo)}";\n'
    dot += "fontsize=18;\n"
    dot += "node [shape=box];\n"
    dot += "edge [arrowhead=vee];\n\n"
    return dot


def _dot_footer():
    return "\n}\n"


def reporte_general(lista_data_centers, cola_solicitudes):
    dot = _dot_header("Reporte General: Centros -> VMs -> Contenedores")

    actual_dc = lista_data_centers.inicio
    while actual_dc is not None:
        dc = actual_dc.dato

        dc_id = _escape_label(dc.id)
        dc_nombre = _escape_label(dc.nombre)
        dc_ub = _escape_label(dc.ubicacion)

        cpu_total = getattr(dc, "cpu_total", 0)
        ram_total = getattr(dc, "ram_total", 0)
        alm_total = getattr(dc, "alm_total", 0)

        cpu_usado = getattr(dc, "cpu_usado", 0)
        ram_usado = getattr(dc, "ram_usado", 0)
        alm_usado = getattr(dc, "alm_usado", 0)

        dot += f'DC_{dc_id} [shape=folder, label="DC {dc_id}\\n{dc_nombre}\\n{dc_ub}\\nCPU {cpu_usado}/{cpu_total} | RAM {ram_usado}/{ram_total} | ALM {alm_usado}/{alm_total}"];\n'

        actual_vm = dc.maquinas_virtuales.inicio
        while actual_vm is not None:
            vm = actual_vm.dato

            vm_id = _escape_label(vm.id)
            so = _escape_label(vm.sistema_operativo)
            estado = _escape_label(vm.estado)

            dot += f'VM_{vm_id} [shape=box3d, label="VM {vm_id}\\nSO: {so}\\nEstado: {estado}\\nCPU:{vm.cpu} RAM:{vm.ram} ALM:{vm.almacenamiento}"];\n'
            dot += f"DC_{dc_id} -> VM_{vm_id};\n"

            actual_ct = vm.contenedores.inicio
            while actual_ct is not None:
                ct = actual_ct.dato

                ct_id = _escape_label(getattr(ct, "id", ""))
                ct_nombre = _escape_label(getattr(ct, "nombre", ""))
                ct_img = _escape_label(getattr(ct, "imagen", getattr(ct, "tipo", "")))
                ct_estado = _escape_label(getattr(ct, "estado", ""))

                dot += f'CT_{ct_id} [shape=component, label="CT {ct_id}\\n{ct_nombre}\\n{ct_img}\\nEstado: {ct_estado}"];\n'
                dot += f"VM_{vm_id} -> CT_{ct_id};\n"

                actual_ct = actual_ct.siguiente

            actual_vm = actual_vm.siguiente

        actual_dc = actual_dc.siguiente

    if cola_solicitudes is not None:
        dot += "\nsubgraph cluster_cola {\n"
        dot += 'label="Cola de Solicitudes (Prioridad)";\n'
        dot += "style=dashed;\n"

        actual = cola_solicitudes.inicio
        idx = 1
        prev = None
        while actual is not None:
            s = actual.solicitud
            sid = _escape_label(getattr(s, "id", ""))
            tipo = _escape_label(getattr(s, "tipo", ""))
            pr = _escape_label(getattr(s, "prioridad", ""))

            nodo = f"SOL_{idx}"
            dot += f'{nodo} [shape=note, label="{sid}\\n{tipo}\\nPrioridad: {pr}"];\n'
            if prev is not None:
                dot += f"{prev} -> {nodo};\n"
            prev = nodo

            idx += 1
            actual = actual.siguiente

        dot += "}\n"

    dot += _dot_footer()
    _guardar_dot_y_png(dot, "reporte_1_general")


def reporte_vms_por_centro(lista_data_centers, centro_id):
    dot = _dot_header(f"Reporte: VMs del Centro {centro_id}")

    centro = None
    actual = lista_data_centers.inicio
    while actual is not None:
        if str(actual.dato.id) == str(centro_id):
            centro = actual.dato
            break
        actual = actual.siguiente

    if centro is None:
        dot += f'X [shape=box, label="No existe el centro {centro_id}"];\n'
        dot += _dot_footer()
        _guardar_dot_y_png(dot, f"reporte_2_vms_centro_{centro_id}")
        print("No existe un centro con ese id.")
        return

    dc_id = _escape_label(centro.id)
    dot += f'DC_{dc_id} [shape=folder, label="Centro {dc_id}\\n{_escape_label(centro.nombre)}"];\n'

    actual_vm = centro.maquinas_virtuales.inicio
    if actual_vm is None:
        dot += 'V0 [shape=box, label="Este centro no tiene VMs"];\n'
        dot += f"DC_{dc_id} -> V0;\n"
    else:
        while actual_vm is not None:
            vm = actual_vm.dato
            vm_id = _escape_label(vm.id)
            dot += f'VM_{vm_id} [shape=box3d, label="VM {vm_id}\\nSO: {_escape_label(vm.sistema_operativo)}\\nEstado: {_escape_label(vm.estado)}"];\n'
            dot += f"DC_{dc_id} -> VM_{vm_id};\n"
            actual_vm = actual_vm.siguiente

    dot += _dot_footer()
    _guardar_dot_y_png(dot, f"reporte_2_vms_centro_{centro_id}")


def reporte_contenedores_por_vm(lista_data_centers, vm_id_buscar):
    dot = _dot_header(f"Reporte: Contenedores de la VM {vm_id_buscar}")

    vm_encontrada = None
    dc_dueno = None

    actual_dc = lista_data_centers.inicio
    while actual_dc is not None and vm_encontrada is None:
        dc = actual_dc.dato
        actual_vm = dc.maquinas_virtuales.inicio
        while actual_vm is not None:
            vm = actual_vm.dato
            if str(vm.id) == str(vm_id_buscar):
                vm_encontrada = vm
                dc_dueno = dc
                break
            actual_vm = actual_vm.siguiente
        actual_dc = actual_dc.siguiente

    if vm_encontrada is None:
        dot += f'X [shape=box, label="No existe la VM {vm_id_buscar}"];\n'
        dot += _dot_footer()
        _guardar_dot_y_png(dot, f"reporte_3_contenedores_vm_{vm_id_buscar}")
        print("VM no encontrada.")
        return

    dc_id = _escape_label(dc_dueno.id)
    vm_id = _escape_label(vm_encontrada.id)

    dot += f'DC_{dc_id} [shape=folder, label="Centro {dc_id}\\n{_escape_label(dc_dueno.nombre)}"];\n'
    dot += f'VM_{vm_id} [shape=box3d, label="VM {vm_id}\\nSO: {_escape_label(vm_encontrada.sistema_operativo)}\\nEstado: {_escape_label(vm_encontrada.estado)}"];\n'
    dot += f"DC_{dc_id} -> VM_{vm_id};\n"

    actual_ct = vm_encontrada.contenedores.inicio
    if actual_ct is None:
        dot += 'C0 [shape=box, label="Esta VM no tiene contenedores"];\n'
        dot += f"VM_{vm_id} -> C0;\n"
    else:
        while actual_ct is not None:
            ct = actual_ct.dato
            ct_id = _escape_label(getattr(ct, "id", ""))
            dot += (
                f'CT_{ct_id} [shape=component, label="CT {ct_id}\\n'
                f'{_escape_label(getattr(ct, "nombre", ""))}\\n'
                f'{_escape_label(getattr(ct, "imagen", ""))}\\n'
                f'Estado: {_escape_label(getattr(ct, "estado", ""))}"];\n'
            )
            dot += f"VM_{vm_id} -> CT_{ct_id};\n"
            actual_ct = actual_ct.siguiente

    dot += _dot_footer()
    _guardar_dot_y_png(dot, f"reporte_3_contenedores_vm_{vm_id_buscar}")


def reporte_cola_solicitudes(cola_solicitudes):
    dot = _dot_header("Reporte: Cola de Solicitudes (por prioridad)")

    if cola_solicitudes is None or cola_solicitudes.inicio is None:
        dot += 'X [shape=box, label="La cola está vacía o no existe"];\n'
        dot += _dot_footer()
        _guardar_dot_y_png(dot, "reporte_4_cola_solicitudes")
        print("La cola está vacía o no existe.")
        return

    dot += "rankdir=LR;\n"
    dot += "node [shape=record];\n\n"

    actual = cola_solicitudes.inicio
    i = 1
    prev = None
    while actual is not None:
        s = actual.solicitud
        sid = _escape_label(getattr(s, "id", ""))
        tipo = _escape_label(getattr(s, "tipo", ""))
        pr = _escape_label(getattr(s, "prioridad", ""))

        nodo = f"N{i}"
        dot += f'{nodo} [label="{{ {sid} | {tipo} | P:{pr} }}"];\n'
        if prev is not None:
            dot += f"{prev} -> {nodo};\n"
        prev = nodo

        i += 1
        actual = actual.siguiente

    dot += _dot_footer()
    _guardar_dot_y_png(dot, "reporte_4_cola_solicitudes")


def generar_reportes_graphviz_menu(lista_data_centers, cola_solicitudes):
    while True:
        print("\n=== REPORTES GRAPHVIZ ===")
        print("1. Reporte general (Centros -> VMs -> Contenedores)")
        print("2. Reporte de VMs por Centro (por ID)")
        print("3. Reporte de Contenedores por VM (por ID)")
        print("4. Reporte de Cola de Solicitudes (por prioridad)")
        print("5. Generar TODOS (1-4)")
        print("6. Volver")
        op = input("Seleccione una opción: ")

        if op == "1":
            reporte_general(lista_data_centers, cola_solicitudes)

        elif op == "2":
            centro_id = input("Ingrese el ID del centro (ej: DC001): ").strip()
            reporte_vms_por_centro(lista_data_centers, centro_id)

        elif op == "3":
            vm_id = input("Ingrese el ID de la VM (ej: VM001): ").strip()
            reporte_contenedores_por_vm(lista_data_centers, vm_id)

        elif op == "4":
            reporte_cola_solicitudes(cola_solicitudes)

        elif op == "5":
            reporte_general(lista_data_centers, cola_solicitudes)
            centro_id = input("ID centro para reporte 2 (ej: DC001): ").strip()
            reporte_vms_por_centro(lista_data_centers, centro_id)
            vm_id = input("ID VM para reporte 3 (ej: VM001): ").strip()
            reporte_contenedores_por_vm(lista_data_centers, vm_id)
            reporte_cola_solicitudes(cola_solicitudes)

        elif op == "6":
            break
        else:
            print("Opción inválida.")


# ==========================
# ✅ OPCIÓN 7: XML DE SALIDA
# ==========================
def _indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            _indent_xml(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def _porcentaje(usado, total):
    if total is None or total == 0:
        return "0.00%"
    try:
        p = (float(usado) / float(total)) * 100.0
        return f"{p:.2f}%"
    except:
        return "0.00%"


def generar_xml_salida_pdf(lista_data_centers):
    os.makedirs(RUTA_TESTS, exist_ok=True)
    ruta_xml = os.path.join(RUTA_TESTS, "resultadoCloudSync.xml")

    root = ET.Element("resultadoCloudSync")

    ts = ET.SubElement(root, "timestamp")
    ts.text = datetime.now().isoformat()

    estado_centros = ET.SubElement(root, "estadoCentros")

    total_vms = 0
    total_contenedores = 0
    vms_activas = 0

    actual_dc = lista_data_centers.inicio
    while actual_dc is not None:
        dc = actual_dc.dato

        centro = ET.SubElement(estado_centros, "centro", id=str(dc.id))
        ET.SubElement(centro, "nombre").text = str(dc.nombre)

        recursos = ET.SubElement(centro, "recursos")

        cpu_total = int(getattr(dc, "cpu_total", 0) or 0)
        ram_total = int(getattr(dc, "ram_total", 0) or 0)

        cpu_usado = int(getattr(dc, "cpu_usado", 0) or 0)
        ram_usado = int(getattr(dc, "ram_usado", 0) or 0)

        cpu_disp = cpu_total - cpu_usado
        ram_disp = ram_total - ram_usado
        if cpu_disp < 0:
            cpu_disp = 0
        if ram_disp < 0:
            ram_disp = 0

        ET.SubElement(recursos, "cpuTotal").text = str(cpu_total)
        ET.SubElement(recursos, "cpuDisponible").text = str(cpu_disp)
        ET.SubElement(recursos, "cpuUtilizacion").text = _porcentaje(cpu_usado, cpu_total)

        ET.SubElement(recursos, "ramTotal").text = str(ram_total)
        ET.SubElement(recursos, "ramDisponible").text = str(ram_disp)
        ET.SubElement(recursos, "ramUtilizacion").text = _porcentaje(ram_usado, ram_total)

        cant_vms = dc.maquinas_virtuales.contar()
        cant_cont = 0

        nodo_vm = dc.maquinas_virtuales.inicio
        while nodo_vm is not None:
            vm = nodo_vm.dato
            cant_cont += vm.contenedores.contar()

            est = str(getattr(vm, "estado", "") or "").strip().lower()
            if est in ("activa", "activo", "running", "encendida", "on"):
                vms_activas += 1

            nodo_vm = nodo_vm.siguiente

        ET.SubElement(centro, "cantidadVMs").text = str(cant_vms)
        ET.SubElement(centro, "cantidadContenedores").text = str(cant_cont)

        total_vms += cant_vms
        total_contenedores += cant_cont

        actual_dc = actual_dc.siguiente

    if vms_activas == 0:
        vms_activas = total_vms

    estadisticas = ET.SubElement(root, "estadisticas")
    ET.SubElement(estadisticas, "vmsActivas").text = str(vms_activas)
    ET.SubElement(estadisticas, "contenedoresTotales").text = str(total_contenedores)

    _indent_xml(root)
    tree = ET.ElementTree(root)

    try:
        tree.write(ruta_xml, encoding="utf-8", xml_declaration=True)
        print("XML de salida generado correctamente.")
        print("XML:", ruta_xml)
        return True
    except Exception as e:
        print("No se pudo generar el XML de salida:", e)
        return False


def main():
    parser = None
    datos_cargados = False

    lista_data_centers = None
    procesador = None
    cola = None

    # ✅ Historial en ListaSimple (no nativo)
    historial = ListaSimple()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ")

        # ==========================
        # ✅ OPCIÓN 1: CARGAR XML
        # ==========================
        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML: ")
            parser = ParserXML()

            if parser.cargar_archivo_xml(ruta):
                print("\nCargando archivo...")
                lista_data_centers = ListaSimple()

                # 1) Copiar DataCenters desde parser (ListaSimple)
                nodo_dc = parser.datacenters.inicio
                while nodo_dc is not None:
                    dc_obj = nodo_dc.dato

                    nuevo_dc = DataCenter(dc_obj.id, dc_obj.nombre, dc_obj.ubicacion)
                    nuevo_dc.cpu_total = getattr(dc_obj, "cpu_total", 0)
                    nuevo_dc.ram_total = getattr(dc_obj, "ram_total", 0)
                    nuevo_dc.alm_total = getattr(dc_obj, "alm_total", 0)

                    nuevo_dc.cpu_usado = 0
                    nuevo_dc.ram_usado = 0
                    nuevo_dc.alm_usado = 0

                    lista_data_centers.insertar_final(nuevo_dc)
                    nodo_dc = nodo_dc.siguiente

                # 2) Insertar VMs en su DC
                nodo_vm = parser.maquinas_virtuales.inicio
                while nodo_vm is not None:
                    vm_obj = nodo_vm.dato
                    centro_id = str(getattr(vm_obj, "centro_asignado", ""))

                    actual = lista_data_centers.inicio
                    while actual is not None:
                        dc = actual.dato
                        if str(dc.id) == centro_id:
                            nueva_vm = MaquinaVirtual(vm_obj.id, vm_obj.nombre, vm_obj.sistema_operativo)
                            nueva_vm.cpu = getattr(vm_obj, "cpu", 0)
                            nueva_vm.ram = getattr(vm_obj, "ram", 0)
                            nueva_vm.almacenamiento = getattr(vm_obj, "almacenamiento", 0)
                            nueva_vm.estado = getattr(vm_obj, "estado", "Activa")

                            try:
                                nueva_vm.ip = vm_obj.ip
                            except:
                                pass

                            dc.maquinas_virtuales.insertar_final(nueva_vm)

                            dc.cpu_usado += nueva_vm.cpu
                            dc.ram_usado += nueva_vm.ram
                            dc.alm_usado += nueva_vm.almacenamiento
                            break

                        actual = actual.siguiente

                    nodo_vm = nodo_vm.siguiente

                # 3) Insertar contenedores en su VM
                nodo_ct = parser.contenedores.inicio
                while nodo_ct is not None:
                    ct_obj = nodo_ct.dato
                    vm_id_dest = str(getattr(ct_obj, "vm_asignada", ""))

                    actual_dc = lista_data_centers.inicio
                    while actual_dc is not None:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato
                            if str(vm.id) == vm_id_dest:
                                from src.models.contenedor import Contenedor
                                nuevo_cont = Contenedor(ct_obj.id, ct_obj.nombre, ct_obj.imagen)
                                vm.contenedores.insertar_final(nuevo_cont)
                                break
                            actual_vm = actual_vm.siguiente

                        actual_dc = actual_dc.siguiente

                    nodo_ct = nodo_ct.siguiente

                # 4) Cola de solicitudes
                cola = ColaPrioridad()
                nodo_sol = parser.solicitudes.inicio
                while nodo_sol is not None:
                    s = nodo_sol.dato
                    cola.agregar_solicitud(s)
                    nodo_sol = nodo_sol.siguiente

                # 5) Procesador
                procesador = ProcesadorSolicitudes(lista_data_centers)
                procesador.asignar_cola(cola)

                datos_cargados = True
                print("Datos cargados correctamente.\n")

                registrar_operacion(historial, "CARGA_XML", f"Se cargo el archivo: {ruta}")

                # 6) Ejecutar instrucciones
                print("\n=== Ejecutando Instrucciones ===")
                nodo_inst = parser.instrucciones.inicio
                while nodo_inst is not None:
                    inst = nodo_inst.dato
                    tipo = getattr(inst, "tipo", "")

                    if tipo == "crearVM":
                        print("VM creada exitosamente")
                        registrar_operacion(historial, "INSTRUCCION", "crearVM ejecutada (mensaje)")

                    elif tipo == "migrarVM":
                        print("VM migrada exitosamente")
                        registrar_operacion(historial, "INSTRUCCION", "migrarVM ejecutada (mensaje)")

                    elif tipo == "procesarSolicitudes":
                        # ✅ AQUÍ ESTÁ EL ARREGLO:
                        # Procesa TODO como antes, sin pedir cantidad y sin len()
                        cantidad = 0
                        aux = procesador.cola_solicitudes.inicio
                        while aux is not None:
                            cantidad += 1
                            aux = aux.siguiente

                        procesadas, completadas, fallidas = procesador.procesar_solicitudes(cantidad)
                        print(f" Procesadas: {procesadas}, Completadas: {completadas}, Fallidas: {fallidas}")

                        registrar_operacion(
                            historial,
                            "PROCESAR_SOLICITUDES",
                            f"Cantidad:{cantidad} | Proc:{procesadas} Comp:{completadas} Fall:{fallidas}"
                        )

                    nodo_inst = nodo_inst.siguiente

                print("\nArchivo XML cargado exitosamente\n")
            else:
                print("No se pudo cargar el archivo.")

        elif opcion == "2":
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue
            print("Gestión Centros: (su código actual aquí sigue igual)")

        elif opcion == "3":
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML")
                continue
            print("Gestión VMs: (su código actual aquí sigue igual)")

        elif opcion == "4":
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue
            print("Gestióo Contenedores: ")

        elif opcion == "5":
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue
            print("Gestion Solicitudes: ")

        # se genera un dot y png con una grafica de los reportes
        elif opcion == "6":
            if not datos_cargados or lista_data_centers is None:
                print("Primero cargue un archivo XML.")
            else:
                cola_real = None
                if procesador is not None:
                    cola_real = procesador.cola_solicitudes

                generar_reportes_graphviz_menu(lista_data_centers, cola_real)
                registrar_operacion(historial, "reportes Graphviz", "Se generaron los reportes")

        # se encarga un archivo  xml de salida
        elif opcion == "7":
            if not datos_cargados or lista_data_centers is None:
                print("Primero cargue un archivo XML.")
            else:
                ok = generar_xml_salida_pdf(lista_data_centers)
                if ok:
                    registrar_operacion(historial, "XML de salida", "Se genero el resultado exitosamente")
                else:
                    registrar_operacion(historial, "XML de salida", "Fallo la generación del XML de salida")

        # la opcion 8 trata de guardar todos los movimientos y operaciones que hemos hecho
        elif opcion == "8":
            menu_historial(historial)

        elif opcion == "9":
            registrar_operacion(historial, "SALIR", "El usuario salio del sistema")
            print("Saliendo del sistema...")
            break

        else:
            print("Opcion invalida, Intente de nuevo")


if __name__ == "__main__":
    main()