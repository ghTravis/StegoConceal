# Stego-Conceal

A proof of concept for concealing a file within a carrier image

### Features

The Stego-Conceal tool allows for a user to take a carrier image and embed a file within it with little to no noticeable difference in image quality for the carrier image

Features include:
* Embed many different file types within the carrier image
* the carrier image is BMP format
* Encrypt the data if desired with a password


### Installation

Be sure to download the proper requirements located in the requirements.txt file

```
pip install -r requirements.txt
```

### Prerequisites

* Python 2.7+

### Usage

To encode a carrier image with a secret file, use the `encode` parameter with an input file, secret file, and output file name:
```
python conceal.py encode -i <path_to_carrier_file> -f <path_to_secret_file> -o <output_file>
```

To decode a carrier image, use the `decode` paramter with the -i flag to specify the carrier image to input with the secret_file embedded, and the output file path:
```
python conceal.py decode -i <path_to_carrier_file> -o <output_file>
```

You can optionally specify a password with the `encode` parameter to encrypt the secret file embedded in the carrier image.
```
python conceal.py encode -i <path_to_carrier_file> -f <path_to_secret_file> -o <output_file> -p test123
python conceal.py decode -i <path_to_carrier_file> -o <output_file> -p test123
```

## Built With

* [Python](https://python.org) - The programming language used

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ghTravis/StegoConceal/tags).

* 1.0.0 - **Initial version** - Pushed to GitHub for public viewing

## Authors

* **Travis Ryder** - *Owner* - [TravisRyder.com](https://travisryder.com)

See also the list of [contributors](https://github.com/ghTravis/StegoConceal/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* BCIT BTech Program