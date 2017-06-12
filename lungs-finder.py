import os
import sys
import numpy as np
import cv2

try:
    __import__("imp").find_module("dicompylercore")
    from dicompylercore import dicomparser

    dicom_support = True
except ImportError:
    dicom_support = False
    print("\"dicompylercore\" library was not found. \"lungs-finder\" works without dicom support.")


def find_left_lung(image):
    left_lung = cv2.CascadeClassifier("left_lung.xml")
    found = left_lung.detectMultiScale(image, 1.3, 5)

    if len(found) > 0:
        find_left_lung.detect += 1
        x, y, width, height = found[0]
        cv2.rectangle(image, (x, y), (x + width, y + height), (255, 0, 0), 2)
    find_left_lung.overall += 1

    return image


def main(argv):
    if len(argv) < 4:
        print("Usage: lungs-finder.py \"path_to_folder\" \"position_to_start\" \"histogram_equalization\".")
        exit(1)

    path_to_folder = argv[1]
    position_to_start = int(argv[2])

    if argv[3].lower() in ["true", "1"]:
        histogram_equalization = True
    else:
        histogram_equalization = False

    find_left_lung.detect = 0
    find_left_lung.overall = 0

    walks = list(os.walk(path_to_folder))
    i = 0
    k = 1

    while i < len(walks):
        path, directories, files = walks[i]
        files = [file for file in files if not file[0] == "."]
        j = 0

        while j < len(files):
            file = files[j]

            if k < position_to_start:
                k += 1
                j += 1
            else:
                _, extension = os.path.splitext(file)

                if extension == ".dcm" and dicom_support:
                    parsed = dicomparser.DicomParser(path + os.sep + file)
                    image = np.array(parsed.GetImage(), dtype=np.uint8)

                    if parsed.GetImageData()["photometricinterpretation"] == "MONOCHROME1":
                        image = 255 - image

                    if histogram_equalization:
                        image = cv2.equalizeHist(image)
                        image = cv2.medianBlur(image, 3)

                elif extension in [".bmp", ".pbm", ".pgm", ".ppm", ".sr", ".ras", ".jpeg", ".jpg", ".jpe", ".png",
                                   ".tiff", ".tif"]:
                    image = cv2.imread(path + os.sep + file, 0)

                    if histogram_equalization:
                        image = cv2.equalizeHist(image)
                        image = cv2.medianBlur(image, 3)
                else:
                    j += 1
                    continue

                if image.shape[0] > image.shape[1]:
                    height = 512
                    width = int(height / image.shape[0] * image.shape[1])
                else:
                    width = 512
                    height = int(width / image.shape[1] * image.shape[0])

                scaled_image = cv2.resize(image, (width, height))
                cv2.imshow("lungs-finder", find_left_lung(scaled_image))
                code = cv2.waitKey(0)

                while code not in [2, 3, 27, 32]:
                    code = cv2.waitKey(0)

                if code == 27:
                    print("File number: " + str(j + 1) + ".")
                    print("Detects: " + str(find_left_lung.detect) + ".")
                    print("Overall: " + str(find_left_lung.overall) + ".")
                    print("Recognition rate: " + str(find_left_lung.detect / find_left_lung.overall * 100) + "%.")
                    exit(0)
                elif code in [3, 32]:
                    j += 1
                else:
                    if j > 0:
                        j -= 1
                    else:
                        if i > 0:
                            i -= 2
        i += 1

    print("Detects: " + str(find_left_lung.detect) + ".")
    print("Overall: " + str(find_left_lung.overall) + ".")
    print("Recognition rate: " + str(find_left_lung.detect / find_left_lung.overall * 100) + "%.")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
