# Reservation System (CLI)

Sistema de reservaciones por línea de comandos (CLI) que permite administrar **Hoteles**, **Clientes** y **Reservaciones** con persistencia en archivos **JSON**.

## Funcionalidades

### Hoteles
- Crear hotel (con `total_rooms` y `available_rooms`)
- Consultar hotel por `hotel_id`
- Modificar hotel (nombre, ubicación, total de cuartos)
  - No permite reducir `total_rooms` por debajo de los cuartos ya reservados
- Eliminar hotel
- Reservar / liberar cuarto (usado internamente por reservaciones)

### Clientes
- Crear cliente
- Consultar cliente por `customer_id`
- Modificar cliente (nombre y/o email)
- Eliminar cliente
- Validación básica de email (debe contener `@`)

### Reservaciones
- Crear reservación
  - Valida que existan el cliente y el hotel
  - Decrementa `available_rooms` del hotel (reserva un cuarto)
- Cancelar reservación
  - Es idempotente (cancelar dos veces no falla)
  - Incrementa `available_rooms` del hotel (libera un cuarto)

### Persistencia y tolerancia a errores
- Los datos se almacenan en:
  - `data/hotels.json`
  - `data/customers.json`
  - `data/reservations.json`
- Si los archivos JSON están corruptos o contienen registros inválidos, el sistema:
  - imprime mensajes `[DATA ERROR] ...`
  - ignora los items inválidos y continúa ejecutándose (best-effort)

---

## Estructura del proyecto

```
A01328387_A6.2/
├─ main.py
├─ source/
│  ├─ customers.py
│  ├─ hotels.py
│  ├─ reservation.py
│  └─ storage.py
├─ data/
│  ├─ customers.json
│  ├─ hotels.json
│  └─ reservations.json
├─ test/
│  └─ unit/
│     └─ src/
│        ├─ base_test_case.py
│        ├─ customers_test.py
│        ├─ hotels_test.py
│        └─ reservation_test.py
├─ test_cases/
│  ├─ TC1
│  ├─ TC2
│  └─ TC3
├─ results/
├─ .coverage
└─ .gitignore
```

---

## Requisitos

- Python 3.10+ (recomendado 3.11/3.12)
- `unittest` (incluido en la librería estándar)

Opcional (calidad):
- `flake8`
- `pylint`
- `coverage`

---

## Cómo ejecutar el programa

Desde la raíz del proyecto:

```bash
python main.py
```

Al iniciar, el programa crea el directorio `data/` y los archivos JSON si no existen.

### Menú del CLI

- `1` Create Hotel  
- `2` Display Hotel  
- `3` Modify Hotel  
- `4` Delete Hotel  
- `5` Create Customer  
- `6` Display Customer  
- `7` Modify Customer  
- `8` Delete Customer  
- `9` Create Reservation  
- `10` Cancel Reservation  
- `0` Exit  

---

## Ejemplos de flujo (inputs)

### Crear hotel, cliente, reservación y salir

Entradas (una por línea):

```
1
H1
Hotel One
MTY
2
5
C1
Miguel Silva
miguel@test.com
9
R1
C1
H1
0
```

Qué sucede:
- Se crea el hotel `H1` con 2 cuartos disponibles.
- Se crea el cliente `C1`.
- Se crea la reservación `R1` y el hotel `H1` decrementa `available_rooms` de 2 a 1.

### Intentar reservar con hotel inexistente

```
5
C1
Miguel Silva
miguel@test.com
9
R1
C1
H404
0
```

Resultado:
- Se imprime `[ERROR] Hotel not found`.

---

## Formato de datos (JSON)

### `data/hotels.json`
Lista de objetos:

```json
[
  {
    "hotel_id": "H1",
    "name": "Hotel One",
    "location": "MTY",
    "total_rooms": 2,
    "available_rooms": 2
  }
]
```

### `data/customers.json`

```json
[
  {
    "customer_id": "C1",
    "full_name": "Miguel Silva",
    "email": "miguel@test.com"
  }
]
```

### `data/reservations.json`

```json
[
  {
    "reservation_id": "R1",
    "hotel_id": "H1",
    "customer_id": "C1",
    "created_at": "2026-02-21T12:00:00Z",
    "canceled_at": null
  }
]
```

---

## Ejecutar pruebas unitarias

Desde la raíz del proyecto:

```bash
python -m unittest -v
```

O específicamente:

```bash
python -m unittest -v test.unit.src.hotels_test
python -m unittest -v test.unit.src.customers_test
python -m unittest -v test.unit.src.reservation_test
```

---

## Cobertura (opcional)

Si tienes `coverage` instalado:

```bash
coverage run -m unittest -v
coverage report -m
```

---

## Calidad de código (opcional)

### flake8
```bash
flake8 .
```

### pylint
```bash
pylint source test main.py
```

---
