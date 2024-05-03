from scapy.all import ARP, Ether, srp
import ipaddress
import pandas as pd
from datetime import datetime
import time

def scan_network(network):
    # Convertir la red en un objeto de subred IP para iterar sobre todas las posibles IP
    subnet = ipaddress.ip_network(network)
    
    # Crear un paquete ARP
    arp_request = ARP(pdst=str(subnet))
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    
    # Enviar el paquete y esperar las respuestas
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    # Listar los dispositivos encontrados
    devices = []
    for sent, received in answered_list:
        # Por cada respuesta, guardar la IP y la MAC
        devices.append({'ip': received.psrc, 'mac': received.hwsrc, 'timestamp': datetime.now()})
    
    return devices

def main():
    network = "172.28.40.0/24"  # Asegúrate de ajustar esto según tu red
    while True:
        devices = scan_network(network)
        df = pd.DataFrame(devices)
        print(df)
        time.sleep(60)  # Espera 60 segundos antes de repetir el escaneo

if __name__ == "__main__":
    main()
