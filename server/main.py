import time
from typing import Literal

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

# ---------- Estado en memoria (se borra al reiniciar) ----------
orders = []
next_id = 1
robot = {"estado": "EN_BASE", "pedido_id": None}
cup = {"presente": False, "peso": 0.0}

COLORES = {
    "EN_BASE": "verde",
    "EN_RUTA": "azul",
    "EN_MESA": "amarillo",
    "REGRESANDO": "blanco",
    "ERROR": "rojo",
}

T_RUTA = 15      # segundos simulados de ida
T_REGRESO = 15   # segundos simulados de regreso


# ---------- Modelos ----------
class OrderIn(BaseModel):
    mesa: int


class CupIn(BaseModel):
    peso: float
    cup: Literal["PRESENT", "ABSENT"]


# ---------- Funciones auxiliares ----------
def buscar_pedido(order_id):
    for o in orders:
        if o["id"] == order_id:
            return o
    return None


def siguiente_en_cola():
    for o in orders:               # el primero que entró (FIFO)
        if o["estado"] == "EN_COLA":
            return o
    return None


def simular_ruta(pedido_id):
    time.sleep(T_RUTA)             # aqui luego código real del robot
    if robot["estado"] == "EN_RUTA":
        robot["estado"] = "EN_MESA"
        buscar_pedido(pedido_id)["estado"] = "EN_MESA"


def simular_regreso():
    time.sleep(T_REGRESO)
    if robot["estado"] == "REGRESANDO":
        robot["estado"] = "EN_BASE"
        robot["pedido_id"] = None


def intentar_salida(bg: BackgroundTasks):
    """Sale si: robot en base + hay vaso + hay pedido en cola."""
    if robot["estado"] == "EN_BASE" and cup["presente"]:
        pedido = siguiente_en_cola()
        if pedido:
            pedido["estado"] = "EN_RUTA"
            robot["estado"] = "EN_RUTA"
            robot["pedido_id"] = pedido["id"]
            bg.add_task(simular_ruta, pedido["id"])


# ---------- Endpoints ----------
@app.get("/status")
def status():
    return {
        "robot": robot["estado"],
        "color": COLORES[robot["estado"]],
        "pedido_id": robot["pedido_id"],
        "vaso": cup["presente"],
    }


@app.post("/orders")
def create_order(order: OrderIn, bg: BackgroundTasks):
    global next_id
    if not 1 <= order.mesa <= 5:
        raise HTTPException(status_code=400, detail="Mesa inválida (1 a 5)")
    nuevo = {"id": next_id, "mesa": order.mesa, "estado": "EN_COLA"}
    orders.append(nuevo)
    next_id += 1
    intentar_salida(bg)            # por si el vaso ya estaba puesto
    return nuevo


@app.get("/orders")
def list_orders():
    return orders


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    pedido = buscar_pedido(order_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@app.post("/cup")
def recibir_cup(data: CupIn, bg: BackgroundTasks):
    estaba_presente = cup["presente"]
    cup["presente"] = data.cup == "PRESENT"
    cup["peso"] = data.peso

    if estaba_presente and not cup["presente"]:      # vaso retirado
        if robot["estado"] == "EN_MESA":
            buscar_pedido(robot["pedido_id"])["estado"] = "ENTREGADO"
            robot["estado"] = "REGRESANDO"
            bg.add_task(simular_regreso)
        elif robot["estado"] == "EN_RUTA":           # se cayó en el camino
            robot["estado"] = "ERROR"

    intentar_salida(bg)
    return {"color": COLORES[robot["estado"]]}


@app.post("/robot/reset")
def reset():
    robot["estado"] = "EN_BASE"
    robot["pedido_id"] = None
    return {"robot": robot["estado"]}
