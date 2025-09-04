# communication_manager.py
import socket
import json
import time
from datetime import datetime
import threading
import select # For non-blocking socket operations
import pika 

class CommunicationManager:
    def __init__(self, protocol='udp', machine_code="MC001", host='192.168.128.240', port=9000):
        """
        Initializes the CommunicationManager with the specified protocol.
        
        Args:
            protocol (str): 'socket' for direct TCP connection, 'rabbitmq' for RabbitMQ.
            machine_code (str): A unique identifier for this machine.
            host (str): Host for socket server (e.g., '0.0.0.0' for all interfaces).
            port (int): Port for socket server.
        """
        self.protocol = protocol.lower()
        self.machine_code = machine_code
        self.host = host
        self.port = port
        
        # if self.protocol == 'socket':
        #     self._start_socket_server_in_background()
        # # --- Socket specific attributes ---
        # self.socket_server = None
        # self.client_socket = None
        # self.client_address = None
        # self.is_socket_connected = False
        # self.socket_lock = threading.Lock() # To protect socket operations
        # self.socket_listen_thread = None
        
        # --- RabbitMQ specific attributes (placeholders for now) ---
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.rabbitmq_host = 'localhost'
        self.rabbitmq_port = 5672
        self.rabbitmq_exchange = 'machine_state_updates' # A common exchange name
        self.rabbitmq_routing_key = '' # Often empty for fanout or direct to queue
        
        if self.protocol == 'udp':
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        elif self.protocol == 'rabbitmq':
             self.rabbitmq_host = self.host
             self.rabbitmq_port = self.port
             self._connect_rabbitmq() # This would ideally run in a separate thread for robust reconnection
        
        print(f"CommunicationManager initialized with protocol: '{self.protocol}'")

        

    # --- UDP only ---
    def _send_via_udp(self, data):
        try:
            json_message = json.dumps(data)
            self.udp_socket.sendto(json_message.encode('utf-8'), (self.host, self.port))
            print(f"UDP: Message sent to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"UDP: Error sending message: {e}")
            return False

    def send_state_update(self, state_name):
        message_data = {
            "MachineCode": self.machine_code,
            "OnDateTime": datetime.now().isoformat(),
            "Status": state_name
        }
        print(f"CommWrapper: Preparing message: {message_data}")
        if self.protocol == 'udp':
            return self._send_via_udp(message_data)
        # elif self.protocol == 'socket':
        #     return self._send_via_socket(message_data)
        elif self.protocol == 'rabbitmq':
            return self._send_via_rabbitmq(message_data)
        else:
            print(f"CommWrapper: ERROR: Unknown communication protocol specified: '{self.protocol}'")
            return False

    def send_ok_qty(self, ok_qty):
        message_data = {
            "OnDateTime": datetime.now().isoformat(),
            "MachineCode": self.machine_code,
            "OKQty": ok_qty
        }
        print(f"CommWrapper: Preparing OKQty message: {message_data}")
        if self.protocol == 'udp':
            return self._send_via_udp(message_data)
        elif self.protocol == 'rabbitmq':
            return self._send_via_rabbitmq(message_data)
        else:
            print(f"CommWrapper: ERROR: Unknown communication protocol specified: '{self.protocol}'")
            return False    
    
    def close(self):
        print("CommunicationManager: Closing resources...")
        # if self.protocol == 'socket':
        #     self._close_socket_client()
        #     self._close_socket_server()
        if self.protocol == 'udp':
            if self.udp_socket:
                self.udp_socket.close()
        print("CommunicationManager: Resources closed.")



    # --- RabbitMQ Placeholder Methods (remain commented until you provide details) ---
    def _connect_rabbitmq(self):
        print("RabbitMQ: Attempting to connect...")
        try:
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                heartbeat=60,
                blocked_connection_timeout=30
            )
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(
                exchange=self.rabbitmq_exchange,
                exchange_type='fanout',
                durable=True
            )
            print("RabbitMQ: Connected successfully.")
            return True
        except Exception as e:
            print(f"RabbitMQ: Connection error: {e}")
            self.rabbitmq_connection = None
            self.rabbitmq_channel = None
            return False

    def _send_via_rabbitmq(self, data):
        if not self.rabbitmq_channel:
            print("RabbitMQ: Not connected, attempting to reconnect...")
            if not self._connect_rabbitmq():
                print("RabbitMQ: Reconnection failed, message not sent.")
                return False
                
        try:
            json_message = json.dumps(data)
            self.rabbitmq_channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=json_message
            )
            print(f"RabbitMQ: Message sent: {json_message}")
            return True
        except Exception as e:
            print(f"RabbitMQ: Error sending message: {e}")
            self._close_rabbitmq()
            return False

    def _close_rabbitmq(self):
        """Close RabbitMQ connection and clean up resources."""
        if self.rabbitmq_connection:
            try:
                self.rabbitmq_connection.close()
                print("RabbitMQ: Connection closed.")
            except Exception as e:
                print(f"RabbitMQ: Error closing connection: {e}")
            finally:
                self.rabbitmq_connection = None
                self.rabbitmq_channel = None



