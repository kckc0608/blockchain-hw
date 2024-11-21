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

# private_key = ec.generate_private_key(ec.SECP256K1())
# public_key = private_key.public_key()
private_key_str = "MHQCAQEEIGUfOHhOgZRudIWj7VWKD3YGNzFWm/q58QHJigkvtdzCoAcGBSuBBAAKoUQDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejp y7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg=="
public_key_str = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejpy7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg=="
private_key = serialization.load_der_private_key(str_to_byte(private_key_str), password=None)
public_key = private_key.public_key()

# data = "txid0 0 MEUCIH1mbdlc+buiyIBxhazxWfzLITHpoM0Tp53A8VtczAmbAiEAijxUcUF4f6tCWAM2QQVIX57CLlGsSwbMZzUPQCJ+Sg4= MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejpy7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg== [(1, 'test_locking_script'), (2, 'test_locking_script'), (3, 'test_locking_script')]"
data = "txid0 0  [(1, 'test_locking_script'), (2, 'test_locking_script'), (3, 'test_locking_script')]"
# 이때 signature는 input 으로 해당 unlocking script 를 포함하는 트랜잭션 전체를 해시 함수 적용한 후, 그 결과에 서명한 것

# pem_data = private_key.private_bytes(
#     encoding=serialization.Encoding.DER,               # PEM 형식
#     format=serialization.PrivateFormat.TraditionalOpenSSL,  # OpenSSL 스타일
#     encryption_algorithm=serialization.NoEncryption()  # 암호화 없이 저장
# )
# public_key_byte = (public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo))
# print(byte_to_str(pem_data))
# print(byte_to_str(public_key_byte))
data = hash(data)
sig = private_key.sign(str_to_byte(data), ec.ECDSA(Prehashed(hashes.SHA256())))
sig_str = byte_to_str(sig)
# print("transaction hasing : ", data)
# print(hash(public_key_str))
# print(sig_str)
public_key.verify(sig, str_to_byte(data), ec.ECDSA(Prehashed(hashes.SHA256())))


P2PKH_locking = "DUP HASH <pubKeyHash> EQUALVERIFY CHECKSIG"
P2PKH_unlocking = "<sig> <pubKey>"