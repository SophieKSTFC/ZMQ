import msgpack
from io import BytesIO

from io import StringIO

test = msgpack.packb([1, 2, 3])

this = msgpack.unpackb(test)

print(this)


'''
buf = BytesIO()

for i in range(100):
    buf.write(msgpack.packb(range(i)))

buf.seek(0)

unpacker = msgpack.Unpacker(buf)
for unpacked in unpacker:
    print (unpacked)
'''


data = ('hello', 11, 2.3)

packed = msgpack.packb(data)

print(packed)

 # Streaming works with anything that quacks like a file.
myfile = BytesIO()

packer = msgpack.Packer()

for i in range(3):
    myfile.write(packer.pack(data))

myfile - BytesIO(myfile.getvalue())

unpacker = msgpack.Unpacker(myfile)

for value in unpacker:
    print(value)