import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, Prehashed

def hash(original_data: str):
    data = original_data.encode('ascii')
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    byte_hash = digest.finalize()
    return base64.b64encode(byte_hash).decode('ascii')


def byte_to_str(data: bytes):
    return base64.b64encode(data).decode('ascii')

def str_to_byte(data: str):
    return base64.b64decode(data.encode('ascii'))


private_key = ec.generate_private_key(ec.SECP256K1())
public_key = private_key.public_key()
public_key_byte = (public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo))
private_key_byte = private_key.private_bytes(
    encoding=serialization.Encoding.DER,               # PEM 형식
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # OpenSSL 스타일
    encryption_algorithm=serialization.NoEncryption()  # 암호화 없이 저장
)
print(byte_to_str(private_key_byte))
print(byte_to_str(public_key_byte))