import sys
import os
import argparse
from Lpc import Lpc


def main():

    lpc = Lpc()

    parser = argparse.ArgumentParser(
        description='Censor license plates in image- and videofiles')
    parser.add_argument(
        '-msize',
        action='store',
        default=1,
        dest='matrix_size',
        help='Size of the tiling matrix',
        type=int)
    parser.add_argument(
        '-multiplier',
        action='store',
        default=2,
        dest='multiplier',
        help='Image/Frame mulitplied by given value for detection accuracy',
        type=int)
    parser.add_argument(
        '-path',
        action='store',
        dest='filepath',
        help='path to the file (for imagestack: path to the folder)',
        type=str,
        required=True)
    parser.add_argument(
        '-pattern',
        action='store',
        default='eu',
        dest='pattern',
        help=
        'pattern for licnese plate matching (see ./runtime_data/postprocess/)',
        type=str)
    parser.add_argument(
        '-mode',
        action='store',
        default='image',
        dest='mode',
        help='modes (image, imagestack, video)',
        type=str,
        required=True)
    parser.add_argument(
        '-output',
        action='store',
        default='image',
        dest='output',
        help='output format (video, image)',
        type=str)
    parser.add_argument(
        '-show',
        action='store_true',
        default=False,
        dest='screen_view',
        help='Display the output with cv2.imshow (screen required)')
    parser.add_argument(
        '-debug',
        action='store_true',
        default=False,
        dest='debug',
        help='Debug mode (pink bar instead of blurred plate)')

    args = parser.parse_args()

    # switch modes
    if args.mode == 'image':
        lpc.config(
            matrix=args.matrix_size,
            multiplier=args.multiplier,
            pattern=args.pattern,
            screen_view=args.screen_view,
            debug=args.debug,
            output=args.output,
            openALPR_config='openalpr.conf')
        lpc.censor_image(args.filepath)
    elif args.mode == 'imagestack':
        lpc.config(
            matrix=args.matrix_size,
            multiplier=args.multiplier,
            pattern=args.pattern,
            screen_view=args.screen_view,
            debug=args.debug,
            output=args.output,
            openALPR_config='openalpr.conf')
        for fname in os.listdir(args.filepath):
            path = os.path.join(args.filepath, fname)
            if os.path.isdir(path):
                # skip directories
                continue
            lpc.censor_image(path)
    elif args.mode == 'video':
        lpc.config(
            matrix=args.matrix_size,
            multiplier=args.multiplier,
            pattern=args.pattern,
            screen_view=args.screen_view,
            debug=args.debug,
            output=args.output,
            openALPR_config='openalpr.conf')
        lpc.censor_video(args.filepath)

    # unload openALPR
    lpc.unload()


if __name__ == "__main__":
    main()
