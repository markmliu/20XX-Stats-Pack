import sys

# post-process data file to split matches, clean data, and upload graphs for each match

def clean_up_data(match):
    # clean up the percentage series.  probably shouldn't believe a jump of more than 30, or a drop in percentage (unless the drop is to 0)
    # if either of these occurs, just keep the previous data
    cleaned_data_1 = []
    cleaned_data_2 = []
    prev_valid_point_1 = -1
    prev_valid_point_2 = -1
    for frame, point_1, point_2 in percent_series:
        if point_1 > prev_valid_point_1 + 50:
            cleaned_data_1.append(prev_valid_point_1)
        elif point_1 < prev_valid_point_1 and point_1 != 0:
            cleaned_data_1.append(prev_valid_point_1)
        else:
            cleaned_data_1.append(point_1)
            prev_valid_point_1 = point_1

        if point_2 > prev_valid_point_2 + 50:
            cleaned_data_2.append(prev_valid_point_2)
        elif point_2 < prev_valid_point_2 and point_2 != 0:
            cleaned_data_2.append(prev_valid_point_2)
        else:
            cleaned_data_2.append(point_2)
            prev_valid_point_2 = point_2


    return cleaned_data_1, cleaned_data_2


def main(argv = sys.argv):
    data_file = argv[1]
    f = open(data_file,'r')
    # match_flag indicates whether data point occurs during actual match or not
    prev_match_flag = False
    num_games = 0
    # array of matches
    matches = []
    cur_match = []
    for line in f:
        frames_elapsed, loc_1, loc_2 = [x.strip() for x in line.split(',')]
        # print frames_elapsed, loc_1, loc_2
        # if at least one location is valid, it's currently a valid match
        # if neither location is valid, invalid match
        if loc_1 == "-1" and loc_2 == "-1":
            cur_match_flag = False
        else:
            cur_match_flag = True
        # match just started
        if cur_match_flag == True and prev_match_flag == False:
            num_games += 1
            cur_match = []
            cur_match.append((frames_elapsed, loc_1, loc_2))
        # match just ended
        elif cur_match_flag == False and prev_match_flag == True:
            matches.append(cur_match)
        elif cur_match_flag == True:
            cur_match.append((frames_elapsed, loc_1, loc_2))
        prev_match_flag = cur_match_flag
    print "Number of games: " + str(num_games)
    print "matches: " + str(matches)
    # video now separated into matches
    for match in matches:
        clean_up_data(match)
if __name__ == "__main__":
    main()