# --- TCP only ---
    # def _start_socket_server_in_background(self):
    #     """Starts a dedicated thread to listen for and manage a single client socket connection."""
    #     self.socket_listen_thread = threading.Thread(target=self._socket_listener_loop, daemon=True)
    #     self.socket_listen_thread.start()
    #     print(f"Socket server listening thread started for {self.host}:{self.port}")

    # def _socket_listener_loop(self):
    #     """The main loop for the socket server thread, handling client connections."""
    #     try:
    #         self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows immediate reuse of address
    #         self.socket_server.bind((self.host, self.port))
    #         self.socket_server.listen(1) # Listen for one incoming connection
    #         print(f"Socket server listening on {self.host}:{self.port} in background thread.")

    #         while True: # Loop indefinitely to accept new connections if current one drops
    #             if not self.is_socket_connected:
    #                 print("Socket: Waiting for client connection...")
    #                 try:
    #                     # Use select for a non-blocking accept with a timeout
    #                     rlist, _, _ = select.select([self.socket_server], [], [], 1.0) # Check every 1 second
    #                     if rlist: # If socket_server is ready to be accepted
    #                         with self.socket_lock:
    #                             self.client_socket, self.client_address = self.socket_server.accept()
    #                             self.client_socket.setblocking(False) # Make client socket non-blocking
    #                             self.is_socket_connected = True
    #                             print(f"Socket: Client connected from {self.client_address}")
    #                             # Optionally send a "connection_established" message here
    #                 except select.error as e: # Handle specific select errors (e.g., interrupted system call)
    #                     if e.errno != 4: # EINTR - an interrupted system call is fine to ignore
    #                         print(f"Socket: Select error during accept: {e}")
    #                 except Exception as e:
    #                     print(f"Socket: Error accepting connection: {e}")
    #                     with self.socket_lock: # Ensure proper cleanup on error
    #                         self._close_socket_client()
    #                     time.sleep(1) # Wait a bit before retrying

    #             time.sleep(0.1) # Small delay to prevent busy-waiting if already connected
    #     except Exception as e:
    #         print(f"Socket: Fatal error in server listener thread: {e}")
    #         self.is_socket_connected = False
    #         self._close_socket_server() # Attempt to close the server socket on thread failure

    # def _send_via_socket(self, data):
    #     """Internal method to send JSON data over the connected TCP socket."""
    #     if not self.is_socket_connected or not self.client_socket:
    #         print("Socket: Not connected to client, message not sent.")
    #         return False
            
    #     try:
    #         with self.socket_lock: # Protect socket operations
    #             json_message = json.dumps(data) + '\n' # Add newline as a delimiter
    #             # Use sendall to ensure all data is sent, handling buffering
    #             self.client_socket.sendall(json_message.encode('utf-8'))
    #         print(f"Socket: Message sent successfully.")
    #         return True
    #     except (BrokenPipeError, ConnectionResetError) as e:
    #         print(f"Socket: Connection lost during send: {e}")
    #         with self.socket_lock:
    #             self._close_socket_client() # Client disconnected
    #         self.is_socket_connected = False
    #         return False
    #     except BlockingIOError: # Client socket is non-blocking, so this can happen if buffer is full
    #         print("Socket: Send buffer full, message temporarily blocked.")
    #         return False # Indicate that it couldn't send *right now*
    #     except Exception as e:
    #         print(f"Socket: Error sending message: {e}")
    #         with self.socket_lock:
    #             self._close_socket_client()
    #         self.is_socket_connected = False
    #         return False

    # def _close_socket_client(self):
    #     """Closes the client socket connection."""
    #     if self.client_socket:
    #         try:
    #             self.client_socket.shutdown(socket.SHUT_RDWR) # Attempt graceful shutdown
    #             self.client_socket.close()
    #         except OSError as e: # Catch errors if socket is already closed/invalid
    #             print(f"Socket: Error during client socket shutdown/close: {e}")
    #         self.client_socket = None
    #         self.client_address = None
    #         self.is_socket_connected = False
    #         print("Socket: Client connection closed.")

    # def _close_socket_server(self):
    #     """Closes the main listening socket."""
    #     if self.socket_server:
    #         try:
    #             self.socket_server.shutdown(socket.SHUT_RDWR)
    #             self.socket_server.close()
    #         except OSError as e:
    #             print(f"Socket: Error during server socket shutdown/close: {e}")
    #         self.socket_server = None
    #         print("Socket: Server listening socket closed.")


    # --- Public Wrapper Function (API for the main script) ---
    # def send_state_update(self, state_name):
    #     """
    #     Public wrapper function to send a machine state update message.
    #     This function chooses the underlying communication protocol.
        
    #     Args:
    #         state_name (str): The name of the new machine state (e.g., "MACHINE_STOP").
            
    #     Returns:
    #         bool: True if the message was successfully dispatched (or queued), False otherwise.
    #     """
    #     message_data = {
    #         "MachineCode": self.machine_code,
    #         "OnDateTime": datetime.now().isoformat(), # Current timestamp for the event
    #         "Status": state_name
    #     }
        
    #     print(f"CommWrapper: Preparing message: {message_data}")

    #     if self.protocol == 'socket':
    #         return self._send_via_socket(message_data)
    #     # elif self.protocol == 'rabbitmq':
    #     #     return self._send_via_rabbitmq(message_data)
    #     else:
    #         print(f"CommWrapper: ERROR: Unknown communication protocol specified: '{self.protocol}'")
    #         return False

    # def close(self):
    #     """Cleans up communication resources based on the active protocol."""
    #     print("CommunicationManager: Closing resources...")
    #     if self.protocol == 'socket':
    #         self._close_socket_client()
    #         self._close_socket_server() # Ensure the listening server socket is also closed
    #     # elif self.protocol == 'rabbitmq':
    #     #     self._close_rabbitmq()
    #     print("CommunicationManager: Resources closed.")







