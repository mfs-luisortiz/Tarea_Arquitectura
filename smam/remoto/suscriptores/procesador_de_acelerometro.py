#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Archivo: procesador_de_ritmo_cardiaco.py
# Capitulo: 3 Estilo Publica-Subscribe
# Autor(es): Perla Velasco & Yonathan Mtz.
# Version: 2.0.1 Mayo 2017
# Descripción:
#
#   Esta clase define el rol de un suscriptor, es decir, es un componente que recibe mensajes.
#
#   Las características de ésta clase son las siguientes:
#
#                                  procesador_de_ritmo_cardiaco.py
#           +-----------------------+-------------------------+------------------------+
#           |  Nombre del elemento  |     Responsabilidad     |      Propiedades       |
#           +-----------------------+-------------------------+------------------------+
#           |                       |                         |  - Se suscribe a los   |
#           |                       |                         |    eventos generados   |
#           |                       |  - Procesar valores     |    por el wearable     |
#           |     Procesador de     |    extremos del ritmo   |    Xiaomi My Band.     |
#           |     Ritmo Cardiaco    |    cardiaco.            |  - Define el valor ex- |
#           |                       |                         |    tremo del ritmo     |
#           |                       |                         |    cardiaco en 110.    |
#           |                       |                         |  - Notifica al monitor |
#           |                       |                         |    cuando un valor ex- |
#           |                       |                         |    tremo es detectado. |
#           +-----------------------+-------------------------+------------------------+
#
#   A continuación se describen los métodos que se implementaron en ésta clase:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Recibe los signos  |
#           |       consume()        |          Ninguno         |    vitales vitales    |
#           |                        |                          |    desde el distribui-|
#           |                        |                          |    dor de mensajes.   |
#           +------------------------+--------------------------+-----------------------+
#           |                        |  - ch: propio de Rabbit. |  - Procesa y detecta  |
#           |                        |  - method: propio de     |    valores extremos   |
#           |                        |     Rabbit.              |    del ritmo cardiaco.|
#           |       callback()       |  - properties: propio de |                       |
#           |                        |     Rabbit.              |                       |
#           |                        |  - body: mensaje recibi- |                       |
#           |                        |     do.                  |                       |
#           +------------------------+--------------------------+-----------------------+
#           |    string_to_json()    |  - string: texto a con-  |  - Convierte un string|
#           |                        |     vertir en JSON.      |    en un objeto JSON. |
#           +------------------------+--------------------------+-----------------------+
#
#
#           Nota: "propio de Rabbit" implica que se utilizan de manera interna para realizar
#            de manera correcta la recepcion de datos, para éste ejemplo no shubo necesidad
#            de utilizarlos y para evitar la sobrecarga de información se han omitido sus
#            detalles. Para más información acerca del funcionamiento interno de RabbitMQ
#            puedes visitar: https://www.rabbitmq.com/
#
#-------------------------------------------------------------------------
import pika
import sys
sys.path.append('../')
from monitor import Monitor
import time
import logging


class ProcesadorAcelerometro:

    def consume(self):
        try:
            logging.basicConfig()
            # Url que define la ubicación del Distribuidor de Mensajes
            url = 'amqp://oevvxuqp:D6vn6A9ErigVUrxOINL-ok-vdD610S_I@wombat.rmq.cloudamqp.com/oevvxuqp'
            # Se utiliza como parámetro la URL dónde se encuentra el Distribuidor
            # de Mensajes
            params = pika.URLParameters(url)
            params.socket_timeout = 5
            # Se establece la conexión con el Distribuidor de Mensajes
            connection = pika.BlockingConnection(params)
            # Se solicita un canal por el cuál se enviarán los signos vitales
            channel = connection.channel()
            # Se declara una cola para leer los mensajes enviados por el
            # Publicador
            channel.queue_declare(queue='accelerometer', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(self.callback, queue='accelerometer')
            channel.start_consuming()  # Se realiza la suscripción en el Distribuidor de Mensajes
        except (KeyboardInterrupt, SystemExit):
            channel.close()  # Se cierra la conexión
            sys.exit("Conexión finalizada...")
            time.sleep(1)
            sys.exit("Programa terminado...")

    def callback(self, ch, method, properties, body):
        json_message = self.string_to_json(body)
        if float(json_message['x_position']) <= 0.3 and float(json_message['y_position']) >= 0.7 and float(json_message['z_position']) <= 0.3:
            monitor = Monitor()
            monitor.print_notification2(json_message['datetime'], json_message['id'], json_message[
                                       'x_position'], json_message['y_position'], json_message['z_position'], 'aceleración', json_message['model'])
        time.sleep(1)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def string_to_json(self, string):
        message = {}
        string = string.replace('{', '')
        string = string.replace('}', '')
        values = string.split(', ')
        for x in values:
            v = x.split(': ')
            message[v[0].replace('\'', '')] = v[1].replace('\'', '')
        return message

if __name__ == '__main__':
    p_acelerometro = ProcesadorAcelerometro()
    p_acelerometro.consume()