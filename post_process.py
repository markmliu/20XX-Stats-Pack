import sys
import matplotlib.pyplot as plt
# post-process data file to split matches, clean data, and upload graphs for each match
FRAMES_PER_SEC = 30
def clean_up_data(percent_series):
    # clean up each percentage series.  probably shouldn't believe a 
    # jump of more than 30, or a drop in percentage (unless the drop is to 0)
    # if either of these occurs, just keep the previous data
    # use prev_valid_point for reference in case bad percentage found.  
    # for example, if 48,5,5, 54 appears, we'll turn the 5 into a 48.  
    # on the other hand, we use prev_point to find when a stock has ended
    cleaned_data = []
    prev_valid_point = -1
    prev_point = -1
    stocks_started = 0
    for point in percent_series:
        if point > prev_valid_point + 50:
            cleaned_data.append(prev_valid_point)
        elif point < prev_valid_point and point != 0:
            cleaned_data.append(prev_valid_point)
        else:
            cleaned_data.append(point)
            prev_valid_point = point
        # if previous point was -1 and current point is 0, is start of a new stock
        if prev_point == -1 and point == 0:
            stocks_started += 1
        prev_point = point

    print "stocks started: " + str(stocks_started)
    return cleaned_data, stocks_started

def main(argv = sys.argv):
    data_file = argv[1]
    f = open(data_file,'r')
    # match_flag indicates whether data point occurs during actual match or not
    prev_match_flag = False
    num_games = 0
    # array of matches
    matches = []
    # array of winners
    winners = []
    cur_match = []
    prev_loc_1 = -1
    prev_loc_2 = -1
    cur_starting_frame = 0
    # this flag should be set to true when one percentage is at -1 and the other is not
    # once this flag is set, i should be watching for both percentages to drop to -1. 
    # then i know it was an actual match-ending death
    possible_match_ending_death_flag_1 = False
    possible_match_ending_death_flag_2 = False
    for line in f:
        frames_elapsed, loc_1, loc_2 = [int(x.strip()) for x in line.split(',')]
        # print frames_elapsed, loc_1, loc_2
        # if at least one location is valid, it's currently a valid match
        # if neither location is valid, invalid match
        if loc_1 == -1 and loc_2 == -1:
            cur_match_flag = False
        else:
            cur_match_flag = True
        # match just started
        if cur_match_flag == True and prev_match_flag == False:
            num_games += 1
            cur_match = []
            cur_match.append((0, loc_1, loc_2))
            cur_starting_frame = frames_elapsed
        # match just ended
        elif cur_match_flag == False and prev_match_flag == True:
            matches.append(cur_match)
            if possible_match_ending_death_flag_1 == True:
                print "Player 1 loses at frame: " + str(frames_elapsed)
                winners.append(2)
            elif possible_match_ending_death_flag_2 == True:
                print "Player 2 loses at frame: " + str(frames_elapsed)
                winners.append(1)
            # what if we didn't get info from that???
            # i guess put 0 there for no meaning we don't know who won.
            # can try to figure out later, when segmenting by stock
                winners.append(0)
            possible_match_ending_death_flag_1 = False
            possible_match_ending_death_flag_2 = False            

        # in middle of the match
        elif cur_match_flag == True:
            relative_frames_elapsed = frames_elapsed - cur_starting_frame
            # add interpolated points
            cur_match.append((relative_frames_elapsed - 1 ,prev_loc_1, prev_loc_2))
            # add real point
            cur_match.append((relative_frames_elapsed, loc_1, loc_2))
            if loc_1 == -1 and loc_2 != -1:
                possible_match_ending_death_flag_1 = True
            elif loc_1 != -1 and loc_2 == -1:
                possible_match_ending_death_flag_2 = True
            else:
                possible_match_ending_death_flag_1 = False
                possible_match_ending_death_flag_2 = False
        prev_match_flag = cur_match_flag
        prev_loc_1 = loc_1
        prev_loc_2 = loc_2
    print "Number of games: " + str(num_games)
    # print "matches: " + str(matches)
    # video now separated into matches
    # plot each match
    fig = plt.figure(1)
    num_matches = len(matches)
    for idx, match in enumerate(matches):
        # print "match: " + str(match)
        time_series =  [float(x[0])/FRAMES_PER_SEC for x in match]
        percent_series_1 = [x[1] for x in match]
        percent_series_2 = [x[2] for x in match]
        # print "percent_series_1: " + str(percent_series_1)
        cleaned_series_1, stocks_started_1 = clean_up_data(percent_series_1)
        cleaned_series_2, stocks_started_2 = clean_up_data(percent_series_2)
        print "cleaned_series_1: " + str(cleaned_series_1)
        print "cleaned_series_2: " + str(cleaned_series_2)
        winner = winners[idx]
        if winner == 0:
            if stocks_started_1 < stocks_started_2:
                winner = 1
            if stocks_started_2 < stocks_started_1:
                winner = 2

        asdf = plt.subplot(num_matches, 1, idx+1)
        plt.plot(time_series, cleaned_series_1, 'b-')
        plt.plot(time_series, cleaned_series_2, 'r-')
        asdf.set_title('Game ' + str(idx+1) + ": Winner is Player " + str(winner))
    fig.subplots_adjust(hspace=.5)
    plt.show()
    fig.savefig('temp.png', dpi = fig.dpi)
if __name__ == "__main__":
    main()
