import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                print("Sunucu bağlantıyı kapattı.")
                break
            print(f"Sunucudan gelen yanıt: {response}")
        except ConnectionError as e:
            print(f"Bağlantı hatası: {e}")
            break

def start_tcp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.77.10'  # Sunucu IP adresi
    port = 12345  # Sunucu portu

    try:
        client_socket.connect((host, port))
        print(f"{host}:{port} adresine bağlanıldı.")

        # Sunucudan gelen mesajları dinlemek için bir thread oluşturun
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            # Kullanıcıdan mesaj al
            message = input("Mesaj girin: ")

            # "BYE" girildiyse döngüden çık
            if message.upper() == "BYE":
                client_socket.sendall(message.encode('utf-8'))
                print(f"Sunucuya gönderilen mesaj: {message}")
                break

            # Mesajı sunucuya gönder
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sunucuya gönderilen mesaj: {message}")

    except ConnectionError as e:
        print(f"Bağlantı hatası: {e}")

    finally:
        client_socket.close()
        print("Bağlantı kapatıldı.")

if __name__ == "__main__":
    start_tcp_client()
