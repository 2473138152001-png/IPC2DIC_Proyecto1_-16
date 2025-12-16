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
RUTA_REPORTES = r"C:\Users\macoe\OneDrive\Documentos\python\progra2Vaqueros\IPC2DIC_Proyecto1_-16\src\reportes"
RUTA_TESTS = r"C:\Users\macoe\OneDrive\Documentos\python\progra2Vaqueros\IPC2DIC_Proyecto1_-16\src\tests"

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
        print("Historial exportado correctamente")
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
        op = input("Seleccione una opcion: ").strip()

        if op == "1":
            if historial.inicio is None:
                print("No hay operaciones registradas")
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
                print("Busqueda vacia")
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
        print("Se creó el .dot pero NO se pudo generar el .png debido a que Graphviz no está en PATH")
        print("DOT:", ruta_dot)
        return

    comando = f'dot -Tpng "{ruta_dot}" -o "{ruta_png}"'
    resultado = os.system(comando)

    if resultado == 0:
        print("Reporte generado correctamente:")
        print("DOT:", ruta_dot)
        print("PNG:", ruta_png)
    else:
        print("Se creó el .dot pero NO se pudo generar el .png")
        print("Comando:", comando)


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

        cpu_total = getattr(dc, "cpu total", 0)
        ram_total = getattr(dc, "ram total", 0)
        alm_total = getattr(dc, "almacenamiento total", 0)

        cpu_usado = getattr(dc, "cpu usado", 0)
        ram_usado = getattr(dc, "ram usado", 0)
        alm_usado = getattr(dc, "almacenamiento usado", 0)

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
        dot += 'label="Cola de Solicitudes por Prioridad";\n'
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
        print("No existe un centro con ese id")
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
        print("VM no encontrada")
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
    dot = _dot_header("Reporte: Cola de Solicitudes por prioridad")

    if cola_solicitudes is None or cola_solicitudes.inicio is None:
        dot += 'X [shape=box, label="La cola está vacía o no existe"];\n'
        dot += _dot_footer()
        _guardar_dot_y_png(dot, "reporte_4_cola_solicitudes")
        print("La cola está vacía o no existe")
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
        print("2. Reporte de VMs por Centro por ID")
        print("3. Reporte de Contenedores por VM por ID")
        print("4. Reporte de Cola de Solicitudes por prioridad")
        print("5. Generar TODOS")
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
            print("Opcion invalida")

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

        cpu_total = int(getattr(dc, "cpu total", 0) or 0)
        ram_total = int(getattr(dc, "ram total", 0) or 0)

        cpu_usado = int(getattr(dc, "cpu usado", 0) or 0)
        ram_usado = int(getattr(dc, "ram usado", 0) or 0)

        cpu_disp = cpu_total - cpu_usado
        ram_disp = ram_total - ram_usado
        if cpu_disp < 0:
            cpu_disp = 0
        if ram_disp < 0:
            ram_disp = 0
        ET.SubElement(recursos, "cpu Total").text = str(cpu_total)
        ET.SubElement(recursos, "cpu Disponible").text = str(cpu_disp)
        ET.SubElement(recursos, "cpu Utilizacion").text = _porcentaje(cpu_usado, cpu_total)
        ET.SubElement(recursos, "ram Total").text = str(ram_total)
        ET.SubElement(recursos, "ram Disponible").text = str(ram_disp)
        ET.SubElement(recursos, "ram Utilizacion").text = _porcentaje(ram_usado, ram_total)
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
        print("XML de salida generado correctamente")
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

    historial = ListaSimple()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML: ")
            parser = ParserXML()

            if parser.cargar_archivo_xml(ruta):
                print("\nCargando archivo...")
                lista_data_centers = ListaSimple()
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

                cola = ColaPrioridad()
                nodo_sol = parser.solicitudes.inicio
                while nodo_sol is not None:
                    s = nodo_sol.dato
                    cola.agregar_solicitud(s)
                    nodo_sol = nodo_sol.siguiente
                procesador = ProcesadorSolicitudes(lista_data_centers)
                procesador.asignar_cola(cola)
                
                datos_cargados = True
                print("Datos cargados correctamente.\n")
                registrar_operacion(historial, "CARGA_XML", f"Se cargó el archivo: {ruta}")
                print("\n=== Ejecutando Instrucciones ===")
                nodo_inst = parser.instrucciones.inicio
                while nodo_inst is not None:
                    inst = nodo_inst.dato
                    tipo = getattr(inst, "tipo", "")

                    if tipo == "crearVM":
                        print("VM creada exitosamente")
                        registrar_operacion(historial, "INSTRUCCION", "crearVM ejecutada")

                    elif tipo == "migrarVM":
                        print("VM migrada exitosamente")
                        registrar_operacion(historial, "INSTRUCCION", "migrarVM ejecutada")

                    elif tipo == "procesarSolicitudes":
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
                print("No se pudo cargar el archivo")

        elif opcion == "2":
            if not datos_cargados:
                print("Primero cargue un archivo XML")
                continue

            while True:
                print("\n=== GESTIÓN DE CENTROS DE DATOS ===")
                print("1. Listar todos los centros")
                print("2. Buscar centro por id")
                print("3. Ver centro con más recursos")
                print("4. Volver al menu principal")
                sub_opcion = input("Seleccione una opcion:")

                if sub_opcion == "1":
                    print("\n Centro de datos registrados")
                    actual = lista_data_centers.inicio
                    contador = 1
                    while actual is not None:
                        dc = actual.dato
                        print(f"\n{contador}. Centro: {dc.nombre} ({dc.id})")
                        print("Ubicación:", dc.ubicacion)
                        print("RAM disponible: ", dc.ram_total - dc.ram_usado)
                        print("CPU disponible:", dc.cpu_total - dc.cpu_usado)
                        print("Almacenamiente disponible: ", dc.alm_total - dc.alm_usado)
                        print("VMs activas:", dc.maquinas_virtuales.contar())

                        actual = actual.siguiente
                        contador += 1

                elif sub_opcion == "2":
                    buscado = input("Ingrese el id del centro (ej: DC001): ")
                    actual = lista_data_centers.inicio
                    encontrado = False
                    while actual is not None:
                        dc = actual.dato
                        if dc.id == buscado:
                            print("\nCentro encontrado:")
                            print("ID:", dc.id)
                            print("Nombre:", dc.nombre)
                            print("Ubicación:", dc.ubicacion)
                            print("   CPU disponible:", dc.cpu_total - dc.cpu_usado)
                            print("RAM disponible:", dc.ram_total - dc.ram_usado)
                            print("Almacenamiento disponible:", dc.alm_total - dc.alm_usado)
                            print("VMs activas:", dc.maquinas_virtuales.contar())
                            encontrado = True
                            break
                        actual = actual.siguiente
                    if not encontrado:
                        print("No existe centro con ese id")

                elif sub_opcion == "3":
                    actual = lista_data_centers.inicio
                    if actual is None:
                        print("No hay centros registrados")
                        continue

                    mejor = actual.dato
                    actual = actual.siguiente

                    while actual is not None:
                        cpu_actual = actual.dato.cpu_total - actual.dato.cpu_usado
                        cpu_mejor = mejor.cpu_total - mejor.cpu_usado

                        if cpu_actual > cpu_mejor:
                            mejor = actual.dato
                        actual = actual.siguiente

                    print("\nCentro con más recursos disponibles:")
                    print("Id:", mejor.id)
                    print("Nombre:", mejor.nombre)
                    print("Ubicación:", mejor.ubicacion)
                    print("CPU disponible:", mejor.cpu_total - mejor.cpu_usado)
                    print("RAM disponible:", mejor.ram_total - mejor.ram_usado)
                    print("Almacenamiento disponible:", mejor.alm_total - mejor.alm_usado)
                    print("VMs activas:", mejor.maquinas_virtuales.contar())

                elif sub_opcion == "4":
                    break
                else:
                    print("Opcion invalida")

        elif opcion == "3":
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML")
                continue

            while True:
                print("\n=== GESTIÓN DE MÁQUINAS VIRTUALES ===")
                print("1. Buscar VM por id")
                print("2. Listar VMs de un centro ")
                print("3. Migrar VM entre centros")
                print("4. Volver al menu principal")
                sub_opcion = input("Seleccione una opcion")

                if sub_opcion == "1":
                    buscada = input("Id de la VM a buscar: ")
                    encontrado = False

                    actual_dc = lista_data_centers.inicio
                    while actual_dc is not None:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato

                            if vm.id == buscada:
                                print("\n--- VM encontrada ---")
                                print("Id:", vm.id)
                                print("Sistema Operativo:", vm.sistema_operativo)
                                print("CPU:", vm.cpu)
                                print("RAM:", vm.ram)
                                print("Almacenamiento:", vm.almacenamiento)
                                print("Estado:", vm.estado)
                                print("Centro asignado:", dc.id)

                                print("Contenedores:")
                                if vm.contenedores.contar() == 0:
                                    print("No hay contenedores")
                                else:
                                    nodo_c = vm.contenedores.inicio
                                    while nodo_c is not None:
                                        cont = nodo_c.dato
                                        print(f"- {cont.id} | {cont.nombre} | {getattr(cont,'tipo',getattr(cont,'imagen',''))}")
                                        nodo_c = nodo_c.siguiente

                                encontrado = True
                                break

                            actual_vm = actual_vm.siguiente

                        if encontrado:
                            break

                        actual_dc = actual_dc.siguiente

                    if not encontrado:
                        print("No existe VM con ese id")

                elif sub_opcion == "2":
                    centro = input("Id del centro (ej. DC001): ")
                    encontrado = False
                    actual_dc = lista_data_centers.inicio
                    while actual_dc is not None:
                        dc = actual_dc.dato

                        if dc.id == centro:
                            encontrado = True
                            print(f"\n--- VMs en el centro {dc.id} ---")

                            if dc.maquinas_virtuales.contar() == 0:
                                print("No hay VMs en este centro")
                            else:
                                actual_vm = dc.maquinas_virtuales.inicio
                                contador = 1

                                while actual_vm is not None:
                                    vm = actual_vm.dato
                                    print(f"{contador}. VM: {vm.id}")
                                    print("   Sistema Operativo:", vm.sistema_operativo)
                                    print("   CPU:", vm.cpu)
                                    print("   RAM:", vm.ram)
                                    print("   Almacenamiento:", vm.almacenamiento)
                                    print("   Estado:", vm.estado)
                                    print("   Contenedores:", vm.contenedores.contar())
                                    contador += 1
                                    actual_vm = actual_vm.siguiente
                            break

                        actual_dc = actual_dc.siguiente

                    if not encontrado:
                        print("No existe un centro con ese id")

                elif sub_opcion == "3":
                    vm_id = input("ID de la VM a migrar: ")
                    destino_id = input("Centro destino: ")

                    centro_origen = None
                    centro_destino = None
                    vm_encontrada = None

                    actual = lista_data_centers.inicio
                    while actual is not None:
                        dc = actual.dato
                        if dc.id == destino_id:
                            centro_destino = dc
                            break
                        actual = actual.siguiente

                    if centro_destino is None:
                        print("Centro destino no existe")
                        continue

                    actual = lista_data_centers.inicio
                    while actual is not None and vm_encontrada is None:
                        dc = actual.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato
                            if vm.id == vm_id:
                                vm_encontrada = vm
                                centro_origen = dc
                                break
                            actual_vm = actual_vm.siguiente

                        actual = actual.siguiente

                    if vm_encontrada is None:
                        print("VM no encontrada")
                        continue

                    if centro_origen.id == centro_destino.id:
                        print("La VM ya se encuentra en el centro destino")
                        continue

                    cpu_disp = centro_destino.cpu_total - centro_destino.cpu_usado
                    ram_disp = centro_destino.ram_total - centro_destino.ram_usado
                    alm_disp = centro_destino.alm_total - centro_destino.alm_usado

                    if (cpu_disp < vm_encontrada.cpu or
                        ram_disp < vm_encontrada.ram or
                        alm_disp < vm_encontrada.almacenamiento):
                        print("Recursos insuficientes en el centro destino")
                        continue

                    centro_origen.eliminar_vm(vm_encontrada.id)

                    centro_origen.cpu_usado -= vm_encontrada.cpu
                    centro_origen.ram_usado -= vm_encontrada.ram
                    centro_origen.alm_usado -= vm_encontrada.almacenamiento

                    centro_destino.maquinas_virtuales.insertar_final(vm_encontrada)

                    centro_destino.cpu_usado += vm_encontrada.cpu
                    centro_destino.ram_usado += vm_encontrada.ram
                    centro_destino.alm_usado += vm_encontrada.almacenamiento

                    print(f"VM {vm_encontrada.id} migrada correctamente de {centro_origen.id} a {centro_destino.id}")

                elif sub_opcion == "4":
                    break
                else:
                    print("Opcion invalida")
        elif opcion == "4":
            if not datos_cargados:
                print("Primero cargue un archivo XML")
                continue

            while True:
                print("\n=== GESTIÓN DE CONTENEDORES ===")
                print("1. Listar contenedores de una VM")
                print("2. Desplegar contenedor en VM")
                print("3. Cambiar estado de contenedor")
                print("4. Eliminar contenedor")
                print("5. Volver al menu principal")

                sub_opcion = input("Seleccione una opcion: ")

                if sub_opcion == "1":
                    vm_id = input("Id de la VM: ")

                    vm_encontrada = None
                    actual_dc = lista_data_centers.inicio

                    while actual_dc is not None and vm_encontrada is None:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato
                            if vm.id == vm_id:
                                vm_encontrada = vm
                                break
                            actual_vm = actual_vm.siguiente

                        actual_dc = actual_dc.siguiente

                    if vm_encontrada is None:
                        print("VM no encontrada")
                        continue

                    print(f"\n--- CONTENEDORES EN VM {vm_encontrada.id} ---")

                    if vm_encontrada.contenedores.contar() == 0:
                        print("No hay contenedores en esta VM")
                    else:
                        actual_cont = vm_encontrada.contenedores.inicio
                        while actual_cont is not None:
                            print(actual_cont.dato)
                            actual_cont = actual_cont.siguiente

                elif sub_opcion == "2":
                    vm_id = input("Id de la VM destino: ")
                    cont_id = input("Id del contenedor: ")
                    nombre = input("Nombre del contenedor: ")
                    imagen = input("Imagen (ej: nginx:latest): ")

                    try:
                        cpu = int(input("CPU requerida: "))
                        ram = int(input("RAM requerida: "))
                    except:
                        print("CPU y RAM deben ser valores numericos")
                        continue

                    vm_encontrada = None
                    actual_dc = lista_data_centers.inicio

                    while actual_dc is not None and vm_encontrada is None:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato
                            if vm.id == vm_id:
                                vm_encontrada = vm
                                break
                            actual_vm = actual_vm.siguiente

                        actual_dc = actual_dc.siguiente

                    if vm_encontrada is None:
                        print("VM no encontrada")
                        continue

                    if cpu > vm_encontrada.cpu or ram > vm_encontrada.ram:
                        print("Falta de recursos en la VM")
                        continue

                    from src.models.contenedor import Contenedor
                    nuevo_contenedor = Contenedor(cont_id, nombre, imagen, cpu, ram)

                    vm_encontrada.cpu -= cpu
                    vm_encontrada.ram -= ram

                    vm_encontrada.contenedores.insertar_final(nuevo_contenedor)

                    print(f"Contenedor {cont_id} desplegado correctamente en la VM {vm_id}")

                elif sub_opcion == "3":
                    cont_id = input("Id del contenedor: ")

                    cont_encontrado = None

                    actual_dc = lista_data_centers.inicio
                    while actual_dc is not None and cont_encontrado is None:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None and cont_encontrado is None:
                            vm = actual_vm.dato
                            actual_cont = vm.contenedores.inicio

                            while actual_cont is not None:
                                cont = actual_cont.dato
                                if cont.id == cont_id:
                                    cont_encontrado = cont
                                    break
                                actual_cont = actual_cont.siguiente

                            actual_vm = actual_vm.siguiente
                        actual_dc = actual_dc.siguiente

                    if cont_encontrado is None:
                        print("Contenedor no encontrado.")
                        continue

                    print("\nEstado actual:", cont_encontrado.estado)
                    print("Estados disponibles:")
                    print("1. Activo")
                    print("2. Pausado")
                    print("3. Detenido")

                    opcion_estado = input("Seleccione nuevo estado: ")

                    if opcion_estado == "1":
                        cont_encontrado.estado = "Activo"
                    elif opcion_estado == "2":
                        cont_encontrado.estado = "Pausado"
                    elif opcion_estado == "3":
                        cont_encontrado.estado = "Detenido"
                    else:
                        print("Estado invalido.")
                        continue

                    print(f"Estado del contenedor {cont_encontrado.id} cambiado a {cont_encontrado.estado}.")

                elif sub_opcion == "4":
                    cont_id = input("ID del contenedor a eliminar: ")

                    eliminado = False

                    actual_dc = lista_data_centers.inicio
                    while actual_dc is not None and not eliminado:
                        dc = actual_dc.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None and not eliminado:
                            vm = actual_vm.dato

                            actual_cont = vm.contenedores.inicio
                            anterior = None

                            while actual_cont is not None:
                                cont = actual_cont.dato

                                if cont.id == cont_id:
                                    vm.cpu += cont.cpu
                                    vm.ram += cont.ram

                                    if anterior is None:
                                        vm.contenedores.inicio = actual_cont.siguiente
                                    else:
                                        anterior.siguiente = actual_cont.siguiente

                                    eliminado = True
                                    print(f"Contenedor {cont_id} eliminado correctamente")
                                    break

                                anterior = actual_cont
                                actual_cont = actual_cont.siguiente

                            actual_vm = actual_vm.siguiente
                        actual_dc = actual_dc.siguiente

                    if not eliminado:
                        print("Contenedor no encontrado")

                elif sub_opcion == "5":
                    break
                else:
                    print("Opcion aun en desarrollo")

        elif opcion == "5":
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue

            while True:
                print("\n=== GESTIÓN DE SOLICITUDES ===")
                print("1. Agregar nueva solicitud")
                print("2. Procesar solicitud de mayor prioridad")
                print("3. Procesar N solicitudes")
                print("4. Ver cola de solicitudes")
                print("5. Volver al menú principal")

                sub_opcion = input("Seleccione una opcion: ")

                if sub_opcion == "1":
                    sol_id = input("ID de la solicitud: ")
                    cliente = input("Cliente: ")
                    tipo = input("Tipo (Deploy / Backup): ")

                    try:
                        prioridad = int(input("Prioridad (1-10): "))
                    except:
                        print("La prioridad debe ser un numero")
                        continue

                    if prioridad < 1 or prioridad > 10:
                        print("La prioridad debe estar entre 1 y 10")
                        continue

                    descripcion = f"Cliente: {cliente}"

                    nueva_solicitud = Solicitud(sol_id, tipo, prioridad, descripcion)
                    procesador.cola_solicitudes.agregar_solicitud(nueva_solicitud)

                    print(f"Solicitud {sol_id} agregada correctamente a la cola")

                elif sub_opcion == "2":
                    if procesador.cola_solicitudes.esta_vacia():
                        print("No hay solicitudes en la cola")
                        continue

                    solicitud = procesador.cola_solicitudes.sacar_siguiente()

                    print("Procesando solicitud:")
                    print(solicitud)

                    try:
                        if solicitud.tipo == "Deploy":
                            procesador.procesar_deploy(solicitud)
                        elif solicitud.tipo == "Backup":
                            procesador.procesar_backup(solicitud)
                        else:
                            print("Tipo de solicitud desconocido.")
                            continue

                        print("Solicitud procesada correctamente")
                    except Exception as e:
                        print("Error al procesar la solicitud")

                elif sub_opcion == "3":
                    try:
                        cantidad = int(input("Cantidad de solicitudes a procesar: "))
                    except:
                        print("Debe ingresar un numero")
                        continue

                    procesadas, completadas, fallidas = procesador.procesar_solicitudes(cantidad)

                    print("\nResumen del procesamiento:")
                    print("Procesadas:", procesadas)
                    print("Completadas:", completadas)
                    print("Fallidas:", fallidas)

                elif sub_opcion == "4":
                    if procesador.cola_solicitudes.esta_vacia():
                        print("No hay solicitudes en la cola")
                    else:
                        procesador.cola_solicitudes.mostrar_cola()

                elif sub_opcion == "5":
                    break
                else:
                    print("Opción aun en desarrollo")
        elif opcion == "6":
            if not datos_cargados or lista_data_centers is None:
                print("Primero cargue un archivo XML")
            else:
                cola_real = None
                if procesador is not None:
                    cola_real = procesador.cola_solicitudes

                generar_reportes_graphviz_menu(lista_data_centers, cola_real)
                registrar_operacion(historial, "REPORTES_GRAPHVIZ", "Se generaron los reportes")
        elif opcion == "7":
            if not datos_cargados or lista_data_centers is None:
                print("Primero cargue un archivo XML")
            else:
                ok = generar_xml_salida_pdf(lista_data_centers)
                if ok:
                    registrar_operacion(historial, "XML_SALIDA", "Se genero el XML de salida")
                else:
                    registrar_operacion(historial, "XML_SALIDA", "Fallo la generación del XML de salida")
                    
        elif opcion == "8":
            menu_historial(historial)

        elif opcion == "9":
            registrar_operacion(historial, "Salir", "El usuario salio del sistema")
            print("Saliendo del sistema...")
            break

        else:
            print("Opcion invalida. Intente de nuevo.")


if __name__ == "__main__":
    main()
