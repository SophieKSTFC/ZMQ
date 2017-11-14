import msgpack
import datetime
from nose.tools import assert_equals, assert_raises, assert_true, assert_false,\
    assert_equal, assert_not_equal, assert_regexp_matches


strings = ["xa", "xb", "xd9", "xda", "xdb"]
integers = ["xcc", "xcd", "xce", "xcf", "xd0", "xd1", "xd2", "xd3"]
floats = ["xca", "xcb"]
bytearrays = ["xc4", " xc5", "xc6"]
maps = ["x8", "xde", "xdf"]
arrays = ["x9", "xdc", "xdd"]
booleans = ["xc2", "xc3"]
nils = ["xc0"]


def encoding_test(array, item):

    print("original: ") 
    print(item)
    encoded_item = msgpack.packb(item)
    print("encoded: ")
    print(str(encoded_item))

    for code in array:
        hexcode = (str(encoded_item)[3]) + (str(encoded_item)[4]) + (str(encoded_item)[5])
        if code in hexcode:
            print(hexcode)
            print("Item encoding matches expected hex code format\n--------\n")
            break

def main():

    encoding_test(strings, "mega massive long string ;wKEGJBw;egjbwe;iUTYQWP984RHW4 K.JFBNWMQJEFBJHAVGDFHAGVDFLJAHGABDSLFJBJLHB")
    encoding_test(maps, {"Key1" : "10", "Key2" : "20", "Key3" : "30", "Key4" : "40"})
    encoding_test(arrays, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
    encoding_test(floats, -9.223372036854775807)
    #encoding_test(integers, )
    encoding_test(booleans, True)
    encoding_test(nils, None)
    encoding_test(bytearrays,)


if __name__ == "__main__":
    main()