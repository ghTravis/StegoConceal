import argparse
import mimetypes
import logging
from conceal.image import Image
from conceal.stego import Stego

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger()


def main():
    """
    Main
    :return:
    """

    # setup class instantiation
    carrier = Image(args.input)
    # read the carrier image into memory
    carrier.read()
    conceal = Stego(carrier)

    # do the encode function if the operation specified was to encode
    if args.operation == "encode":

        # read in the secret file
        file = open(args.file, "rb").read()
        conceal.hide_file = file

        # determine the file type used for the secret file
        mime = mimetypes.guess_type(args.file)

        # encode the secret file into the carrier file, encrypted with a password if specified
        carrier = conceal.encode(encrypt=args.password or False, mime=mime)
        carrier.write(args.output)

    # do the decode function if the operation specified was to decode
    elif args.operation == "decode":

        # determine the file type used for the secret file
        mime = mimetypes.guess_type(args.output)

        # decode the carrier file to reveal the secret file, with a password if secret file is encrypted
        raw = conceal.decode(decrypt=args.password or False, mime=mime)

        # write out to specified output file location
        with open(args.output, "wb") as f:
            f.write(raw)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A steganography tool to conceal a file within an image.')
    parser.add_argument('-i', '--input', dest='input', help='The carrier image to hold the concealed data')
    parser.add_argument('-o', '--output', dest='output', help='The filename to output the combined files as')
    parser.add_argument('-f', '--file', dest='file', help='The file to store in the carrier image')
    parser.add_argument('-p', '--password', dest='password', action="store", help='Encrypt the embedded file with a password')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='Increase verbosity level')
    parser.add_argument('operation', choices=['encode', 'decode'], help="Supply the operation you want to perform on the image")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.CRITICAL - (10 * int(args.verbose)))

    main()
