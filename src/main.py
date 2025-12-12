# main.py
# CloudSync Manager - Sistema de Nube
# Menú principal según especificación del proyecto

from src.parser.parser import ParserXML


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
                datos_cargados = True
                print("Datos cargados correctamente.")
                # puedes dejar estos prints o quitarlos
                print("Centros:", parser.datacenters)
                print("VMs:", parser.maquinas_virtuales)
                print("Contenedores:", parser.contenedores)
                print("Solicitudes:", parser.solicitudes)
                print("Instrucciones:", parser.instrucciones)
            else:
                print("No se pudo cargar el archivo.")

        elif opcion == "2":
            # Gestión de Centros de Datos (versión simple)
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML (opción 1).")
            else:
                print("\n--- CENTROS DE DATOS ---")
                if len(parser.datacenters) == 0:
                    print("No hay centros de datos cargados.")
                else:
                    for centro in parser.datacenters:
                        # cada centro es un diccionario {"id": ..., "nombre": ...}
                        print("ID:", centro.get("id", ""),
                              "| Nombre:", centro.get("nombre", ""))

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
