import pandas as pd
import cv2 as cv


# url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
# table = pd.read_html(url)[0]
# table.columns = table.columns.droplevel()

# cap = cv2.VideoCapture(0)
# resolutions = {}

# for index, row in table[["W", "H"]].iterrows():
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     resolutions[str(width)+"x"+str(height)] = "OK"

# print(resolutions)

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
print("[turret contoller] Set Video resolution: " + str(cap.get(cv.CAP_PROP_FRAME_WIDTH)) + " x " + str(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
print("[turret contoller] Video capture setup complete")

cap.release()