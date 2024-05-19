import sys
from PIL import Image
import numpy as np
from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import argparse


# NOTE: Important - This code must be run in python3.10+ otherwise the Match statements will be seen as invalid syntax

# pip3.10 install -r requirements.txt
# python3.10 encrypt.py img.bmp


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
        return False
    
    if not key:
        print("Malformed Key: Could not get key from hex input!")
        return False
    
    # Validate image and load bmp file contents as binary data
    if not img_path:
        print("Must supply an image")
        return False
    img, size = image_load(img_path)
    if not img or len(img) == 0:
        print("Invalid image provided")
        return False
    
    # Determine and choose correct AES mode - padding the data as needed
    aes = None
    iv = None
    match aes_type:
        case "cbc":
            img = Padding.pad(img, 16)
            iv = get_random_bytes(AES.block_size)
            print("Generated IV:", iv)
            aes = AES.new(key, AES.MODE_CBC, iv=iv)
        case "cfb":
            iv = get_random_bytes(AES.block_size)
            print("Generated IV:", iv)
            aes = AES.new(key, AES.MODE_CFB, iv=iv)
        case "ecb":
            img = Padding.pad(img, 16)
            aes = AES.new(key, AES.MODE_ECB)
        case _:
            print("Invalid supported AES type (cbc, cfb, ecb):", aes_type)
            return False
    if not aes:
        print("AES failed to initalise - please check your parameters")
        return False
    
    # Encrypt bmp and save contents as a JPG body
    enc_img = aes.encrypt(img)
    output_binary_img(enc_img, size, output_filename)
    return True

def image_load(filepath="./Image-Assignment2.bmp"): 
    """
    Load image from filepath, read as binary
    Note: img_size is needed for formatting binary as an JPG image
    """
    img_size = None
    try:
        img = Image.open(filepath)
        img_size = img.size
        return np.asarray(img).flatten().tobytes(), img_size
    except FileNotFoundError:
        return None, None


def output_binary_img(img, size, save_path="encrypted-img.jpg"):
    """
    Convert binary data to image body, and save
    """
    output_img = Image.frombytes("RGB", size, img)
    output_img.save(save_path)
  
def run(args):
    # Return on first fail to avoid printing 3 of the same error
    if not image_encrypt(args.filepath, args.key, "cfb", 'cfb-encrypted.jpg'):
    	return
    if not image_encrypt(args.filepath, args.key, "cbc", 'cbc-encrypted.jpg'):
    	return
    if not image_encrypt(args.filepath, args.key, "ecb", 'ecb-encrypted.jpg'):
    	return

if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    run(args)
  
