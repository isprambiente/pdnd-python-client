import tomlkit

with open("pyproject.toml", "r", encoding="utf-8") as f:
    data = tomlkit.parse(f.read())

version = data["project"]["version"]
major, minor, patch = map(int, version.split("."))
patch += 1
new_version = f"{major}.{minor}.{patch}"
data["project"]["version"] = new_version

with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(tomlkit.dumps(data))

print(f"Bumped version to {new_version}")
