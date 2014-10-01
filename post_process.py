import sys
import os
import matplotlib.pyplot as plt

# post-process data file to split matches, clean data, and upload graphs for each match
# TODO: This is hard coded now, but we can retrieve in percent_track and pass along to this script
FRAMES_PER_SEC = 30

def calculate_control(time_series, percent_series_1, percent_series_2):
    # figure out who has "control" of a match
    # controlled_time refers to the amount of time player was the last player to deal damage
    res = {}
    prev_percent_1 = 0
    prev_percent_2 = 0
    prev_time = 0
    controlled_time_1 = 0
    controlled_time_2 = 0
    # array of damage done by each combo for each player
    combo_damage_1 = []
    combo_damage_2 = []
    cur_combo_damage_1 = 0
    cur_combo_damage_2 = 0
    # number of openings player 1 got
    num_openings_1 = 0
    num_openings_2 = 0
    # who was controlling the match at previous time step
    prev_controller = 0
    for time, percent_1, percent_2 in zip(time_series, percent_series_1, percent_series_2):
        elapsed_time = time - prev_time
        if percent_1 > prev_percent_1 and percent_2 == prev_percent_2:
            # player 1 took more damage while player 2 did not
            # so player 2 controlled time should be incremented and
            # player 2 combo damage should increase
            controlled_time_2 += elapsed_time
            prev_controller = 2
            cur_combo_damage_2 += (percent_1 - prev_percent_1)
            if (cur_combo_damage_1 != 0):
                # player 1's combo is now ending then
                print "player 1's combo ending at " + str(cur_combo_damage_1) + " percent "
                combo_damage_1.append(cur_combo_damage_1)
                cur_combo_damage_1 = 0
                num_openings_1 += 1
        elif percent_2 > prev_percent_2 and percent_1 == prev_percent_1:
            # player 2 took more damage while player 1 did not
            controlled_time_1 += elapsed_time
            prev_controller = 1
            cur_combo_damage_1 += (percent_2 - prev_percent_2)
            if (cur_combo_damage_2 != 0):
                # combo has ended
                print "player 2's combo ending at " + str(cur_combo_damage_2) + " percent "
                combo_damage_2.append(cur_combo_damage_2)
                cur_combo_damage_2 = 0
                num_openings_2 += 1
        elif percent_1 == prev_percent_1 and percent_2 == prev_percent_2:
            # nothing's changed
            if prev_controller == 1:
                controlled_time_1 += elapsed_time
            elif prev_controller == 2:
                controlled_time_2 += elapsed_time
        elif percent_1 > prev_percent_1 and percent_2 > prev_percent_2:
            # both combos should end and both players should lose control
            if cur_combo_damage_1 > 0:
                combo_damage_1.append(cur_combo_damage_1)
            if cur_combo_damage_2 > 0:
                combo_damage_2.append(cur_combo_damage_2)
            cur_combo_damage_1 = 0
            cur_combo_damage_2 = 0
            prev_controller = 0
        else:
            # only other case is one of the percentages decreased, meaning someone was KO'ed.  let's assume
            # control is reset in this situation, so neither player is controlling
            if cur_combo_damage_1 > 0:
                combo_damage_1.append(cur_combo_damage_1)
            if cur_combo_damage_2 > 0:
                combo_damage_2.append(cur_combo_damage_2)
            cur_combo_damage_1 = 0
            cur_combo_damage_2 = 0
            prev_controller = 0
            # how to reward low percent gimps without overdoing it?
            # nothing for now
        prev_percent_1 = percent_1
        prev_percent_2 = percent_2
        prev_time = time
    res['controlled_time_1'] = controlled_time_1
    res['controlled_time_2'] = controlled_time_2
    res['combo_damage_1'] = combo_damage_1
    res['combo_damage_2'] = combo_damage_2
    res['average_combo_length_1'] = sum(combo_damage_1)/float(len(combo_damage_1))
    res['average_combo_length_2'] = sum(combo_damage_2)/float(len(combo_damage_2))
    res['num_openings_1'] = num_openings_1
    res['num_openings_2'] = num_openings_2
    return res

        
        

def clean_up_data(percent_series):
    # clean up each percentage series.  probably shouldn't believe a 
    # jump of more than 30, or a drop in percentage (unless the drop is to 0)
    # if either of these occurs, just keep the previous data
    # use prev_valid_point for reference in case bad percentage found.  
    # for example, if 48,5,5, 54 appears, we'll turn the 5 into a 48.  
    # on the other hand, we use prev_point to find when a stock has ended
    # also return the number of stocks which were STARTED by the player
    # since we don't necessarily know how many ended just from the percent_series
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

