import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import os
import base64

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.types={}
		self.types['.pdf']='application/pdf'
		self.types['.jpg']='image/jpeg'
		self.types['.txt']='text/plain'
		self.types['.html']='text/html'
	def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")

		response_headers=''
		for i in resp:
			response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
		if (type(messagebody) is not bytes):
			messagebody = messagebody.encode()

		response = response_headers.encode() + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		# set header and body for post if data contains \r\n\r\n
		if "\r\n\r\n" in data:
			header, body = data.split("\r\n\r\n", 1)
		
		requests = data.split("\r\n")
		# print(requests)

		baris = requests[0]
		#print(baris)

		all_headers = [n for n in requests[0:] if n!='']
		# print(all_headers)

		j = baris.split(" ")
		try:
			method=j[0].upper().strip()

			if (method=='GET'):
				object_address = j[1].strip()
				return self.http_get(object_address, all_headers)
			if (method=='POST'):
				object_address = j[1].strip()
				return self.http_post(object_address, all_headers, body)
			if (method=='DELETE'):
				object_address = j[1].strip()
				return self.http_delete(object_address, all_headers)
			else:
				return self.response(400,'Bad Request','',{})
		except IndexError:
			return self.response(400,'Bad Request','',{})
	def http_get(self,object_address,headers):
		files = glob('./*')
		# print(files)
		thedir='./'
		if (object_address == '/'):
			return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

		if (object_address == '/video'):
			return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
		if (object_address == '/santai'):
			return self.response(200,'OK','santai saja',dict())

		if (object_address == '/list'):
			dirpath = './upload/*'
			file_list = glob(dirpath)
			if file_list:
				filename_list = [f"- {os.path.basename(path)}" for path in file_list]
				file_list_str = '\n'.join(filename_list)
				if file_list_str:
					resp = f"File List in ./upload/ directory:\n{file_list_str}"
					return self.response(200, 'OK', resp, dict())
				else:
					return self.response(200, 'OK', 'No file detected', dict())
            
            


		object_address=object_address[1:]
		if thedir+object_address not in files:
			return self.response(404,'Not Found','',{})
		fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
		#harus membaca dalam bentuk byte dan BINARY
		isi = fp.read()
		
		fext = os.path.splitext(thedir+object_address)[1]
		content_type = self.types[fext]
		
		headers={}
		headers['Content-type']=content_type
		
		return self.response(200,'OK',isi,headers)
	def http_post(self,object_address,headers, body=""):
		header_dict = {}
		for h in headers[1:]:
			if ':' in h:
				key, val = h.split(':', 1)
				header_dict[key.strip()] = val.strip()
		isi = "kosong"

		if (object_address == '/upload'):
			try:
				# pindah ke direktori ./upload
				dirpath = "./upload/"
				if not os.path.exists(dirpath):
					os.mkdir(dirpath)
				os.chdir(dirpath)

				filename = header_dict.get('X-Filename')
				decoded_file_body = base64.b64decode(body)
				with open(filename, 'wb') as f:
					f.write(decoded_file_body)
				isi = f"File {filename} berhasil diupload"
				return self.response(200, 'OK', isi, {})
			except Exception as e:
				return self.response(500, 'Failed', f'error upload: {e}', {})
			

		return self.response(404, 'Not Found', 'POST target tidak ditemukan', {})

	def http_delete(self, object_address, headers):
		try:
			target_filepath = '.' + object_address
			os.remove(target_filepath)
			return self.response(200, 'OK', 'Success delete file', {})
		except Exception as e:
			return self.response(400, 'Error', f'Error delete: {e}', {})
		return self.response(404, 'Error', 'File not Found', {})
			 	
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET testing.txt HTTP/1.0')
	print(d)
	d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
#	d = httpserver.http_get('testing.txt')
#	print(d)
