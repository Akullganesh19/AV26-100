import jwt
from cryptography.hazmat.primitives import serialization

# In app/api/deps.py:
# payload = jwt.decode(
#    token,
#    public_key,
#    algorithms=["RS256"],
#    issuer=settings.CLERK_ISSUER,
#    audience=settings.CLERK_AUDIENCE,
#    options={"verify_aud": True, "verify_iss": True}
# )
# public_key is settings.CLERK_PEM_PUBLIC_KEY, which is a PEM string.
# Does python-jose handle PEM string? Yes.
# Does PyJWT handle PEM string natively? Yes, as tested above.
# We don't have JWKS dictionary decoding in `deps.py` currently, only PEM.
print("deps.py uses PEM public key, which PyJWT handles natively as a string.")
