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
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML: ")

            parser = ParserXML()

            if parser.cargar_archivo_xml(ruta):
                print("Datos cargados correctamente.")
                print("Centros:", parser.datacenters)
                print("VMs:", parser.maquinas_virtuales)
                print("Solicitudes:", parser.solicitudes)
                print("Instrucciones:", parser.instrucciones)
            else:
                print("No se pudo cargar el archivo.")


        elif opcion == "2":
            print("Gestión de Centros de Datos en desarrollo.")

        elif opcion == "3":
            print("Gestión de Máquinas Virtuales en desarrollo.")

        elif opcion == "4":
            print("Gestión de Contenedores en desarrollo.")

        elif opcion == "5":
            print("Gestión de Solicitudes en desarrollo.")

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
