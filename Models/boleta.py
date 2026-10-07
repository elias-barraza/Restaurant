import re

class Boleta:
    def __init__(self, numero_boleta: int = 1, rut_cliente: str = "", monto_total: int = 0):
        self.numeroBoleta = numero_boleta
        self._rutCliente = ""
        if rut_cliente:
            self.rut_cliente = rut_cliente
        self.montoTotal = monto_total

    @property
    def rut_cliente(self) -> str:
        return self._rutCliente

    @rut_cliente.setter
    def rut_cliente(self, rut: str):
        if not self.validarRut(rut):
            raise ValueError(f"El RUT '{rut}' no tiene un formato válido (debe contener cuerpo numérico y dígito verificador, ej. 12345678-9).")
        self._rutCliente = rut

    # Soporte para camelCase acorde al diagrama UML
    @property
    def rutCliente(self) -> str:
        return self._rutCliente

    @rutCliente.setter
    def rutCliente(self, rut: str):
        self.rut_cliente = rut

    def validarRut(self, rut: str) -> bool:
        """
        Valida que el RUT cumpla con el formato chileno y su dígito verificador oficial (Módulo 11).
        Ejemplos: 12.345.678-5 (Válido), 12.345.678-9 (Inválido - DV incorrecto).
        """
        if not rut or not isinstance(rut, str):
            return False
        
        rut_limpio = rut.strip().replace(".", "").replace(" ", "").upper()
        patron = r"^(\d{7,8})-([\dK])$"
        match = re.match(patron, rut_limpio)
        if not match:
            return False
        
        cuerpo, dv = match.groups()
        multiplicadores = [2, 3, 4, 5, 6, 7]
        suma = sum(int(c) * multiplicadores[i % 6] for i, c in enumerate(reversed(cuerpo)))
        resto = suma % 11
        dv_calculado = 11 - resto
        if dv_calculado == 11:
            dv_esperado = "0"
        elif dv_calculado == 10:
            dv_esperado = "K"
        else:
            dv_esperado = str(dv_calculado)
        
        return dv == dv_esperado

    def emitirDocumento(self) -> bool:
        print(f"[Boleta N° {self.numeroBoleta}] Emitida para RUT {self._rutCliente} por un total de ${self.montoTotal} CLP.")
        return True

    def __str__(self):
        return f"Boleta N°{self.numeroBoleta} - Cliente: {self._rutCliente} - Total: ${self.montoTotal}"
