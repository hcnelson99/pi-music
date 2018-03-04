from pythonosc import osc_message_builder
from pythonosc import udp_client

sender = udp_client.SimpleUDPClient('127.0.0.1', 4559)
sender.send_message('/a', [50, 100, 8]) 
 
