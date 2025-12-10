# Este archivo es el menú principal del proyecto.
# Desde aquí se llama a todo lo demás.


from src.parser.parser import ParserXML
from src.core.procesador import ProcesadorSolicitudes
from src.data_structures.cola_prioridad import ColaPrioridad


def mostrar_menu():
    print("\n====== MENÚ PRINCIPAL ======")
    print("1. Cargar archivo de DataCenters")
    print("2. Cargar archivo de Solicitudes")
    print("3. Cargar archivo de Instrucciones")
    print("4. Salir")
    print("============================")


def main():
    parser = None
    procesador = None
    cola = ColaPrioridad()

    lista_data_centers = None

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ruta = input("Ingrese la ruta del archivo XML de DataCenters: ")

            parser = ParserXML()
            parser.cargar_archivo(ruta)
            lista_data_centers = parser.obtener_data_centers()

            procesador = ProcesadorSolicitudes(lista_data_centers)
            procesador.asignar_cola(cola)

            print("DataCenters cargados correctamente.")

        elif opcion == "2":
            if procesador is None:
                print("Primero debe cargar los DataCenters.")
                continue

            ruta = input("Ingrese la ruta del archivo XML de Solicitudes: ")
            procesador.cargar_solicitudes_xml(ruta)

        elif opcion == "3":
            if procesador is None:
                print("Primero debe cargar los DataCenters.")
                continue

            ruta = input("Ingrese la ruta del archivo XML de Instrucciones: ")
            procesador.cargar_solicitudes(ruta)

        elif opcion == "4":
            print("Saliendo del programa...")
            break

        else:
            print("Opción inválida. Intente de nuevo.")


# Punto de entrada del programa
if __name__ == "__main__":
    main()
