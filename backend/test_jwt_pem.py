import jwt
import json

pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu8J73N2P42y2N9Kz1t8P
... (dummy) ...
-----END PUBLIC KEY-----"""

# Let's create a token signed with an RS256 key
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

pem_priv = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
pem_pub = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

token = jwt.encode({"sub": "test"}, pem_priv, algorithm="RS256")

# Now decode it with PEM
try:
    decoded = jwt.decode(token, pem_pub.decode("utf-8"), algorithms=["RS256"])
    print("Success with PEM string:", decoded)
except Exception as e:
    print("Failed with PEM string:", repr(e))

# What if the key is a JWK dict in PyJWT?
jwk_dict = {
    "kty": "RSA",
    "e": "AQAB",
    "n": "u8J73N2P42y2N9Kz1t8P"
}
try:
    jwt.decode(token, jwk_dict, algorithms=["RS256"])
except Exception as e:
    print("Failed with JWK dict:", repr(e))
