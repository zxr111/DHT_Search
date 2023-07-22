from encodings.utf_8 import encode

from common.bencode import bdecode
from common.utils import decode_nodes

if __name__ == '__main__':
    msg = '''收到announce_peer请求 
msg: \n{'a': {'id': b'\x7f\x13\xd1\xc49\\n8:@\xf9\x9e\xb6\x0c\x1b\xe7\x0e\xa7\xa2\x8d\x81', \n\t'implied_port': 1, \n\t'info_hash': b'\xc9\\n/_B##\x07\xb7\xfc\xd5>\xf7\xf6B\x8b\xeba\xdc\x01', \n\t'name': 'The.Express.2008.1080p.BluRay.H264.AAC-RARBG', \n\t'port': 54838, \n\t'token': b'\xc9\\n'}, \n\t'q': 'announce_peer', \n\t't': b'\xc4\x0b\x00\x00', \n\t'v': b'UT\xb15', \n\t'y': 'q'} \nfrom address: ('58.228.63.183', 54838)'''
    print(msg)






