################################################################
################################################################
## send pubsub ###############
################################################################
################################################################


from google.cloud import pubsub_v1
from google.oauth2 import service_account
from scapy.all import ARP, Ether, srp
import ipaddress
import pandas as pd
from datetime import datetime
import time
import json

# Función para escanear la red y devolver los datos en un formato adecuado para Pub/Sub
def scan_network(network):
    subnet = ipaddress.ip_network(network)
    arp_request = ARP(pdst=str(subnet))
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []
    for sent, received in answered_list:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc, 'timestamp': datetime.now().isoformat()})
    
    return devices

# Función para publicar datos en Pub/Sub
def publish_to_pubsub(project_id, topic_id, data):
    # Crea una instancia de las credenciales a partir del archivo JSON
    credentials_file = '/Users/adrianacamposnarvaez/Desktop/hack/gft-edem-hackathon-a5a971a1f10a.json'
    credentials = service_account.Credentials.from_service_account_file(credentials_file)
    
    # Crea un cliente de Pub/Sub utilizando las credenciales
    publisher = pubsub_v1.PublisherClient(credentials=credentials)

    # Crea el nombre del tema completo
    topic_path = publisher.topic_path(project_id, topic_id)

    # Publica el mensaje en el tema
    future = publisher.publish(topic_path, data=json.dumps(data).encode('utf-8'))
    print(f"Mensaje publicado en {topic_path}.")

    # Espera a que se complete la publicación
    resultado = future.result()
    print(f"Resultado: {resultado}")

def main():
    project_id = "gft-edem-hackathon"
    topic_id = "edem-gft"
    network = "172.28.40.0/24"

    while True:
        devices = scan_network(network)
        for device in devices:
            publish_to_pubsub(project_id, topic_id, device)
        time.sleep(60)

if __name__ == "__main__":
    main()
