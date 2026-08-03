import jwt

# mock clerk token decode
token = jwt.encode({"sub": "123", "aud": "my-aud", "iss": "my-iss"}, "secret", algorithm="HS256")

# how to get unverified claims?
unverified = jwt.decode(token, options={"verify_signature": False})
print("Unverified:", unverified)

# how to decode with audience?
verified = jwt.decode(token, "secret", algorithms=["HS256"], audience="my-aud", issuer="my-iss")
print("Verified:", verified)
