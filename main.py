import numpy as np
import cv2
from time import sleep

def centroid(x, y, w, h):
    '''Get center of element'''
    x_f = int(w/2)
    y_f = int(h/2)
    c_x = x + x_f
    c_y = y + y_f
    return c_x, c_y

def create_roi(event, x, y, flags, params):
	'''Draw a ROI over the road to better analysis'''
	if event == cv2.EVENT_LBUTTONDOWN:
		print("Início")
		roi_start.append((x, y))
	if event == cv2.EVENT_LBUTTONUP:
		print("Final")
		roi_end.append((x, y))


MIN_WIDTH = 80
MIN_HEIGHT = 80
DELAY = 60
LINE_POS = 450

roi_start = []
roi_end = []
detected = []

cv2.namedWindow("resize")
cv2.setMouseCallback("resize", create_roi)


def main():
    cars = 0
    '''Main function'''
    cap = cv2.VideoCapture("gopro-inclinada.mp4")
    backSub = cv2.createBackgroundSubtractorKNN()
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        tempo = float(1/DELAY)
        sleep(tempo)
        resize = cv2.resize(frame, None, fx=0.5, fy=0.5)

        if (roi_start and roi_end):
        	'''Get each value to be clear'''
	        y_start = roi_start[0][1]
	        y_end = roi_end[0][1]
	        x_start = roi_start[0][0]
	        x_end = roi_end[0][0]

	        # print("image[{}:{}, {}:{}]".format(y_start, y_end, x_start, x_end))

	        roi_road = resize[y_start : y_end, x_start : x_end]

	        
	        
        	cv2.rectangle(resize, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

	        gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)
	        blur = cv2.GaussianBlur(gray, (3, 3), 5)
	        frame_sub_b = backSub.apply(blur)

	        dilation = cv2.dilate(frame_sub_b, np.ones((5, 5)))
	        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
	        closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)

	        contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	        cv2.line(roi_road, (0, int((y_end-y_start)/2)), (x_end, int((y_end-y_start)/2)), (0, 0, 255), 2)
	        
	        for (i, contour) in enumerate(contours):
	            (x, y, w, h) = cv2.boundingRect(contour)
	            validate = (w >= MIN_WIDTH) and (h >= MIN_HEIGHT)
	            if not validate:
	                continue
	            center = centroid(x, y, w, h)
	            detected.append(center)
	            
	            cv2.circle(resize, center, 2, (0, 0, 255), -1)

	            cv2.rectangle(resize, (x, y), (x+w, y+h), (0, 0, 255), 2)

	            for (x, y) in detected:
	                if (y < (LINE_POS + 3)) and (y >= (LINE_POS - 3) and (x < 900)):
	                    cars += 1
	                    cv2.line(resize, (x_start, int((y_end - y_start)/2) + y_start), (x_end, int((y_end - y_start)/2) + y_start), (255, 0, 255), 3)
	                    detected.remove((x, y))
	                    print("Cars detected {}" .format(cars))

	        cv2.putText(resize, "Cars count: "+str(cars), (400, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 5)
        	
        	cv2.imshow("roi image", roi_road)


        cv2.imshow("resize", resize)
        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()