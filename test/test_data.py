import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

private_key = ec.generate_private_key(ec.SECP256K1())
public_key = private_key.public_key()



data = b"test_data" # 이때 signature는 input 으로 해당 unlocking script 를 포함하는 트랜잭션 전체를 해시 함수 적용한 후, 그 결과에 서명한 것
sig = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
# sig = decode_dss_signature(sig)
base64_ascii = base64.b64encode(sig).decode('ascii')
public_key_byte = (public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo))
public_key_str = base64.b64encode(public_key_byte).decode('ascii')
print(public_key_str)
print(serialization.load_der_public_key(base64.b64decode(public_key_str.encode('ascii'))))
public_key.verify(sig, data, ec.ECDSA(hashes.SHA256()))


P2PKH_locking = "DUP HASH <pubKeyHash> EQUALVERIFY CHECKSIG"
P2PKH_unlocking = "<sig> <pubKey>"