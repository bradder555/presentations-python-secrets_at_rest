import os

def secure_delete(file):
    file_len = os.path.getsize(file)
    with open(file, "rb+") as f:
        f.seek(0)
        f.write(b'\x00'*file_len)
    os.unlink(file)