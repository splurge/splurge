 
create the server private key, you'll be asked for a passphrase:
$ openssl genrsa -des3 -out server.key 1024

Create the Certificate Signing Request (CSR):
$ openssl req -new -key server.key -out server.csr

Remove the necessity of entering a passphrase for starting up nginx or apache with SSL using the above private key:
$ cp server.key server.key.org
$ openssl rsa -in server.key.org -out server.key

Finally sign the certificate using the above private key and CSR:
$ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
