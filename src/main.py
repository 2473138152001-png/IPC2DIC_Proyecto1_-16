# main.py
# CloudSync Manager - Sistema de Nube
# Menú principal según especificación del proyecto
from src.core.procesador import ProcesadorSolicitudes
from src.data_structures.cola_prioridad import ColaPrioridad
from src.models.solicitud import Solicitud
from src.parser.parser import ParserXML
from src.models.data_center import DataCenter
from src.data_structures.lista_simple import ListaSimple
from src.models.maquina_virtual import MaquinaVirtual
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
                        dc["ubicacion"]
                    )

                    # capacidades
                    nuevo_dc.cpu_total = dc["cpu_total"]
                    nuevo_dc.ram_total = dc["ram_total"]
                    nuevo_dc.alm_total = dc["alm_total"]

                    # usados
                    nuevo_dc.cpu_usado = 0
                    nuevo_dc.ram_usado = 0
                    nuevo_dc.alm_usado = 0

                    lista_data_centers.insertar_final(nuevo_dc)


                from src.models.maquina_virtual import MaquinaVirtual

                for vm_data in parser.maquinas_virtuales:
                    actual = lista_data_centers.inicio

                    while actual is not None:
                        dc = actual.dato

                        if dc.id == vm_data["centro"]:
                            nueva_vm = MaquinaVirtual(
                                vm_data["id"],
                                vm_data["id"],  # nombre simple
                                vm_data["so"]
                            )

                            nueva_vm.cpu = vm_data["cpu"]
                            nueva_vm.ram = vm_data["ram"]
                            nueva_vm.almacenamiento = vm_data["almacenamiento"]
                            nueva_vm.estado = vm_data["estado"]

                            dc.maquinas_virtuales.insertar_final(nueva_vm)

                            # actualizar recursos del DC
                            dc.cpu_usado += nueva_vm.cpu
                            dc.ram_usado += nueva_vm.ram
                            dc.alm_usado += nueva_vm.almacenamiento
                            break

                        actual = actual.siguiente


                from src.models.contenedor import Contenedor

                for cont_data in parser.contenedores:
                    actual = lista_data_centers.inicio

                    while actual is not None:
                        dc = actual.dato
                        actual_vm = dc.maquinas_virtuales.inicio

                        while actual_vm is not None:
                            vm = actual_vm.dato

                            if vm.id == cont_data["vm"]:
                                nuevo_cont = Contenedor(
                                    cont_data["id"],
                                    cont_data["nombre"],
                                    cont_data["imagen"]
                                )
                                vm.contenedores.insertar_final(nuevo_cont)
                                break

                            actual_vm = actual_vm.siguiente

                        actual = actual.siguiente

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
                print("Datos cargados correctamente.\n")


                for dc in parser.datacenters:
                    print(f"Centro {dc['id']} cargado")

                for vm in parser.maquinas_virtuales:
                    print(f"VM {vm['id']} cargada en {vm['centro']}")

                for cont in parser.contenedores:
                    print(f"   Contenedor {cont['id']} agregado a VM {cont['vm']}")

                for sol in parser.solicitudes:
                    print(f" Solicitud {sol['id']} cargada")

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
                print("2. Buscar centro por id")
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
                        cpu_disp = dc.cpu_total - dc.cpu_usado
                        print("RAM disponible: ", dc.ram_total - dc.ram_usado )
                        print("CPU disponible:",  dc.cpu_total - dc.cpu_usado)
                        print("Almacenamiente disponible: ",dc.alm_total - dc.alm_usado)
                        print("VMs activas:", dc.maquinas_virtuales.contar())
                    
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
                            cpu_disp = dc.cpu_total - dc.cpu_usado
                            print("   CPU disponible:",  dc.cpu_total - dc.cpu_usado)
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
                        print("No hay centros registrados.")
                        continue

                    mejor = actual.dato
                    actual = actual.siguiente

                    while actual is not None:
                        cpu_actual= actual.dato.cpu_total - actual.dato.cpu_usado
                        cpu_mejor= mejor.cpu_total - mejor.cpu_usado
                        
                        if cpu_actual > cpu_mejor:
                            mejor = actual.dato
                        actual = actual.siguiente

                    print("\nCentro con más recursos disponibles:")
                    print("Id:", mejor.id)
                    print("Nombre:", mejor.nombre)
                    print("Ubicación:", mejor.ubicacion)
                    print("CPU disponible:", dc.cpu_total - dc.cpu_usado)
                    print("RAM disponible:", dc.ram_total - dc.ram_usado)
                    print("Almacenamiento disponible:", dc.alm_total - dc.alm_usado)
                    print("VMs activas:", mejor.maquinas_virtuales.contar())

                elif sub_opcion =="4":
                    break
                else:
                    print("Opcion invalida")
        elif opcion == "3":
            # Gestión de Máquinas Virtuales (mostrar lista simple)
            if not datos_cargados or parser is None:
                print("Primero cargue un archivo XML (opción 1).")
                continue
            
            while True: 
                print("\n=== GESTIÓN DE MÁQUINAS VIRTUALES ===")
                print("1. Buscar VM por id")
                print("2. Listar VMs de un centro ")
                print("3. Migrar VM entre centros")
                print("4. Volver al menu principal")
                sub_opcion= input("Seleccione una opcion")
                if sub_opcion =="1":
                    buscada= input("Id de la VM a buscar: ")
                    encontrado= False
                    
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
                                        print(f"- {cont.id} | {cont.nombre} | {cont.tipo}")
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
                                print("No hay VMs en este centro.")
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
                        print("No existe un centro con ese id.")
                        
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
                        print("Centro destino no existe.")
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
                        print("VM no encontrada.")
                        continue

                    if centro_origen.id == centro_destino.id:
                        print("La VM ya se encuentra en el centro destino.")
                        continue

                   
                    cpu_disp = centro_destino.cpu_total - centro_destino.cpu_usado
                    ram_disp = centro_destino.ram_total - centro_destino.ram_usado
                    alm_disp = centro_destino.alm_total - centro_destino.alm_usado

                    if (cpu_disp < vm_encontrada.cpu or
                        ram_disp < vm_encontrada.ram or
                        alm_disp < vm_encontrada.almacenamiento):
                        print("Recursos insuficientes en el centro destino.")
                        continue

                   

                  
                    centro_origen.eliminar_vm(vm_encontrada.id)

                    
                    centro_origen.cpu_usado -= vm_encontrada.cpu
                    centro_origen.ram_usado -= vm_encontrada.ram
                    centro_origen.alm_usado -= vm_encontrada.almacenamiento

                    
                    centro_destino.maquinas_virtuales.insertar_final(vm_encontrada)

                    centro_destino.cpu_usado += vm_encontrada.cpu
                    centro_destino.ram_usado += vm_encontrada.ram
                    centro_destino.alm_usado += vm_encontrada.almacenamiento

                    print(f"VM {vm_encontrada.id} migrada correctamente de {centro_origen.id} a {centro_destino.id}.")

                    

                elif sub_opcion == "4":
                    break

                else:
                    print("Opcion invalida.")
                                
        elif opcion == "4":
            
            if not datos_cargados:
                print("Primero cargue un archivo XML.")
                continue

            while True:
                print("\n=== GESTIÓN DE CONTENEDORES ===")
                print("1. Listar contenedores de una VM")
                print("2. Desplegar contenedor en VM")
                print("3. Cambiar estado de contenedor")
                print("4. Eliminar contenedor")
                print("5. Volver al menu principal")

                sub_opcion = input("Seleccione una opción: ")

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
                        print("VM no encontrada.")
                        continue

                    print(f"\n--- CONTENEDORES EN VM {vm_encontrada.id} ---")

                    if vm_encontrada.contenedores.contar() == 0:
                        print("No hay contenedores en esta VM.")
                    else:
                        actual_cont = vm_encontrada.contenedores.inicio
                        while actual_cont is not None:
                            print(actual_cont.dato)
                            actual_cont = actual_cont.siguiente
                            
            
                elif sub_opcion == "2":
                    vm_id = input("d de la VM destino: ")
                    cont_id = input("Id del contenedor: ")
                    nombre = input("Nombre del contenedor: ")
                    imagen = input("Imagen (ej: nginx:latest): ")

                    try:
                        cpu = int(input("CPU requerida: "))
                        ram = int(input("RAM requerida: "))
                    except:
                        print("CPU y RAM deben ser valores numéricos.")
                        continue

                    # Buscar VM
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
                        print("VM no encontrada.")
                        continue

                    # Validar recursos de la VM
                    if cpu > vm_encontrada.cpu or ram > vm_encontrada.ram:
                        print("Falta de recursos en la VM.")
                        continue

                    # Crear contenedor
                    from src.models.contenedor import Contenedor
                    nuevo_contenedor = Contenedor(cont_id, nombre, imagen, cpu, ram)

                    # Descontar recursos de la VM
                    vm_encontrada.cpu -= cpu
                    vm_encontrada.ram -= ram

                    # Agregar contenedor
                    vm_encontrada.contenedores.insertar_final(nuevo_contenedor)

                    print(f"Contenedor {cont_id} desplegado correctamente en la VM {vm_id}.")
                    
                    
                
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
                                    # Devolver recursos a la VM
                                    vm.cpu += cont.cpu
                                    vm.ram += cont.ram

                                    # Eliminar contenedor de la lista
                                    if anterior is None:
                                        vm.contenedores.inicio = actual_cont.siguiente
                                    else:
                                        anterior.siguiente = actual_cont.siguiente

                                    eliminado = True
                                    print(f"Contenedor {cont_id} eliminado correctamente.")
                                    break

                                anterior = actual_cont
                                actual_cont = actual_cont.siguiente

                            actual_vm = actual_vm.siguiente
                        actual_dc = actual_dc.siguiente

                    if not eliminado:
                        print("Contenedor no encontrado.")


                elif sub_opcion == "5":
                    break

                else:
                    print("Opcion aun en desarrollo.")


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

                sub_opcion = input("Seleccione una opción: ")
                if sub_opcion =="1":
                    sol_id = input("ID de la solicitud: ")
                    cliente = input("Cliente: ")
                    tipo = input("Tipo (Deploy / Backup): ")

                    try:
                        prioridad = int(input("Prioridad (1-10): "))
                    except:
                        print("La prioridad debe ser un número.")
                        continue

                    if prioridad < 1 or prioridad > 10:
                        print("La prioridad debe estar entre 1 y 10.")
                        continue

                    descripcion = f"Cliente: {cliente}"

                    nueva_solicitud = Solicitud(sol_id, tipo, prioridad, descripcion)
                    procesador.cola_solicitudes.agregar_solicitud(nueva_solicitud)

                    print(f"Solicitud {sol_id} agregada correctamente a la cola.")
                    
                    
                elif sub_opcion == "2":
                    if procesador.cola_solicitudes.esta_vacia():
                        print("No hay solicitudes en la cola.")
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

                        print("Solicitud procesada correctamente.")

                    except Exception as e:
                        print("Error al procesar la solicitud.")
                        
                    
                elif sub_opcion == "3":
                    try:
                        cantidad = int(input("Cantidad de solicitudes a procesar: "))
                    except:
                        print("Debe ingresar un número.")
                        continue

                    procesadas, completadas, fallidas = procesador.procesar_solicitudes(cantidad)

                    print("\nResumen del procesamiento:")
                    print("Procesadas:", procesadas)
                    print("Completadas:", completadas)
                    print("Fallidas:", fallidas)


                                    
                elif sub_opcion == "4":
                    if procesador.cola_solicitudes.esta_vacia():
                        print("No hay solicitudes en la cola.")
                    else:
                        procesador.cola_solicitudes.mostrar_cola()

                elif sub_opcion == "5":
                    break

                else:
                    print("Opción aún en desarrollo.")


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
