import xml.etree.ElementTree as ET
from src.data_structures.lista_simple import ListaSimple
from src.models.data_center import DataCenter
from src.models.maquina_virtual import MaquinaVirtual
from src.models.contenedor import Contenedor
from src.models.solicitud import Solicitud
class Instruccion:
    def __init__(self, tipo):
        self.tipo = tipo

    def __str__(self):
        return "Instruccion tipo=" + str(self.tipo)


class ParserXML:
    def __init__(self):
        self.datacenters = ListaSimple()
        self.maquinas_virtuales = ListaSimple()
        self.contenedores = ListaSimple()
        self.solicitudes = ListaSimple()
        self.instrucciones = ListaSimple()

    def cargar_archivo_xml(self, ruta):
        try:
            tree = ET.parse(ruta)
            root = tree.getroot()

            if root.tag != "cloudSync":
                print("El archivo no es un cloudSync válido.")
                return False

            configuracion = root.find("configuracion")
            instrucciones = root.find("instrucciones")

            if configuracion is not None:
                self._leer_configuracion(configuracion)

            if instrucciones is not None:
                self._leer_instrucciones(instrucciones)

            print("Archivo XML cargado correctamente.")
            return True

        except Exception as e:
            print("Error al leer el archivo XML:", e)
            return False
    def _leer_configuracion(self, configuracion):
        centros = configuracion.find("centrosDatos")
        if centros is not None:
            for centro in centros:
                pais = centro.findtext("ubicacion/pais")
                ciudad = centro.findtext("ubicacion/ciudad")

                cpu = int(centro.findtext("capacidad/cpu") or 0)
                ram = int(centro.findtext("capacidad/ram") or 0)
                almacenamiento = int(centro.findtext("capacidad/almacenamiento") or 0)

                ubicacion = str(ciudad) + ", " + str(pais)

                dc_obj = DataCenter(centro.get("id"), centro.get("nombre"), ubicacion)
                dc_obj.cpu_total = cpu
                dc_obj.ram_total = ram
                dc_obj.alm_total = almacenamiento
                dc_obj.cpu_usado = 0
                dc_obj.ram_usado = 0
                dc_obj.alm_usado = 0

                self.datacenters.insertar_final(dc_obj)
        maquinas = configuracion.find("maquinasVirtuales")
        if maquinas is not None:
            for vm in maquinas:
                vm_id = vm.get("id")
                centro_asignado = vm.get("centroAsignado")

                cpu = int(vm.findtext("recursos/cpu") or 0)
                ram = int(vm.findtext("recursos/ram") or 0)
                almacenamiento = int(vm.findtext("recursos/almacenamiento") or 0)

                so = vm.findtext("sistemaOperativo") or ""
                ip = vm.findtext("ip") or ""

                vm_obj = MaquinaVirtual(vm_id, vm_id, so)
                vm_obj.cpu = cpu
                vm_obj.ram = ram
                vm_obj.almacenamiento = almacenamiento
                vm_obj.ip = ip
                vm_obj.estado = "Activa"
                vm_obj.centro_asignado = centro_asignado

                self.maquinas_virtuales.insertar_final(vm_obj)
                contenedores = vm.find("contenedores")
                if contenedores is not None:
                    for cont in contenedores:
                        cont_id = cont.get("id")
                        nombre = cont.findtext("nombre") or ""
                        imagen = cont.findtext("imagen") or ""

                        c_obj = Contenedor(cont_id, nombre, imagen)
                        c_obj.vm_asignada = vm_id

                        self.contenedores.insertar_final(c_obj)

        solicitudes = configuracion.find("solicitudes")
        if solicitudes is not None:
            for sol in solicitudes:
                sol_id = sol.get("id")
                tipo = sol.findtext("tipo") or ""
                prioridad_txt = sol.findtext("prioridad") or "0"

                try:
                    prioridad = int(prioridad_txt)
                except:
                    prioridad = 0

                cliente = sol.findtext("cliente") or ""
                descripcion = "Cliente: " + str(cliente)

                s_obj = Solicitud(sol_id, tipo, prioridad, descripcion)
                self.solicitudes.insertar_final(s_obj)
    def _leer_instrucciones(self, instrucciones):
        for inst in instrucciones:
            tipo = inst.get("tipo")
            self.instrucciones.insertar_final(Instruccion(tipo))
