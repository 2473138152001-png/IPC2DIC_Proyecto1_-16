# main.py
# CloudSync Manager - Sistema de Nube
# Menú principal según especificación del proyecto
from src.core.procesador import ProcesadorSolicitudes
from src.data_structures.cola_prioridad import ColaPrioridad
from src.models.solicitud import Solicitud
from src.parser.parser import ParserXML
from src.models.data_center import DataCenter
from src.data_structures.lista_simple import ListaSimple
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


def main():
    parser = None          # aquí voy a guardar el parser
    datos_cargados = False # para saber si ya se cargó un XML


    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML: ")

            parser = ParserXML()

            if parser.cargar_archivo_xml(ruta):
                
                print("\nCargando archivo...")
                lista_data_centers = ListaSimple()
                for dc in parser.datacenters:
                    nuevo_dc = DataCenter(
                        dc["id"],
                        dc["nombre"],
                        dc ["Ubicación"]
                    )
                    # asigno capacidades totales
                    nuevo_dc.cpu_total = dc["cpu_total"]
                    nuevo_dc.ram_total = dc["ram_total"]
                    nuevo_dc.alm_total = dc["alm_total"]

                    # inicializo usados
                    nuevo_dc.cpu_usado = 0
                    nuevo_dc.ram_usado = 0
                    nuevo_dc.alm_usado = 0
                    lista_data_centers.insertar_final(nuevo_dc)
                cola = ColaPrioridad()

                for sol in parser.solicitudes:
                    solicitud = Solicitud(
                        sol["id"],
                        sol["tipo"],
                        int(sol["prioridad"]),
                        "Solicitud cargada desde XML"
                    )
                    cola.agregar_solicitud(solicitud)

        
                procesador = ProcesadorSolicitudes(lista_data_centers)
                procesador.asignar_cola(cola)

                datos_cargados = True
                print("Datos cargados correctamente.")
                # Centros de datos
                for dc in parser.datacenters:
                    print(f"Centro {dc['id']} cargado")

                # Máquinas virtuales y contenedores
                
                for vm in parser.maquinas_virtuales:
                    for nodo_dc in lista_data_centers.recorrer():  # si no tienes recorrer, usa while
                        if nodo_dc.id == vm["centro"]:
                            nodo_dc.cpu_usado += vm["cpu"]
                            nodo_dc.ram_usado += vm["ram"]
                            nodo_dc.alm_usado += vm["almacenamiento"]


                for cont in parser.contenedores:
                    if cont["vm"] == vm["id"]:
                        print(f"   Contenedor {cont['id']} agregado a VM {vm['id']}")

                # Solicitudes
                for sol in parser.solicitudes:
                    print(f"✓ Solicitud {sol['id']} cargada")

                
                print("\n=== Ejecutando Instrucciones ===")
                for inst in parser.instrucciones:
                    if inst["tipo"] == "crearVM":
                        print("VM creada exitosamente")
                    elif inst["tipo"] == "migrarVM":
                        print("VM migrada exitosamente")
                    elif inst["tipo"] == "procesarSolicitudes":
                        cantidad = len(parser.solicitudes)
                        procesadas, completadas, fallidas = procesador.procesar_solicitudes(cantidad)
                        print(f" Procesadas: {procesadas}, Completadas: {completadas}, Fallidas: {fallidas}")



                print("\n Archivo XML cargado exitosamente\n")
            else:
                print("No se pudo cargar el archivo.")


        elif opcion == "2":
            
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue
            while True:
                print("\n=== GESTIÓN DE CENTROS DE DATOS ===")
                print("1. Listar todos los centros")
                print("2. Buscar centro por ID")
                print("3. Ver centro con más recursos")
                print("4. Volver al menú principal")
                sub_opcion= input("Seleccione una opcion:")
                if sub_opcion == "1":
                    print("\n Centro de datos registrados")
                    actual = lista_data_centers.inicio
                    contador= 1
                    while actual is not None:
                        dc= actual.dato
                        print(f"\n{contador}. Centro: {dc.nombre} ({dc.id})")
                        print("   Ubicación:", dc.ubicacion)
                        print("   CPU disponible:", dc.cpu_disponible)
                        print("   VMs activas:", dc.maquinas_virtuales.contar())
                    
                        actual=actual.siguiente
                        contador+=1
                    
                elif sub_opcion =="2":
                    buscado= input("Ingrese el id del centro (ej: DC001): ")
                    actual = lista_data_centers.inicio
                    encontrado = False 
                    while actual is not None:
                        dc=actual.dato
                        if dc.id== buscado:
                            print("\nCentro encontrado:")
                            print("ID:", dc.id)
                            print("Nombre:", dc.nombre)
                            print("Ubicación:", dc.ubicacion)
                            print("CPU disponible:", dc.cpu_disponible)
                            print("VMs activas:", dc.maquinas_virtuales.contar())
                            encontrado = True
                            break
                        actual = actual.siguiente
                    if not encontrado:
                        print("No existe centro con ese id")
                            
                elif sub_opcion == "3":
                    

                    actual = lista_data_centers.inicio
                    if actual is None:
                        print("No hay centros registrados.")
                        continue

                    mejor = actual.dato
                    actual = actual.siguiente

                    while actual is not None:
                        if actual.dato.cpu_disponible > mejor.cpu_disponible:
                            mejor = actual.dato
                        actual = actual.siguiente

                    print("\nCentro con más recursos disponibles:")
                    print("ID:", mejor.id)
                    print("Nombre:", mejor.nombre)
                    print("Ubicación:", mejor.ubicacion)
                    print("CPU disponible:", mejor.cpu_disponible)
                    print("VMs activas:", mejor.maquinas_virtuales.contar())

                elif sub_opcion =="4":
                    break
                else:
                    print("Opcion invalida")
        elif opcion == "3":
            # Gestión de Máquinas Virtuales (mostrar lista simple)
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML (opción 1).")
            else:
                print("\n--- MÁQUINAS VIRTUALES ---")
                if len(parser.maquinas_virtuales) == 0:
                    print("No hay máquinas virtuales cargadas.")
                else:
                    for vm in parser.maquinas_virtuales:
                        # vm es {"id": ..., "centro": ...}
                        print("ID VM:", vm.get("id", ""),
                              "| Centro asignado:", vm.get("centro", ""))

        elif opcion == "4":
            # Gestión de Contenedores (solo listar lo que hay)
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML (opción 1).")
            else:
                print("\n--- CONTENEDORES ---")
                if len(parser.contenedores) == 0:
                    print("No hay contenedores cargados.")
                else:
                    for cont in parser.contenedores:
                        # cont es {"id": ..., "vm": ...}
                        print("ID contenedor:", cont.get("id", ""),
                              "| Pertenece a VM:", cont.get("vm", ""))

        elif opcion == "5":
            # Gestión de Solicitudes (solo mostrar por ahora)
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML (opción 1).")
            else:
                print("\n--- SOLICITUDES ---")
                if len(parser.solicitudes) == 0:
                    print("No hay solicitudes cargadas.")
                else:
                    for sol in parser.solicitudes:
                        print("ID:", sol.get("id", ""),
                              "| Cliente:", sol.get("cliente", ""),
                              "| Tipo:", sol.get("tipo", ""),
                              "| Prioridad:", sol.get("prioridad", ""))

                print("\n--- INSTRUCCIONES ---")
                if len(parser.instrucciones) == 0:
                    print("No hay instrucciones cargadas.")
                else:
                    for inst in parser.instrucciones:
                        print("Tipo de instrucción:", inst.get("tipo", ""))

        elif opcion == "6":
            print("Reportes Graphviz en desarrollo.")

        elif opcion == "7":
            print("Generación de XML de salida en desarrollo.")

        elif opcion == "8":
            print("Historial de operaciones en desarrollo.")

        elif opcion == "9":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción inválida. Intente de nuevo.")


if __name__ == "__main__":
    main()