def split_data_by_matches(f):
    # takes raw csv and splits by matches.  also adds interpolated points
    # data is returned in matches and winners lists
    # match_flag indicates whether data point occurs during actual match or not
    prev_match_flag = False
    num_games = 0
    # array of matches
    matches = []
    # array of winners
    winners = []
    cur_match = []
    # last percentage that appeared at location 1/2
    prev_loc_1 = -1
    prev_loc_2 = -1
    # starting frame of the current match
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
            # if we didn't get info from this, put 0 there for now
            # can try to figure out later when counting how many stocks were taken
            else:
                winners.append(0)
            possible_match_ending_death_flag_1 = False
            possible_match_ending_death_flag_2 = False            

        # in middle of the match
        elif cur_match_flag == True:
            relative_frames_elapsed = frames_elapsed - cur_starting_frame
            # add interpolated point
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
    return matches, winners

def main(argv = sys.argv):
    data_file = argv[1]
    f = open(data_file,'r')
    matches, winners = split_data_by_matches(f)
    f.close()
    # plot each match
    percent_fig = plt.figure(1)

    num_matches = len(matches)
    wins_1 = 0
    wins_2 = 0
    max_match_length = -1

    # calculate longest match
    for match in matches:
        time_series = [float(x[0])/FRAMES_PER_SEC for x in match]
        if time_series[-1] > max_match_length:
            max_match_length = time_series[-1]
        
    for idx, match in enumerate(matches):
        # print "match: " + str(match)
        time_series = [float(x[0])/FRAMES_PER_SEC for x in match]
        percent_series_1 = [x[1] for x in match]
        percent_series_2 = [x[2] for x in match]
        # print "percent_series_1: " + str(percent_series_1)
        cleaned_series_1, stocks_started_1 = clean_up_data(percent_series_1)
        cleaned_series_2, stocks_started_2 = clean_up_data(percent_series_2)
        # print "cleaned series for match" + str(idx) 
        #for time, percent_1, percent_2 in zip(time_series, cleaned_series_1, cleaned_series_2):
            #print "time: " + str(time) + " , percent_1: " + str(percent_1) + " , percent_2: " + str(percent_2)
        # print "cleaned_series_1: " + str(cleaned_series_1)
        # print "cleaned_series_2: " + str(cleaned_series_2)
        winner = winners[idx]
        # if winner is unclear from reading percents, try to figure out from stock count
        if winner == 0:
            print "winner unclear from reading percents for game " + str(idx + 1)
            if stocks_started_1 < stocks_started_2:
                winner = 1
            if stocks_started_2 < stocks_started_1:
                winner = 2
        if winner == 1:
            wins_1 += 1
        if winner == 2:
            wins_2 += 1
        num_stocks_won_by = abs(stocks_started_1 - stocks_started_2) + 1
        metrics = calculate_control(time_series, cleaned_series_1, cleaned_series_2)
        
        print "in match " + str(idx) + ", player 1 controlled for " + str(metrics['controlled_time_1']) + " and player 2 controlled for " + str(metrics['controlled_time_2'])
        print "player 1 average damage per opening: " + str(metrics['average_combo_length_1']) + ' on ' + str(metrics['num_openings_1']) + ' openings'
        print "player 2 average damage per opening: " + str(metrics['average_combo_length_2']) + ' on ' + str(metrics['num_openings_2']) + ' openings'
        print "player 1 combo damages: " + str(metrics['combo_damage_1'])
        print "player 2 combo damages: " + str(metrics['combo_damage_2'])
        percent_subplt = plt.subplot(num_matches, 3, (3 * idx) + 1)
        plt.plot(time_series, cleaned_series_1, 'r-')
        plt.plot(time_series, cleaned_series_2, 'b-')
        plt.xlim([0,max_match_length + 5])
        percent_subplt.set_title('Game ' + str(idx+1) + ": Winner is Player " + str(winner) + " by " + str(num_stocks_won_by) + " stocks")
        percent_subplt.set_xlabel('Seconds')
        percent_subplt.set_ylabel('Percent')

        combos_subplt = plt.subplot(num_matches, 3, (3 * idx) + 2)
        n, bins, patches = plt.hist(metrics['combo_damage_1'], 50, normed=1, facecolor='red', alpha=0.75)
        n, bins, patches = plt.hist(metrics['combo_damage_2'], 50, normed=1, facecolor='blue', alpha=0.75)
        combos_subplt.set_title("Total combo percents")
        control_subplt = plt.subplot(num_matches, 3, (3 * idx) + 3)
        plt.pie([metrics['controlled_time_1'],metrics['controlled_time_2']],colors=('r','b'))
        control_subplt.set_title("Percentage of control of match")


    set_count = "Set count: " + str(wins_1) + " - " + str(wins_2)
    percent_fig.suptitle(set_count)
    percent_fig.subplots_adjust(hspace=0.75)
    plt.show()
    if not os.path.exists('graphs'):
        os.makedirs('graphs')
    data_file_name = data_file.split('/')[1].split('.')[0]
    percent_fig.savefig('graphs/' + data_file_name + '_percent.png', dpi = percent_fig.dpi)
if __name__ == "__main__":
    main()
