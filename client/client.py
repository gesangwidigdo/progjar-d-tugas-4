import socket
import logging
import base64
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True, help="Server host")
parser.add_argument("--port", type=int, required=True, help="Server port")
parser.add_argument("--command", choices=["list", "upload", "delete"], required=True, help="Command to execute")
parser.add_argument("--file", help="File path for upload or delete")
args = parser.parse_args()

def send_command(command_str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (args.host, args.port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        logging.warning(f"sending message ")
        command_str = command_str + "\r\n"
        sock.sendall(command_str.encode())

        data_recv = ""
        while True:
            data = sock.recv(4096)
            if data:
                data_recv += data.decode()
                if "\r\n\r\n" in data_recv:
                    break
                else:
                    break
        hasil = data_recv
        logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving: {str(ee)}")
        return False

cmd = ""
def get_files():
    # Get Request
    cmd = f"""GET /list HTTP/1.1
Host: {args.host}
User-Agent: myclient/1.1
Accept: */*
"""
    return send_command(cmd)

def upload_file(filepath):
    try:
        with open(filepath, "rb") as f:
            filecontent = base64.b64encode(f.read()).decode()

        filename = os.path.basename(filepath)
    
        headers = [
            f"POST /upload HTTP/1.1",
            f"Host: {args.host}",
            f"User-Agent: myclient/1.1",
            f"Content-Length: {len(filecontent)}",
            f"X-Filename: {filename}"
        ]
    
        cmd = "\r\n".join(headers) + "\r\n\r\n" + filecontent
        return send_command(cmd)
    except Exception as ee:
        logging.warning(f"Failed to read or encode file: {str(ee)}")
        return False

def delete_file(route_file_path):
    cmd = f"""DELETE /{route_file_path} HTTP/1.1
Host: {args.host}
User-Agent: myclient/1.1
"""
    return send_command(cmd)


if __name__ == "__main__":
    if args.command == "list":
        result = get_files()
    elif args.command == "upload":
        if not args.file:
            print("Please provide --file for upload.")
            exit(1)
        result = upload_file(args.file)
    elif args.command == "delete":
        if not args.file:
            print("Please provide --file for delete.")
            exit(1)
        result = delete_file(args.file)
    else:
        result = "Invalid command."

    print("Result from server:")
    print(result)