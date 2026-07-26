with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("ubuntu-latest", "ubuntu-24.04")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
