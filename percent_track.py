import matplotlib.pyplot as plt
import numpy as np
import cv2
# hardcoded size of zero template...
WIDTH = 25
HEIGHT = 28
DIFF_METHOD = 'cv2.TM_CCOEFF_NORMED'
# include a buffer for candidate size, augment each side by 5 pixels to account for shakiness
BUFFER_SIZE = 5
def load_resources():
    # grab resources and put them into number_templates
    number_templates = []
    for i in range(0,10):
        number_templates.append(cv2.imread('smash_resources/' + str(i) + '.png', 1))
    return number_templates
        
def compare_with_previous(img1, img2, locations_found):
    # compare img1 with img2 and see if anything changed significantly in locations_found
    # if diff falls below diff_threshold, then percentage has changed
    # don't necessarily need to include buffer for this
    diff_threshold = 0.9
    for location in locations_found:
        # location[0] is horizontal, location[1] is vertical 
        # but you need to index into image vertically then horizontally
        percent_1 = img1[location[1]:location[1] + HEIGHT, location[0]:location[0] + WIDTH]
        percent_2 = img2[location[1]:location[1] + HEIGHT, location[0]:location[0] + WIDTH]
        diff = cv2.matchTemplate(percent_1, percent_2, eval(DIFF_METHOD))[0][0]
        # print "diff: " + str(diff)
        if diff < diff_threshold:
            return False
    return True

def match_to_number(candidate, number_templates):
    # try to match candidate to each image in number_templates
    # candidate should be bigger than number to allow room for moving around
    prev_val = float("-inf")
    max_idx = -1
    max_val = prev_val
    for index, number in enumerate(number_templates):
        #cv2.imshow('compare1', candidate)
        #cv2.imshow('compare2', number)
        cur_diff = cv2.matchTemplate(candidate, number, eval(DIFF_METHOD))
        _, cur_val, _, _ = cv2.minMaxLoc(cur_diff)
        #print "cur_diff: " + str(cur_diff)
        #cv2.waitKey(0)
        if cur_val > max_val:
            max_val = cur_val
            max_idx = index
    # if there's something reasonably close, return that...
    if max_val > 0.5:
        return max_idx
    # otherwise return -1
    return -1

def extend_locations(locations):
    # move each top_left up and to the left by 5 pixels each.  then
    # for each zero location found, grab two boxes to the right
    extended_locations = []
    for location in locations:
        extended_locations.append((location[0] - BUFFER_SIZE, location[1] - BUFFER_SIZE))
        extended_locations.append((location[0] - WIDTH - BUFFER_SIZE, location[1] - BUFFER_SIZE))
        extended_locations.append((location[0] - (2 * WIDTH) - BUFFER_SIZE, location[1] - BUFFER_SIZE))
    return extended_locations    

def calculate_total_percent(ones, tens, hundreds):
    # calculate actual value from three digits...
    # return -1 if percentage does not make sense.
    if ones == -1:
        return -1
    total = ones;
    if hundreds != -1:
        total += hundreds * 100
    if tens != -1:
        total += tens * 10
    return total

def clean_up_data(percent_series):
    # clean up the percentage series.  probably shouldn't believe a jump of more than 30, or a drop in percentage (unless the drop is to 0)
    # if either of these occurs, just keep the previous data
    cleaned_data = []
    prev_valid_point = -1
    for point in percent_series:
        if point > prev_valid_point + 30:
            cleaned_data.append(prev_valid_point)
        elif point < prev_valid_point and point != 0:
            cleaned_data.append(prev_valid_point)
        else:
            cleaned_data.append(point)
            prev_valid_point = point
    return cleaned_data

def main():
    # if threshold greater than this, its a match
    # maybe should just take top two instead..
    threshold = 0.95

    cap = cv2.VideoCapture('falconDitto.mp4')
    # hardcode to find start of match now...should be able to find this programmatically
    for i in range(1, 1400):
        cap.read()    
    ret, frame = cap.read()

    # find where percentages are using template matching
    # load the zero template, use matchTemplate to find spots which are closest to it
    number_templates = load_resources()
    zero = number_templates[0]
    diff = cv2.matchTemplate(frame, zero, eval(DIFF_METHOD))
    # cv2.imshow('diff', diff)
    # locations_found is the places where we think the zeros are
    # its an list of x,y pairs
    locations_found_unzipped = np.where(diff > threshold)
    locations_found = zip(locations_found_unzipped[1], locations_found_unzipped[0])
    extended_locations_found = extend_locations(locations_found)
    # draw a rectangle around each location, using hardcoded values of size of percents
    for top_left in extended_locations_found:
        print "top left: " + str(top_left)
        bottom_right = (top_left[0] + WIDTH + (2 * BUFFER_SIZE), top_left[1] + HEIGHT + (2 * BUFFER_SIZE))
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)
    cv2.imshow('frame', frame)
    cv2.waitKey(0)

    _, previous_frame = cap.read()
    prev_stability = False
    frames_elapsed = 0
    percent_series_1 = []
    percent_series_2 = []
    time_series = []
    while(cap.isOpened()):
        ret ,frame = cap.read()
        frames_elapsed += 1
        if ret == True:
            # cv2.imshow('frame', frame)
            if not compare_with_previous(previous_frame, frame, locations_found):
                # percentage will shake around, making it unstable
                # wait until stable again to look for difference between it and previous one
                cur_stability = False
            else: 
                cur_stability = True
            # if we've stabilized, check both percentages to see whats changed
            if cur_stability and not prev_stability:
                best_guesses = []
                for idx, location in enumerate(extended_locations_found):
                    candidate = frame[location[1]:location[1] + HEIGHT + (2 * BUFFER_SIZE), location[0]:location[0] + WIDTH + (2 * BUFFER_SIZE)]
                    # cv2.imshow('candidate', candidate)
                    # cv2.waitKey(0)
                    best_guess = match_to_number(candidate, number_templates)
                    # print "location: " + str(idx)
                    # print "guessed percent: " + str(best_guess)
                    best_guesses.append(best_guess)
                percent_1 = calculate_total_percent(best_guesses[0], best_guesses[1], best_guesses[2])
                percent_2 = calculate_total_percent(best_guesses[3], best_guesses[4], best_guesses[5])
                time_elapsed = float(frames_elapsed)/60
                print "Location 1: " + str(percent_1) + " Location 2: " + str(percent_2) + " at time " + str(time_elapsed)
                percent_series_1.append(percent_1)
                percent_series_2.append(percent_2)
                time_series.append(time_elapsed)
                #cv2.waitKey(0)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break   
            prev_stability = cur_stability
        else:
            break
        previous_frame = frame
    # loops has ended, clean up the data now?
    cleaned_1 = clean_up_data(percent_series_1)
    cleaned_2 = clean_up_data(percent_series_2)
    plt.plot(time_series, cleaned_1, 'b-')
    # plt.plot(time_series, percent_series_1, 'bo')
    plt.plot(time_series, cleaned_2, 'r-')
    # plt.plot(time_series, percent_series_2, 'ro')
    plt.show()
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()
