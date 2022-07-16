import argparse
from downloaders import DOWNLOADERS
from generators import GENERATORS
from transformations import TRANSFORMATIONS

if __name__ == '__main__':

    # Get the downloader and ebook generator types.
    parser = argparse.ArgumentParser()
    parser.add_argument('downloader', choices=DOWNLOADERS.keys())
    parser.add_argument('ebook_generator', choices=GENERATORS.keys())
    for transformation in TRANSFORMATIONS:
        parser.add_argument(
            transformation.ACTIVATION_COMMAND,
            dest=transformation.COMMAND_DESTINATION,
            action='store_true',
        )
    arguments, other_arguments = parser.parse_known_args()

    # Parse additional arguments for downloader.
    downloader_argument_parser = argparse.ArgumentParser()
    downloader_class = DOWNLOADERS[arguments.downloader]
    downloader_object = downloader_class()
    downloader_object.add_arguments(downloader_argument_parser)
    downloader_arguments, other_arguments = downloader_argument_parser.parse_known_args(other_arguments)

    # Parse additional arguments for ebook generator.
    generator_argument_parser = argparse.ArgumentParser()
    generator_class = GENERATORS[arguments.ebook_generator]
    generator_object = generator_class()
    generator_object.add_arguments(generator_argument_parser)
    generator_arguments, other_arguments = generator_argument_parser.parse_known_args(other_arguments)

    # Parse additional arguments for transformations.
    transformations = []

    arguments_dictionary = vars(arguments)
    for transformation in TRANSFORMATIONS:
        if transformation.COMMAND_DESTINATION not in arguments_dictionary:
            continue
        if arguments_dictionary[transformation.COMMAND_DESTINATION]:
            transformation_argument_parser = argparse.ArgumentParser()
            transformation_object = transformation()
            transformation_object.add_arguments(transformation_argument_parser)
            transformation_arguments, other_arguments = transformation_argument_parser.parse_known_args(other_arguments)
            transformations.append((transformation_object, transformation_arguments))

    # Use [downloader_object] to download ebook.
    ebook_data = downloader_object.download(downloader_arguments)

    # Apply all selecte transformations on downloaded ebook.
    for transformation, arguments in transformations:
        transformation.apply(arguments, ebook_data)

    # Use [generator_object] to generate ebook from [ebook_data].
    generator_object.generate(generator_arguments, ebook_data)