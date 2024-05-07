import sys
from PIL import Image
import numpy as np
from Crypto.Util import Padding
from Crypto.Cipher import AES
import argparse

parser = argparse.ArgumentParser(prog="AES Image Encrypted",
                                 description="Encrypt any image in AES CFB, CBC or ECB modes")

parser.add_argument('filepath')
parser.add_argument('-k', '--key', default="770A8A65DA156D24EE2A093277530142")

def image_encrypt(img_path, hex_key, aes_type, output_filename):
    
    

    # Validate key, and convert to byte format for AES
    key = None
    try:
        key = bytes.fromhex(hex_key)
    except:
        print("Key not valid hex")
        return
    
    if not key:
        print("Malformed Key: Could not get key from hex input!")
        return
    
    # Validate image and load bmp file contents as binary data
    if not img_path:
        print("Must supply an image")
        return
    img, size = image_load(img_path)
    if not img:
        print("Invalid image provided")
        return
    
    # Determine and choose correct AES mode - padding the data as needed
    aes_mode = None
    match aes_type:
        case "cbc":
            aes_mode = AES.MODE_CBC
            img = Padding.pad(img, 16)
        case "cfb":
            aes_mode = AES.MODE_CFB
        case "ecb":
            aes_mode = AES.MODE_ECB
            img = Padding.pad(img, 16)
        case _:
            print("Invalid supported AES type (cbc, cfb, ecb):", aes_type)
            return
    aes = AES.new(key, aes_mode)
    if not aes:
        print("AES failed to initalise - please check your parameters")
        return
    
    # Encrypt bmp and save contents as a JPG body
    enc_img = aes.encrypt(img)
    output_binary_img(enc_img, size, output_filename)

def image_load(filepath="./Image-Assignment2.bmp"): 
    """
    Load image from filepath, read as binary
    Note: img_size is needed for formatting binary as an JPG image
    """
    img_size = None
    try:
        img_size = Image.open(filepath).size
    except:
        return None, None

    file_obj = open(filepath, 'rb')
    bin_data = file_obj.read()
    file_obj.close()
    return bin_data, img_size


def output_binary_img(img, size, save_path="encrypted-img.jpg"):
    """
    Convert binary data to image body, and save
    """
    output_img = Image.frombuffer("L", size, img)
    output_img.save(save_path)

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    image_encrypt(args.filepath, args.key, "cfb", 'cfb-encrypted.jpg')
    image_encrypt(args.filepath, args.key, "cbc", 'cbc-encrypted.jpg')
    image_encrypt(args.filepath, args.key, "ecb", 'ecb-encrypted.jpg')