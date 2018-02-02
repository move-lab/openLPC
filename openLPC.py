import sys
import os
import argparse
from Lpc import Lpc


def main():

    lpc = Lpc()

    filepath = sys.argv[1]
    matrix_size = 1
    mode = 'image'

    if len(sys.argv) >= 3:
        matrix_size = int(sys.argv[2])

    if len(sys.argv) >= 4:
        mode = str(sys.argv[3])

    # TODO: implement proper arguments for CLI
    # parser = argparse.ArgumentParser(
    #     description='Censor license plates in image- and videofiles')
    # parser.add_argument(
    #     '--mode',
    #     dest='accumulate',
    #     action='store_const',
    #     const=sum,
    #     default=max,
    #     help='sum the integers (default: find the max)')

    # args = parser.parse_args()
    # print args.accumulate(args.integers)

    # switch modes
    if mode == 'image':
        lpc.config(
            matrix=matrix_size,
            multiplier=2,
            screen_view=False,
            debug=False,
            output='image',
            openALPR_config='openalpr.conf')
        lpc.censor_image(filepath)
    elif mode == 'imagestack':
        lpc.config(
            matrix=matrix_size,
            multiplier=2,
            screen_view=False,
            debug=False,
            output='image',
            openALPR_config='openalpr.conf')
        for fname in os.listdir(filepath):
            path = os.path.join(filepath, fname)
            if os.path.isdir(path):
                # skip directories
                continue
            lpc.censor_image(path)
    elif mode == 'video':
        lpc.config(
            matrix=matrix_size,
            multiplier=2,
            screen_view=False,
            debug=False,
            output='video',
            openALPR_config='openalpr.conf')
        lpc.censor_video(filepath)

    # unload openALPR
    lpc.unload()


if __name__ == "__main__":
    main()
