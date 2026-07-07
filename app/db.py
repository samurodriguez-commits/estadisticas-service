"""
db.py — Conexión de SOLO LECTURA a PostgreSQL (compartida con casino-backend).

A diferencia de los otros servicios, estadisticas-service no crea tablas: solo
agrega datos de `transacciones`, `usuarios` y `apuestas`. Config 12-factor por env.
"""
import os
import time

import psycopg2
import psycopg2.extras
import psycopg2.pool
from psycopg2 import extensions

# NUMERIC -> float para respuestas JSON nativas.
_DEC2FLOAT = extensions.new_type(
    extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
extensions.register_type(_DEC2FLOAT)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "casino"),
    "password": os.getenv("DB_PASSWORD", "casino"),
    "dbname": os.getenv("DB_NAME", "casino_db"),
}

_pool: psycopg2.pool.ThreadedConnectionPool | None = None


def esperar_bd(max_intentos: int = 30, espera_s: float = 2.0) -> None:
    """Reintenta hasta que Postgres acepte consultas (arranque asincrónico)."""
    global _pool
    ultimo_error = None
    for intento in range(1, max_intentos + 1):
        try:
            _pool = psycopg2.pool.ThreadedConnectionPool(1, 10, **DB_CONFIG)
            conn = _pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            _pool.putconn(conn)
            print(f"[PG] Conexión establecida (intento {intento})", flush=True)
            return
        except Exception as err:  # noqa: BLE001
            ultimo_error = err
            print(f"[PG] BD no disponible ({intento}/{max_intentos}): {err}", flush=True)
            time.sleep(espera_s)
    raise RuntimeError(f"No se pudo conectar a Postgres: {ultimo_error}")


class _Conexion:
    """Context manager: presta una conexión del pool y la devuelve siempre."""

    def __enter__(self):
        self.conn = _pool.getconn()
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.conn.rollback()
        _pool.putconn(self.conn)


def conexion() -> _Conexion:
    return _Conexion()


def dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def ping() -> bool:
    try:
        with conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001
        return False
