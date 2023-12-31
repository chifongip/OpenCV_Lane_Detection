# -*- coding: utf-8 -*-
# ROAD LANE DETECTION

import cv2
import matplotlib.pyplot as plt
import numpy as np


def gray(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def yellow_mask(image):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    yellow_lower = np.array([90, 140, 140])
    yellow_upper = np.array([110, 255, 255])
    mask_yellow = cv2.inRange(img_hsv, yellow_lower, yellow_upper)

    return mask_yellow


def white_mask(image):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    white_lower = np.array([0, 0, 150])
    white_upper = np.array([200, 150, 200])
    mask_white = cv2.inRange(img_hsv, white_lower, white_upper)

    return mask_white


def gauss(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

    # outline the strongest gradients in the image --> this is where lines in the image are


def canny(image):
    edges = cv2.Canny(image, 50, 100)
    return edges


def region(image):
    height, width = image.shape
    # isolate the gradients that correspond to the lane lines
    triangle = np.array([
                       [(0, height), (width//2, height//2), (width, height)]
                       ])
    # rect = np.array(
    #     [[(0, height//2), (width, height//2), (width, height), (0, height)]])
    # create a black image with the same dimensions as original image
    mask = np.zeros_like(image)
    # create a mask (triangle that isolates the region of interest in our image)
    mask = cv2.fillPoly(mask, triangle, 255)
    mask = cv2.bitwise_and(image, mask)
    return mask


def display_lines(image, lines):
    lines_image = np.zeros_like(image)
    # make sure array isn't empty
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line
            # draw lines on a black image
            cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return lines_image


def average(image, lines):
    left = []
    right = []

    if lines is not None:
        for line in lines:
            # print(line)
            x1, y1, x2, y2 = line.reshape(4)
            # fit line to points, return slope and y-int
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            # print(parameters)
            slope = parameters[0]
            y_int = parameters[1]
            # lines on the right have positive slope, and lines on the left have neg slope
            if slope < 0:
                left.append((slope, y_int))
            else:
                right.append((slope, y_int))
    if len(left) == 0:
        right_avg = np.average(right, axis=0)
        right_line = make_points(image, right_avg)
        return np.array([right_line])
    elif len(right) == 0:
        left_avg = np.average(left, axis=0)
        left_line = make_points(image, left_avg)
        return np.array([left_line])
    else:
        # takes average among all the columns (column0: slope, column1: y_int)
        right_avg = np.average(right, axis=0)
        left_avg = np.average(left, axis=0)
        # create lines based on averages calculates
        left_line = make_points(image, left_avg)
        right_line = make_points(image, right_avg)
        return np.array([left_line, right_line])


def make_points(image, average):
    # print(average)
    slope, y_int = average
    y1 = image.shape[0]
    # how long we want our lines to be --> 3/5 the size of the image
    y2 = int(y1 * (3/5))
    # determine algebraically
    x1 = int((y1 - y_int) // slope)
    x2 = int((y2 - y_int) // slope)
    return np.array([x1, y1, x2, y2])


def main():
    cap = cv2.VideoCapture("solidWhiteRight.mp4")

    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
    size = (frame_width, frame_height) 
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('output.mp4', fourcc, 30.0, size)

    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # detection
        # img_gray = gray(frame)
        # blur = gauss(img_gray)
        # edges = canny(blur)
        # seg = region(edges)
        
        # DRAWING LINES: (order of params) --> region of interest, bin size (P, theta), min intersections needed, placeholder array,
        # lines = cv2.HoughLinesP(seg, 2, np.pi/180, 30,
        #                         np.array([]), minLineLength=20, maxLineGap=5)
        # averaged_lines = average(frame, lines)
        # black_lines = display_lines(frame, averaged_lines)
        # # taking wighted sum of original image and lane lines image
        # lanes = cv2.addWeighted(frame, 0.8, black_lines, 1, 1)


        white = white_mask(frame)
        yellow = yellow_mask(frame)
        mask = cv2.bitwise_or(white, yellow)
        blur = gauss(mask)
        edges = canny(blur)
        seg = region(edges)

        lines = cv2.HoughLinesP(seg, 2, np.pi/180, 30,
                        np.array([]), minLineLength=20, maxLineGap=5)
        averaged_lines = average(frame, lines)
        black_lines = display_lines(frame, averaged_lines)
        # taking wighted sum of original image and lane lines image
        lanes = cv2.addWeighted(frame, 0.8, black_lines, 1, 1)

        cv2.imshow("result", lanes)
        # out.write(lanes)

        if cv2.waitKey(1) == ord('q'):
            break
    # out.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
