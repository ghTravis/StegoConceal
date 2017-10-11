import argparse
import mimetypes
import logging
from conceal.image import Image
from conceal.stego import Stego

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger()


def main():
    carrier = Image(args.input)
    carrier.read()
    conceal = Stego(carrier)

    if args.operation == "encode":
        file = open(args.file, "rb").read()
        conceal.hide_file = file

        mime = mimetypes.guess_type(args.file)

        carrier = conceal.encode(encrypt=args.password or False, mime=mime)
        carrier.write(args.output)

    elif args.operation == "decode":

        mime = mimetypes.guess_type(args.output)
        raw = conceal.decode(mime)

        with open(args.output, "wb") as f:
            f.write(raw)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A steganography tool to conceal a file within an image.')
    parser.add_argument('-i', '--input', dest='input', help='The carrier image to hold the concealed data')
    parser.add_argument('-o', '--output', dest='output', help='The filename to output the combined files as')
    parser.add_argument('-f', '--file', dest='file', help='The file to store in the carrier image')
    parser.add_argument('-p', '--password', dest='password', action="store", help='Encrypt the embedded file with a password')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='Encrypt the embedded file with a password')
    parser.add_argument('operation', choices=['encode', 'decode'], help="Supply the operation you want to perform on the image")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.CRITICAL - (10 * int(args.verbose)))

    main()