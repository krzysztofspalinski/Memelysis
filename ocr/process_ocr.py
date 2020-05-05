import sys

if __name__ == "__main__":
    data = sys.stdin.read()
    with open("output.txt", "w") as f:
        f.write(data)
