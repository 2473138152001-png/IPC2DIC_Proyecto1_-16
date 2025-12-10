# Este archivo es para leer el XML.
# La idea es que al final me devuelva una lista (simple) con todos los DataCenters cargados.

import xml.etree.ElementTree as ET

from src.models.data_center import DataCenter
from src.models.maquina_virtual import MaquinaVirtual
from src.models.contenedor import Contenedor
from src.data_structures.lista_simple import ListaSimple


class ParserXML:

    def __init__(self):
        # Aquí voy a guardar los data centers que salgan del XML
        self.lista_data_centers = ListaSimple()

    def cargar_archivo(self, ruta):
        # Intento abrir el archivo. Si falla, solo aviso.
        try:
            arbol = ET.parse(ruta)
            raiz = arbol.getroot()
        except:
            print("No se pudo leer el archivo XML. Revise la ruta o el formato.")
            return

        # Aquí empiezo a recorrer los DataCenter uno por uno
        for dc in raiz.findall("DataCenter"):
            id_dc = dc.get("id")

            # Los siguientes nodos los leo uno por uno
            nodo_nombre = dc.find("Nombre")
            if nodo_nombre != None:
                nombre_dc = nodo_nombre.text
            else:
                nombre_dc = ""

            nodo_ubic = dc.find("Ubicacion")
            if nodo_ubic != None:
                ubicacion_dc = nodo_ubic.text
            else:
                ubicacion_dc = ""

            # Creo el objeto
            data_center = DataCenter(id_dc, nombre_dc, ubicacion_dc)

            # Ahora voy con las máquinas virtuales
            seccion_maquinas = dc.find("MaquinasVirtuales")

            if seccion_maquinas != None:
                # Recorro cada VM
                for vm in seccion_maquinas.findall("VM"):
                    id_vm = vm.get("id")

                    nodo_nombre_vm = vm.find("Nombre")
                    if nodo_nombre_vm != None:
                        nombre_vm = nodo_nombre_vm.text
                    else:
                        nombre_vm = ""

                    nodo_so_vm = vm.find("SO")
                    if nodo_so_vm != None:
                        so_vm = nodo_so_vm.text
                    else:
                        so_vm = ""

                    # Creo la máquina virtual
                    maquina = MaquinaVirtual(id_vm, nombre_vm, so_vm)

                    # Ahora los contenedores
                    seccion_conts = vm.find("Contenedores")

                    if seccion_conts != None:
                        for cont in seccion_conts.findall("Contenedor"):
                            id_cont = cont.get("id")

                            nodo_nombre_cont = cont.find("Nombre")
                            if nodo_nombre_cont != None:
                                nombre_cont = nodo_nombre_cont.text
                            else:
                                nombre_cont = ""

                            nodo_tipo_cont = cont.find("Tipo")
                            if nodo_tipo_cont != None:
                                tipo_cont = nodo_tipo_cont.text
                            else:
                                tipo_cont = ""

                            # Creo el contenedor y lo agrego
                            cont_obj = Contenedor(id_cont, nombre_cont, tipo_cont)
                            maquina.agregar_contenedor(cont_obj)

                    # Agrego la máquina al Data Center
                    data_center.agregar_vm(maquina)

            # Al final meto el Data Center completo en la lista
            self.lista_data_centers.agregar(data_center)

        print("Archivo XML cargado exitosamente (creo).")

    def obtener_data_centers(self):
        # Solo regreso la lista que ya llené
        return self.lista_data_centers