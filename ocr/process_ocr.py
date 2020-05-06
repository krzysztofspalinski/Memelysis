import sys

if __name__ == "__main__":
    data = sys.stdin.read()
    with open("data_type.txt", "w") as f:
        f.write(type(data))

    print(data)
