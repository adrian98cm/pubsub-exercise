# Pub/Sub con RabbitMQ y PostgreSQL

Este proyecto implementa un sistema de publicación/suscripción utilizando RabbitMQ como broker de mensajes y PostgreSQL como base de datos para almacenar los resultados.

## Descripción del Problema

Se requiere crear un sistema donde un `Publisher` genera números aleatorios y los envía a través de RabbitMQ. Un `Subscriber` recibe estos números, calcula su cuadrado y almacena el resultado en una base de datos PostgreSQL.

## Solución Implementada

La solución se divide en cuatro componentes principales:

1.  **RabbitMQ:**
    * Actúa como broker de mensajes, permitiendo la comunicación asíncrona entre el Publisher y el Subscriber.
    * Utiliza una cola llamada `numbers` para almacenar los mensajes (generada por el publisher o por el subscriber, la genera el primero que se conecte a RabbitMQ).

1.  **Publisher:**
    * Genera números aleatorios entre 1 y 100.
    * Envía los números como mensajes JSON a una cola de RabbitMQ llamada `numbers` (enviado el mensaje al exchange por defecto de RabbitMQ, si tuviésemos más  mensajería, deberíamos estructurar la relación entre exchanges y colas).
    * Implementado en Python usando la librería `pika`.
    * Maneja errores de conexión con RabbitMQ al inicializar el servicio, el periodo de re-intento de conexión es parametrizable.
    * Utiliza `uv` como gestor de paquetes para gestionar las dependencias del proyecto.

2.  **Subscriber:**
    * Recibe los mensajes de la cola `numbers` de RabbitMQ.
    * Calcula el cuadrado del número recibido.
    * Almacena el número original, el resultado y las marcas de tiempo en una tabla `results` en PostgreSQL.
    * Implementado en Python usando las librerías `pika` y `psycopg`.
    * Maneja errores de conexión con RabbitMQ al inicializar el servicio, el periodo de re-intento de conexión es parametrizable.
    * Implementa manejo de errores en el procesamiento de mensajes, reenviando los mensajes a la cola en caso de errores de base de datos y descartándolos en caso de errores de decodificación JSON.
    * Utiliza `uv` como gestor de paquetes para gestionar las dependencias del proyecto.

3.  **Base de Datos PostgreSQL:**
    * Utilizada para almacenar los resultados del procesamiento.
    * La tabla `results` tiene las siguientes columnas: `id`, `number`, `result`, `message_timestamp` y `processed_timestamp`.
    * Se inicializa con un script SQL (`schema.sql`) que crea la tabla si no existe.

## Configuración y Ejecución

1.  **Requisitos:**
    * Docker y Docker Compose instalados.

2.  **Configuración:**
    * Las variables de entorno para la conexión a RabbitMQ y PostgreSQL se configuran en el archivo `docker-compose.yml`.

3.  **Ejecución:**
    * Ejecutar `docker compose up --build -d` desde la raíz del proyecto.
    * Esto creará las imagenes del Publisher y Subscriber e iniciará los contenedores de RabbitMQ, PostgreSQL, Publisher y Subscriber.

## Escalabilidad

* El sistema se puede escalar fácilmente aumentando el número de contenedores de Publisher y Subscriber usando `docker compose up --scale publisher=N --scale subscriber=M`.