import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
pem_public = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

token = jwt.encode({"sub": "123", "aud": "my-aud", "iss": "my-iss"}, private_key, algorithm="RS256")

# PyJWT decode with audience, issuer, and options
try:
    decoded = jwt.decode(
        token,
        pem_public,
        algorithms=["RS256"],
        audience="my-aud",
        issuer="my-iss",
        options={"verify_aud": True, "verify_iss": True}
    )
    print("Decoded with options:", decoded)
except Exception as e:
    print("Error:", e)

# Unverified claims
try:
    unverified = jwt.decode(token, options={"verify_signature": False})
    print("Unverified:", unverified)
except Exception as e:
    print("Unverified Error:", e)
