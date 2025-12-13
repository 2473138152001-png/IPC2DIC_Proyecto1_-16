import xml.etree.ElementTree as ET


class ParserXML:
    def __init__(self):
        # listas simples para guardar lo que se lea del XML
        self.datacenters = []
        self.maquinas_virtuales = []
        self.contenedores = []
        self.solicitudes = []
        self.instrucciones = []

    def cargar_archivo_xml(self, ruta):
        try:
            tree = ET.parse(ruta)
            root = tree.getroot()

            # validar etiqueta principal
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

    # ----------------------------
    # Métodos auxiliares
    # ----------------------------

    def _leer_configuracion(self, configuracion):
        # Leer centros de datos
        centros = configuracion.find("centrosDatos")
        if centros is not None:
            for centro in centros:
                pais= centro.find("ubicacion/pais").text
                ciudad = centro.find("ubicacion/ciudad").text

                cpu = int(centro.find("capacidad/cpu").text)
                ram = int(centro.find("capacidad/ram").text)
                almacenamiento = int(centro.find("capacidad/almacenamiento").text)
                self.datacenters.append({
                "id": centro.get("id"),
                "nombre": centro.get("nombre"),
                "ubicacion": f"{ciudad}, {pais}",
                "cpu_total": cpu,
                "ram_total": ram,
                "alm_total": almacenamiento
            })
        
        # Leer máquinas virtuales
        maquinas = configuracion.find("maquinasVirtuales")
        if maquinas is not None:
            for vm in maquinas:
                self.maquinas_virtuales.append({
                    "id": vm.get("id"),
                    "centro": vm.get("centroAsignado")
                })

                # leer contenedores de la VM
                contenedores = vm.find("contenedores")
                if contenedores is not None:
                    for cont in contenedores:
                        self.contenedores.append({
                            "id": cont.get("id"),
                            "vm": vm.get("id")
                        })

        # Leer solicitudes
        solicitudes = configuracion.find("solicitudes")
        if solicitudes is not None:
            for sol in solicitudes:
                self.solicitudes.append({
                    "id": sol.get("id"),
                    "cliente": sol.findtext("cliente"),
                    "tipo": sol.findtext("tipo"),
                    "prioridad": sol.findtext("prioridad")
                })

    def _leer_instrucciones(self, instrucciones):
        for inst in instrucciones:
            self.instrucciones.append({
                "tipo": inst.get("tipo")
            })
