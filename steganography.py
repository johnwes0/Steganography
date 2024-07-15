import numpy as np
import cv2
import hashlib
import os

def encode_message(img, msg, password):
  """
  Encode a message into the least significant bits of the image pixels using OpenCV method.
  img: numpy array, image array loaded with OpenCV
  msg: str, message to encode
  password: str, password for encoding
  """
  height, width, channels = img.shape

  # Hash the password using SHA-256
  hash_object = hashlib.sha256(password.encode())
  hashed_password = hash_object.digest()

  # Initialize dictionaries for mapping characters to their ASCII values
  d = {}
  for i in range(256):
    d[chr(i)] = i  # Character to ASCII

  # Determine which color channels to modify (typically change least significant bits of 1 or 2 channels)
  channels_to_modify = [0, 1]  # Change least significant bits of channels 0 (Blue) and 1 (Green)

  # Encode the secret message into the image using the hashed password
  index = 0  # Index for the secret message
  for n in range(height):
    for m in range(width):
      if index < len(msg):
        for z in channels_to_modify:
          # Ensure the calculation stays within the 0-255 range
          new_value = (int(img[n, m, z]) + d[msg[index]] + hashed_password[index % len(hashed_password)]) % 256
          img[n, m, z] = new_value
          index += 1
      else:
        break
    if index >= len(msg):
      break

  return img

def decode_message(img, password):
  """
  Decode a message from the least significant bits of the image pixels using OpenCV method.
  img: numpy array, image array loaded with OpenCV
  password: str, password for decoding
  """
  height, width, channels = img.shape

  # Hash the password using SHA-256
  hash_object = hashlib.sha265(password.encode())
  hashed_password = hash_object.digest()

  # Initialize dictionaries for mapping ASCII values to characters
  c = {}
  for i in range(256):
    c[i] = chr(i)  # ASCII to character

  decoded_msg = ""
  index = 0  # Index for the secret message

  # Determine which color channels were modified during encoding
  channels_to_modify = [0, 1]  # Assumed to be the same as in encode_message

  # Define the delimiter used in encoding
  delimiter = "1111111111111110"

  for n in range(height):
    for m in range(width):
      if index < len(hashed_password):
        for z in channels_to_modify:
          decoded_char = (int(img[n, m, z]) - hashed_password[index % len(hashed_password)]) % 256
          decoded_msg += c[decoded_char]
          index += 1
      # Check for delimiter and stop decoding if found
      elif decoded_msg[-len(delimiter):] == delimiter:
        break

  # Remove any remaining padding null characters
  return decoded_msg.strip('\x00')

if __name__ == '__main__':
  while True:
    # Prompt user to choose action: encode or decode
    action = input("Do you want to encode (E) or decode (D) a message (or 'Q' to quit)? ").upper()

    if action == 'Q':
      break

    # Handle encoding
    if action == 'E':
      # Prompt user to enter the image path for encoding
      image_path_encode = input("Enter the image path for encoding: ")

      # Read the input image using OpenCV
      img_encode = cv2.imread(image_path_encode)

      # Check if the image is successfully loaded
      if img_encode is None:
        print("Image not found. Check the file path and make sure the image exists.")
        continue

      # Prompt the user to input the secret message and password
      msg_encode = input("Enter secret message: ")
      password_encode = input("Enter a passcode: ")
      img_encoded = encode_message(img_encode, msg_encode, password_encode)

      # Save the modified image to a new file
      while True:
        output_path_encode = input("Enter the output image path for encoded image (or 'C' to cancel): ")
        if output_path_encode.lower() == 'c':
          break
        try:
          cv2.imwrite(output_path_encode, img_encoded)
          print(f"Message has been encoded into '{output_path_encode}'.")
          break
        except Exception as e:
          print(f"Error saving image: {e}")

    # Handle decoding
    elif action == 'D':
      # Prompt user to enter the image path for decoding
      image_path_decode = input("Enter the image path for decoding: ")

      # Read the encoded image using OpenCV
      img_decode = cv2.imread(image_path_decode)

      # Check if the image is successfully loaded
      if img_decode is None:
        print("Encoded image not found. Check the file path and make sure the image exists.")
        continue

      # Prompt user to enter the password for decoding
      password_decode = input("Enter the passcode for decoding: ")

      # Decode the message from the image using OpenCV method
      decoded_message = decode_message(img_decode, password_decode)

      # Print only the decoded message
      print(f"Decoded message: {decoded_message}")

    else:
      print("Invalid input. Please enter 'E' for encode or 'D' for decode.")