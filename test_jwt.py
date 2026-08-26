import jwt

# Test encode
to_encode = {"sub": "123", "jti": "abc"}
token = jwt.encode(to_encode, "secret", algorithm="HS256")
print("Encoded:", token)

# Test unverified
unverified = jwt.decode(token, options={"verify_signature": False, "verify_exp": False, "verify_aud": False, "verify_iss": False})
print("Unverified:", unverified)

# Test verified
verified = jwt.decode(token, "secret", algorithms=["HS256"])
print("Verified:", verified)
