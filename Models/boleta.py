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
        Valida que el RUT cumpla con el formato chileno requerido (ej: 12345678-9 o 1234567-K).
        """
        if not rut or not isinstance(rut, str):
            return False
        
        rut_limpio = rut.strip().replace(".", "").upper()
        patron = r"^\d{7,8}-[\dK]$"
        return bool(re.match(patron, rut_limpio))

    def emitirDocumento(self) -> bool:
        print(f"[Boleta N° {self.numeroBoleta}] Emitida para RUT {self._rutCliente} por un total de ${self.montoTotal} CLP.")
        return True

    def __str__(self):
        return f"Boleta N°{self.numeroBoleta} - Cliente: {self._rutCliente} - Total: ${self.montoTotal}"
