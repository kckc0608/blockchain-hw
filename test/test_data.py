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


private_key_str = "MHQCAQEEIGUfOHhOgZRudIWj7VWKD3YGNzFWm/q58QHJigkvtdzCoAcGBSuBBAAKoUQDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejp y7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg=="
public_key_str = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejpy7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg=="

private_key2 = "MHQCAQEEIJDTgUGM7pYY1WJ1eh3eXxKUiCLrSc6aEip0/+4Ch3nLoAcGBSuBBAAKoUQDQgAEazw7FD31oZtV6gC+F8OfQB1YxYQll5qEhb80GfiGfUZmtYVxV7o+DHMIB3uUVjU6a3+X8hhu5j/afFULCWRcwA=="
public_key2 = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEazw7FD31oZtV6gC+F8OfQB1YxYQll5qEhb80GfiGfUZmtYVxV7o+DHMIB3uUVjU6a3+X8hhu5j/afFULCWRcwA=="

private_key3 = "MHQCAQEEILywPxh/Gc8mkMwVfK6a6pxghGPAfB3zo+tQmZd7hZgYoAcGBSuBBAAKoUQDQgAEC45AV/QSbdCgSfoKEwGv0HRPrNGsTn2u/aQ1+k5mAcjmjdI9Cf1O6ty1IgqdGm1lDEoYmH6pwqGLEsOEJUauEw=="
public_key3 = "MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEC45AV/QSbdCgSfoKEwGv0HRPrNGsTn2u/aQ1+k5mAcjmjdI9Cf1O6ty1IgqdGm1lDEoYmH6pwqGLEsOEJUauEw=="

private_key = serialization.load_der_private_key(str_to_byte(private_key_str), password=None)
public_key = private_key.public_key()

# data = "txid0 0 MEUCIH1mbdlc+buiyIBxhazxWfzLITHpoM0Tp53A8VtczAmbAiEAijxUcUF4f6tCWAM2QQVIX57CLlGsSwbMZzUPQCJ+Sg4= MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEdvLD3mnd3k7iWpRDqo6RvxdvbA7HC8jlNsCqIXLmxiI59Ejpy7SPsU2M3jhWlhoSgw9JcUwENdZCutwmQLILJg== [(1, 'test_locking_script'), (2, 'test_locking_script'), (3, 'test_locking_script')]"
# data = "txid0 0  [(1, 'test_locking_script'), (2, 'test_locking_script'), (3, 'test_locking_script')]"
data = "txid0 0  [(1, 'OP_DUP OP_HASH <scriptXHash> OP_EQUALVERIFY'), (2, 'test_locking_script'), (3, 'test_locking_script')]"
# 이때 signature는 input 으로 해당 unlocking script 를 포함하는 트랜잭션 전체를 해시 함수 적용한 후, 그 결과에 서명한 것

public_key1_obj = serialization.load_der_public_key(str_to_byte(public_key_str))
private_key1_obj = serialization.load_der_private_key(str_to_byte(private_key_str), password=None)

public_key2_obj = serialization.load_der_public_key(str_to_byte(public_key2))
private_key2_obj = serialization.load_der_private_key(str_to_byte(private_key2), password=None)
# data = hash(data)
tx2_hash = "2n/xwTuqEIC94Fpk0cE6HpzsKJ1txCZPpt9rq5u/9MU="
tx3_hash = "NrXDNealMeCuO04cBYsge8IqwNQKyP+wmVDpqrWMmio="
sig = private_key1_obj.sign(str_to_byte(tx3_hash), ec.ECDSA(Prehashed(hashes.SHA256())))
sig2 = private_key2_obj.sign(str_to_byte(tx3_hash), ec.ECDSA(Prehashed(hashes.SHA256())))
sig_str = byte_to_str(sig2)
print("transaction hasing : ", tx3_hash)
print(hash(public_key_str))
print(sig_str)
public_key1_obj.verify(sig, str_to_byte(tx3_hash), ec.ECDSA(Prehashed(hashes.SHA256())))


P2PKH_locking = "DUP HASH <pubKeyHash> EQUALVERIFY CHECKSIG"
P2PKH_unlocking = "<sig> <pubKey>"