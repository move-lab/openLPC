import cv2
import sys
import os
import datetime
import numpy as np
from openalpr import Alpr


class Lpc(object):
    """docstring for Lpc."""

    gl_filepath = None
    gl_original_image = None
    gl_matrix = 1
    gl_multiplier = 2
    gl_screen_view = False
    gl_debug = False
    gl_output = 'image'
    gl_counter = 0

    def __init__(self):
        super(Lpc, self).__init__()

        # region currently set to EU (Europe).
        # Other regions include SG (Singapore) and US
        self.alpr = Alpr('eu', 'openalpr.conf', 'runtime_data')

        # Make sure the library loaded before continuing.
        if not self.alpr.is_loaded():
            print('Error loading OpenALPR')
            sys.exit(1)

        # Optionally, provide the library with a region for pattern matching.
        # Example: md for maryland
        #self.alpr.set_default_region('eu')

    def config(self,
               matrix=1,
               multiplier=2,
               screen_view=False,
               debug=False,
               output='image',
               openALPR_config='openalpr.conf'):
        self.gl_matrix = matrix
        self.gl_multiplier = multiplier
        self.gl_screen_view = screen_view
        self.gl_debug = debug
        self.gl_output = output
        self.alpr = Alpr('eu', openALPR_config, 'runtime_data')

        if self.gl_debug:
            print '--------------------------------'
            print '-----------DEBUG MODE-----------'
            print '--------------------------------'

    def unload(self):
        # Call when completely done to release memory
        self.alpr.unload()

    def __save_file(self, ndarray_image, frame=''):
        filename_without_ext, file_extension = os.path.splitext(
            os.path.basename(self.gl_filepath))

        if len(str(frame)) > 0:
            file_extension = '.png'

        if not os.path.exists(
                os.path.dirname(self.gl_filepath) + '/censored/'):
            os.makedirs(os.path.dirname(self.gl_filepath) + '/censored/')

        save_path = os.path.dirname(
            self.gl_filepath) + '/censored/' + filename_without_ext + '_' + str(
                self.gl_matrix) + 'x' + str(
                    self.gl_matrix) + '_' + str(frame) + '_censored_' + str(
                        datetime.datetime.now().strftime(
                            '%Y-%m-%d_%H-%M-%S')) + file_extension

        cv2.imwrite(save_path, ndarray_image)
        print 'saved file in: ' + save_path
        self.__write_log(save_path)

    def __write_log(self, filepath):
        if os.path.exists('./logs/log.txt'):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        log = open('./logs/log.txt', append_write)
        log.write('-------------------------------' + '\n')
        log.write("Date:            " + str(datetime.datetime.now()) + '\n')
        log.write("File:            " + self.gl_filepath + '\n')
        log.write("Censored File:   " + filepath + '\n')
        log.write("Matrix Size:     " + str(self.gl_matrix) + '\n')
        log.write("Multiplier:      " + str(self.gl_multiplier) + '\n')
        log.write("Output:          " + self.gl_output + '\n')
        log.write("Total LPs found: " + str(self.gl_counter) + '\n')
        log.write("ScrennView:      " + str(self.gl_screen_view) + '\n')
        log.write("Debug:           " + str(self.gl_debug) + '\n')
        log.write('-------------------------------' + '\n')
        log.close()

        print 'logfile at: ./logs/log.txt'

    def __search_and_censor(self, ndarray_image):
        if not ndarray_image.size:
            print 'file does not exist'
            sys.exit(1)

        analyzed_file = self.alpr.recognize_ndarray(ndarray_image)

        if not analyzed_file['results']:
            print 'No license plate(s) detected | total: ' + str(
                self.gl_counter)
            # sys.exit(1)
        if analyzed_file['results']:
            self.gl_counter = self.gl_counter + len(analyzed_file['results'])
            print 'found ' + str(len(analyzed_file['results'])
                                 ) + ' licenece plate(s) | total: ' + str(
                                     self.gl_counter)

        # loop through the results
        for result in analyzed_file['results']:
            # x,y coordinates of opposite corners of license plate
            x1 = result['coordinates'][0]['x']
            y1 = result['coordinates'][0]['y']
            x2 = result['coordinates'][2]['x']
            y2 = result['coordinates'][2]['y']

            true_x1 = x1 / self.gl_multiplier
            true_y1 = y1 / self.gl_multiplier
            true_x2 = x2 / self.gl_multiplier
            true_y2 = y2 / self.gl_multiplier

            # blurred plate
            plate = self.gl_original_image[true_y1:true_y2, true_x1:true_x2]
            blured_plate = cv2.GaussianBlur(plate, (19, 19), 4, 4, 0)
            self.gl_original_image[true_y1:true_y2, true_x1:
                                   true_x2] = blured_plate

            if self.gl_debug:
                # pink bar
                cv2.rectangle(self.gl_original_image, (true_x1, true_y1),
                              (true_x2, true_y2), (255, 0, 251), -1)

        return self.gl_original_image

    # TODO: should not return resized image but true coordinates where to censore the image
    def __tile_and_merge(self, ndarray_image, matrix=1):
        censored_tiles = []

        if not ndarray_image.size:
            print 'file does not exist'
            sys.exit(1)

        height = int(ndarray_image.shape[0] / self.gl_matrix)
        width = int(ndarray_image.shape[1] / self.gl_matrix)

        print 'tile image in ' + str(self.gl_matrix) + 'x' + str(
            self.gl_matrix) + ' matrix'
        for row in range(self.gl_matrix):
            for col in range(self.gl_matrix):
                y0 = row * height
                y1 = y0 + height
                x0 = col * width
                x1 = x0 + width

                print 'start censoring tile ' + str(row) + 'x' + str(col)
                censored_tile = self.__search_and_censor(
                    ndarray_image[y0:y1, x0:x1])
                censored_tiles.append(censored_tile)

        print 'merging tiles'
        tile_row_array = []
        tile_row = []
        count = 0
        for i, c_tile in enumerate(censored_tiles):
            count += 1
            tile_row_array.append(c_tile)

            if (count == self.gl_matrix):
                tmp_row = np.concatenate(tile_row_array, axis=1)
                tile_row.append(tmp_row)
                tile_row_array = []
                count = 0

        return np.concatenate(tile_row, axis=0)

    def censor_image(self, filepath, frame=''):
        if not type(filepath) is np.ndarray:
            self.gl_filepath = filepath
            img = cv2.imread(filepath)
        else:
            img = filepath

        height = int(img.shape[0])
        width = int(img.shape[1])
        self.gl_original_image = img

        print 'resize image (x' + str(
            self.gl_multiplier) + '):' + self.gl_filepath + ' ' + str(frame)
        img = cv2.resize(
            img, (width * self.gl_multiplier, height * self.gl_multiplier))
        print 'new image size is: ' + str(int(img.shape[1])) + 'x' + str(
            int(img.shape[0])) + ' px'

        if self.gl_matrix == 1:
            merged_img = self.__search_and_censor(img)
        elif self.gl_matrix > 1:
            merged_img = self.__tile_and_merge(img, self.gl_matrix)

        if self.gl_output == 'image':
            self.__save_file(merged_img, frame)

            # show image on screen if gl_screen_view is true
            if self.gl_screen_view:
                cv2.namedWindow('ImageWindow', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('ImageWindow', np.size(merged_img, 1),
                                 np.size(merged_img, 0))
                cv2.imshow('ImageWindow', merged_img)
                cv2.waitKey(0)
        elif self.gl_output == 'video':
            return merged_img

    def censor_video(self, filepath):
        self.gl_filepath = filepath
        cap = cv2.VideoCapture(filepath)

        # get video file information
        width = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
        framerate = cap.get(cv2.cv.CV_CAP_PROP_FPS)

        # check if censored folder exists
        if not os.path.exists(
                os.path.dirname(self.gl_filepath) + '/censored/'):
            os.makedirs(os.path.dirname(self.gl_filepath) + '/censored/')

        # build output path/name
        filename_without_ext = os.path.splitext(
            os.path.basename(self.gl_filepath))[0]
        save_path = os.path.dirname(
            self.gl_filepath
        ) + '/censored/' + filename_without_ext + '_' + str(
            self.gl_matrix) + 'x' + str(self.gl_matrix) + '_censored_' + str(
                datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + '.avi'

        # Define the codec and create VideoWriter object
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter(save_path, fourcc, framerate,
                              (int(width), int(height)))

        while not cap.isOpened():
            cap = cv2.VideoCapture(filepath)
            cv2.waitKey(1000)
            print 'Wait for the header'

        pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
        while True:
            flag, frame = cap.read()
            if flag:
                # The frame is ready and already captured
                pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

                # pass frame to image censoring method
                censored_frame = self.censor_image(frame, pos_frame)

                # switch between video file and image stack
                if self.gl_output == 'video':
                    out.write(censored_frame)

                if self.gl_output == 'image':
                    self.__save_file(censored_frame, pos_frame)

                # show frame on screen if gl_screen_view is true
                if self.gl_screen_view:
                    cv2.namedWindow('VideoWindow', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('VideoWindow', np.size(censored_frame, 1),
                                     np.size(censored_frame, 0))
                    cv2.imshow('VideoWindow', censored_frame)
            else:
                # The next frame is not ready, so we try to read it again
                cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame - 1)
                print 'frame is not ready'
                # It is better to wait for a while for the next frame to be ready
                cv2.waitKey(1000)

            if cv2.waitKey(10) == 27:
                break
            if cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == cap.get(
                    cv2.cv.CV_CAP_PROP_FRAME_COUNT):
                # If the number of captured frames is equal
                # to the total number of frames, we stop
                break

        # release // cleanup
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        self.__write_log(save_path)
        print 'total license plates counted: ' + str(self.gl_counter)
        print 'saved censored video file in: ' + save_path
