import argparse


def main():
    carrier =


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A steganography tool to conceal a file within an image.')
    parser.add_argument('-i', '--input', dest='input', help='The carrier image to hold the concealed data')
    parser.add_argument('-o', '--output', dest='output', help='The filename to output the combined files as')
    parser.add_argument('-f', '--file', dest='file', help='The file to store in the carrier image')
    args = parser.parse_args()

    main()