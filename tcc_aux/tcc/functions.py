import os
import csv
import numpy as np
import logging as lg
import matplotlib.pyplot as plt
import re
from tqdm import tqdm as progress_bar
import simpleaudio as sa
import pandas as pd
"""
Potential Improvements:

Modularization: Each distinct functionality (BER calculation, MER calculation, SNR calculation, data loading, plotting) should be modularized into separate files or classes.
Exception Handling: There should be comprehensive error and exception handling, especially where file I/O operations are involved.
Logging: The current logging mechanism could be improved with proper configuration and more detailed logging messages.
Testing: Each function should have associated unit tests to ensure they work as expected and to facilitate easier debugging and maintenance.
Code Documentation: Although the functions have docstrings, adding comments within complex sections of code would improve readability.
Data Models: Using classes or dataclasses to represent simulation data would make the code more organized and maintainable.
Performance: Functions like count_lines could be optimized for large files, potentially using generators or buffer reading.
File Naming Convention: The function extract_number relies on a specific file naming convention, which should be consistently enforced or made more flexible.
"""

def time_dif_format(time_dif):
    '''
    Formats a time difference in hour, minutes seconds and milliseconds 

    :param time_dif: Time difference.
    :type time_dif: float
    :return: Formatted time difference.
    :rtype: str
    '''
    hours, rem = divmod(time_dif, 3600)
    minutes, seconds = divmod(rem, 60)
    formatted_time = "{:0>2}:{:0>2}:{:06.3f}".format(int(hours), int(minutes), seconds)
    return formatted_time

def compute_MER(message,tx_file_path,rx_file_path):
    '''
    Calculate the MER of one simulation

    :param message: Base massage 
    :type message: string
    :param tx_file_path: Path to the file of transmitted message 
    :type tx_file_path: string
    :param rx_file_path: Path to the file of received message
    :type rx_file_path: string 
    :return: Total Packet Message Rate (MER) of the simulation 
    :rtype: int
    '''

    wrong_msgs = -1 
    line_send = count_lines(tx_file_path)
    line_recv = count_lines(rx_file_path)
    lines = line_send - line_recv
    local_logger = lg.getLogger('local')
    for lost_line in range(lines):
        wrong_msgs += 1
    with open(rx_file_path, 'rb') as file:
        for line in file:
            lines += 1
            if(message != line):
                wrong_msgs += 1
        local_logger.info(f'\t##### Mensagens Enviadas: {line_send}')
        local_logger.info(f'\t##### Mensagens Recebidas: {line_recv}')
        local_logger.info(f'\t##### Porcentagem Recebidas/Enviadas: {(line_recv/line_send)*100} %')
   
    return (wrong_msgs/line_send)

def calculate_wrong_bits_for_msg(base_msg, new_msg):
    '''
    Calculates the number of wrong bits the base massage and a massage with is received 

    :param base_msg: Standard massage that was transmitted 
    :type base_msg: Utf-8 string
    :param new_msg: Message received
    :type new_msg: Utf-8 string
    :return: Bit Error Rate (BER) of this new message 
    :rtype: int 
    '''
    differing_bits = 0
    min_length = min(len(base_msg), len(new_msg)) 
    for b1, b2 in zip(base_msg[:min_length], new_msg[:min_length]):
        differing_bits += bin(b1 ^ b2).count('1')
    wrong_bits = differing_bits
    return wrong_bits

def count_lines(filename):
    '''
    Count how many lines there is in a file

    :param filename: Path of the file of interest
    :type filename: String
    :return: number of  lines 
    :rtype: int
    '''
    with open(filename, 'rb') as f:
        return sum(1 for line in f)

def compute_ber(message,tx_file_path,rx_file_path):
    '''
    Calculate the BER of one simulation

    :param message: Base massage 
    :type message: string
    :param tx_file_path: Path to the file of transmitted message 
    :type tx_file_path: string
    :param rx_file_path: Path to the file of received message
    :type rx_file_path: string 
    :return: Total Bit Error Rate (BER) of the simulation 
    :rtype: int
    '''

    wrong_bits_total = 0 
    line_send = count_lines(tx_file_path)
    line_recv = count_lines(rx_file_path)
    lines = line_send - line_recv
    local_logger = lg.getLogger('local')
    for lost_line in range(lines):
        # times 8 because the message is encoded in utf-8
        wrong_bits_total += len(message)*8
        #print(f"Line {lost_line}: BER = {len(message)*8}")
    with open(rx_file_path, 'rb') as file:
        for line in file:
            lines += 1
            wrong_bits = calculate_wrong_bits_for_msg(message, line)
            wrong_bits_total += wrong_bits
            #print(f"Line {lines}: BER = {ber:.4f}")
        local_logger.info(f'\t##### Mensagens Enviadas: {line_send}')
        local_logger.info(f'\t##### Mensagens Recebidas: {line_recv}')
        local_logger.info(f'\t##### Porcentagem Recebidas/Enviadas: {(line_recv/line_send)*100} %')
        local_logger.info(f'\t##### Total de Erros de bit: {wrong_bits_total}')
        ## Total de bits na mensagem ... 
        local_logger.info(f'\t##### Total de Bits transmitidos: {line_send*len(message)*8}')
        local_logger.info(f'\t##### Porcentagem de Bits Recebidos: {100 - ((wrong_bits_total)*100/(line_send*len(message)*8))}%')

    total_ber = wrong_bits_total/(line_send*len(message)*8)
    return total_ber
    
def binary_to_utf8(file_path):
    '''
    Converts a binary file to utf-8

    :param file_path: Directory where the base file is stored
    :type file_path: string
    '''
    file_name = file_path.split('.')
    new_file_path = file_name[0] +"_utf8.txt"
    with open(file_path, 'rb') as file:
        with open(new_file_path,'w+') as new_file:
            for line in file:
                try:
                    line = line.decode('ascii')
                    new_file.write(line)
                except:
                    new_file.write('Invalid Character in this line')

def read_line_from_binary(file_path):
    '''
    Read a binary file 

    :param file_path: Directory of the file to be read.
    :type file_path: string
    :return: Line that was read
    :rtype: binary
    '''
    with open(file_path, 'rb') as file:
        return file.readline()
    
def read_float32_data(file_name):
    '''
    Read a numpy float32 from a file 

    :param file_name: File path
    :type file_name: string
    :return: All file data as float an 
    :rtype: np.array(float32)
    '''
    data = np.fromfile(file_name, dtype=np.float32)
    return data

def create_std_message(file_name, message, lines):
    '''
    Create the standard message to be transmitted.

    :param file_name: Name of the output file.
    :type file_name: str
    :param message: Message.
    :type message: str
    :param lines: Number of lines.
    :type lines: int
    '''
    with open(file_name, 'w') as file:
        for i in range(lines):
            if i == lines - 1:
                file.write(f'{message},')
            else :
                file.write(f'{message},\n')

def write_bin_line(path,data):
    with open(path, 'ab') as file:
        file.write(data+b',\n')

def compute_SNR(signal, noise):
    '''
    Computes the SNR.

    :param signal: Transmitted signal in complex format
    :type signal: array[floats]
    :param noise: Noise signal in complex format.
    :type noise: array[floats]
    :return: Calculated SNR.
    :rtype: float
    '''
    #noise = noise - signal
    P_signal = np.mean(np.square(signal))
    P_noise = np.mean(np.square(noise))
    SNR = 10 * np.log10(P_signal / P_noise)
    return SNR

def clear_directory(directory_path):
    '''
    Cleans a directory

    :param directory_path: Path to the directory 
    :type directory_path: string
    '''
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    clear_directory(file_path)  # Recursively clear subdirectories
                    os.rmdir(file_path)  # Remove the now-empty directory
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    except Exception as e:
        print("Directory does not exist")
    finally:
        return
   
def delete_file(filename):
    """
    Deletes the specified file.

    :param filename: Path to the file to be deleted.
    """
    if os.path.exists(filename):
        os.remove(filename)
    #else:
    #   print(f"'{filename}' does not exist!")

def noise_snr_range(min_value=-10, max_value=10, step=0.1, tx_power=1):
    '''
    Generates a range of noise values to generate a simulation with the desired SNR range and spacing

    :param min_value: Lower bound of the range, defaults to -10.
    :type min_value: int, optional
    :param max_value: Upper bound of the range, defaults to 10.
    :type max_value: int, optional
    :param step: Step between two values, defaults to 0.1.
    :type step: float, optional
    :param tx_power: Power of the transmission, defaults to 1.
    :type tx_power: int, optional
    :return: noise values to be used in the simulation.
    :rtype: array[float]
    '''
    # Define the range for y values, for instance from -10 to 10
    y_values = np.arange(min_value, max_value+step,step)
    noise_values = [tx_power * 10**(-y/20) for y in y_values]
    return noise_values

def save_sim_data(file_path,list_data):
    '''
    Save simulation data

    :param file_path: Path to save the data.
    :type file_path: str
    :param list_data: Data to be saved.
    :type list_data: list[floats]
    '''
    with open(file_path, "w", newline='') as file:
        writer = csv.writer(file)
        for item in list_data:
            writer.writerow([item])

def load_csv_to_list(filename,delimiter = ','):
    '''
    Loads data from a csv to a list. It's  expected that all the values inside are floats

    :param filename: Path of the file to load.
    :type filename: str
    :param delimiter: Character to break, defaults to ','
    :type delimiter: str, optional
    :return: Return the contents .csv file.
    :rtype: list[floats]
    '''
    with open(filename, "r") as file:
        reader = csv.reader(file,delimiter=delimiter)
        return [float(row[0]) for row in reader] 
 
def merge_list(main_list,incorporated):
    '''
    Merge to lists

    :param main_list: List that will incorporate the contents of the other list.
    :type main_list: list[Any]
    :param incorporated: List that will be incorporated by the main list.
    :type incorporated: list[Any]
    :return: Merged list.
    :rtype: list[Any]
    '''
    if incorporated != None:
        for item in incorporated:
            main_list.append(item)
    return main_list

def create_dir(path):
    '''
    Create a directory if it does not exist.

    :param path: Path o the new directory.
    :type path: str
    '''
    if not os.path.exists(path):
        os.makedirs(path)

def or_str_filter(strings,filtering_strings= None):
    '''
    Filter any list of strings to return a list that contains only the elements that match any filtering substrings.

    :param strings: List of strings to be filtered.
    :type strings: list[str]
    :param filtering_strings: List of substrings that the main string must have, defaults to None
    :type filtering_strings: list[str], optional
    :return: List of the strings that have all the substrings of the filter
    :rtype: list[str]
    '''
    filtered_strings = []
    if (filtering_strings != None):
        for string in strings:
            is_in = False
            for filter in filtering_strings:
                if filter is string:
                    is_in = True
            if is_in:
                filtered_strings.append(string)
        ordered = sorted(filtered_strings)
        return ordered
    return strings

def and_str_filter(strings,filtering_strings= None):
    '''
    Filter any list of strings to return a list that contains only the elements that match all filtering substrings.

    :param strings: List of strings to be filtered.
    :type strings: list[str]
    :param filtering_strings: List of substrings that the main string must have, defaults to None
    :type filtering_strings: list[str], optional
    :return: List of the strings that have all the substrings of the filter
    :rtype: list[str]
    '''
    filtered_strings = []
    if (filtering_strings != None):
        for string in strings:
            is_in = True
            for filter in filtering_strings:
                if filter not in string:
                    is_in = False
            if is_in:
                filtered_strings.append(string)
        ordered = sorted(filtered_strings)
        #print(ordered)
        return ordered
    return strings

def get_x_y_data(x_path_list,y_path_list):
    '''
    Get X and Y data from a files.

    :param x_path_list: List with paths from X data to be loaded.
    :type x_path_list: list[str]
    :param y_path_list: List with paths from Y data to be loaded.
    :type y_path_list: list[str]
    :return: Dictionary with CR:{cr}_SF:{sf}_BW:{bw} pattern as key and a dictionary with keys X and Y as values. The values of the dictionary accessed inner keys are the data of the respective axis. 
    :rtype: dict{dict{float}}
    '''
    len_x = len(x_path_list)
    len_y = len(y_path_list)
    assert len_x ==  len_y, f"ERROR len(x_path_list) != len(y_path_list) {len_x} , {len_y}  "
    num_plots = len_x
    plots = dict()
    for i in range(num_plots):
        x = load_csv_to_list(x_path_list[i])
        y = load_csv_to_list(y_path_list[i])
        split = x_path_list[i].split('_')
        cr = split[-3]
        sf = split[-2]
        bw = split[-1].split('.')[0]
        plots[f'CR: {cr}_SF: {sf}_BW: {bw}Hz'] = {'X':x,
                                             'Y':y}
    return plots

def load_data_for_plot(path_x,path_y,filtering_strings=None,filter_type = 'and'):
    '''
    Loads data for a plot.

    :param path_x: Path to x axis data.
    :type path_x: str
    :param path_y:  Path to y axis data.
    :type path_y: str
    :param filtering_strings: List of strings that will be used to filter for a specific data to load, defaults to None
    :type filtering_strings: list[str], optional
    :param filter_type: Type of filter AND or OR, defaults to 'and'
    :type filter_type: str, optional
    :return: Dictionary with CR:{cr}_SF:{sf}_BW:{bw} pattern as key and a dictionary with keys X and Y as values. The values of the dictionary accessed inner keys are the data of the respective axis. 
    :rtype: dict{dict{float}}
    '''
    plots = dict()
    all_x = [os.path.join(path_x, f) for f in os.listdir(path_x)]
    all_y = [os.path.join(path_y, f) for f in os.listdir(path_y)]
    if (filter_type == 'or'):
        filtered_x = or_str_filter(all_x,filtering_strings=filtering_strings)
        filtered_y = or_str_filter(all_y,filtering_strings=filtering_strings)
    elif (filter_type == 'and'):
        filtered_x = and_str_filter(all_x,filtering_strings=filtering_strings)
        filtered_y = and_str_filter(all_y,filtering_strings=filtering_strings)
    plots = get_x_y_data(filtered_x,filtered_y)
    return plots

#TODO, MAKE A GENERIC PLACE TO SPLIT 
def extract_number(filename):
    '''
    This assumes a filename structure like "0_file.zzz". It extracts the numerical part of the filename and converts it to an integer.

    :param filename: Name of the file to extract the number.
    :type filename: str
    :return: Number that was in the file name
    :rtype: int
    '''
    num_part = filename.split('_')[0]
    return int(num_part) if num_part.isdigit() else float('inf')  # Handle non-numeric filenames gracefully

def get_folders(path):
    '''
    Get all folders in a path 

    :param path: Path to search for all folders in it.
    :type path: str
    :return: All folders in the path.
    :rtype: list[str]
    '''
    all_folders = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return all_folders


def single_sim_analyse(msg_path, rx_path, tx_path, results_path, tx_power,cr=1):
    '''
    Generate the analyse of the current data
    Analysis of all simulation data available

    :param msg_path: Path to where the message is stored (file).
    :type msg_path: str
    :param rx_path: Path to where the received data is stored (directory).
    :type rx_path: str
    :param tx_path: Path to where the transmitted data  is stored (directory)
    :type tx_path: str
    :param results_path: Path to where the results will be stored (directory)
    :type results_path: str
    :param tx_power: Transmission power
    :type tx_power: float
    :param cr: Coding rate being used, defaults to 1
    :type cr: int, optional
    '''
    msg = f'{read_line_from_binary(msg_path).decode("utf-8").split(",")[0]}\n'.encode("utf-8")
 
    create_dir(f'{results_path}/ber')
    create_dir(f'{results_path}/mer')
    create_dir(f'{results_path}/snr')
    all_folders =  [os.path.join(rx_path, f) for f in os.listdir(rx_path)]
    with open(f'{tx_path}/noise.txt', 'r') as file:
        noise_list =  [float(line.strip()) for line in file]
    for folder in progress_bar(all_folders):
        rx_paths = sorted(os.listdir(folder), key = extract_number)
        noise_rx_map = dict(zip(noise_list, rx_paths))
        total_ber_list = []
        snr_list = []
        total_mer_list = []
        split = folder.split('_')
        cr = cr
        sf = split[-2]
        bw = split[-1]
        #out_path = out_name+f'{cr}_{sf}_{bw}.csv'
        for noise, rx_path in  noise_rx_map.items():
            rx_full_path = folder+ '/' +rx_path
            #print(rx_full_path)
            ber = compute_ber(msg,msg_path,rx_full_path)
            mer = compute_MER(msg,msg_path,rx_full_path)
            snr = compute_SNR(tx_power,noise) 
            total_ber_list.append(ber)
            total_mer_list.append(mer)
            snr_list.append(snr)
            #store_in_single_table(msg,msg_path,rx_full_path,noise,out_path)
        
        save_sim_data(f'{results_path}/ber/ber_{cr}_{sf}_{bw}.csv',total_ber_list)
        save_sim_data(f'{results_path}/mer/mer_{cr}_{sf}_{bw}.csv',total_mer_list)
        save_sim_data(f'{results_path}/snr/snr_{cr}_{sf}_{bw}.csv',snr_list)

def check_create_file(file_path):
    if not os.path.exists(file_path):
        # File does not exist, create an empty file
        with open(file_path, 'ab') as file:
            pass  # 'pass' simply does nothing, but it allows for an empty 'with' block


def join_data(rx_path, tx_path, results_path,cr=1):

    all_folders =  [os.path.join(rx_path, f) for f in os.listdir(rx_path)]
    with open(f'{tx_path}/noise.txt', 'r') as file:
        noise_list =  [float(line.strip()) for line in file]
    for folder in progress_bar(all_folders):
        rx_paths = sorted(os.listdir(folder), key = extract_number)
        noise_rx_map = dict(zip(noise_list, rx_paths))
        split = folder.split('_')
        cr = cr
        sf = split[-2]
        bw = split[-1]
        out_path_rx = f'{results_path}/global_rx/{cr}/rx_{sf}_{bw}'
        out_path_tx = f'{results_path}/global_tx/'
        create_dir(out_path_rx)
        create_dir(out_path_tx)
        out_noise = out_path_tx+'noise.txt'
        #out_path_tx = out_path_tx+'tx_text.txt'
        check_create_file(out_noise)
        #check_create_file(out_path_tx) 
        with open(out_noise, 'r') as file:
            noise_entries =  [float(line.strip()) for line in file]
        sorted_noise = sorted(noise_entries, reverse=True)
        i =0
        for noise, rx_path in  noise_rx_map.items():
            out_path_rx = f'{results_path}/global_rx/{cr}/rx_{sf}_{bw}/{i}_rx_noise{noise:2.2f}.csv'
            check_create_file(out_path_rx)
            if (noise not in sorted_noise):
                sorted_noise.append(noise)
                sorted_noise = sorted(sorted_noise, reverse=True)
            rx_full_path = folder+ '/' +rx_path
            tx_full_path = f'{tx_path}tx_text.txt'
            append_binary_content(rx_full_path,out_path_rx)
            i +=1
        save_sim_data(out_noise,sorted_noise)
        #append_binary_content(tx_full_path,out_path_tx)
        
def is_file_empty(file_path):
    """ Check if file is empty by reading its size """
    return os.path.exists(file_path) and os.path.getsize(file_path) == 0

def append_binary_content(source_path, target_path):
    """
    Appends the binary content of the source file to the target file.
    
    :param source_path: Path to the source file.
    :param target_path: Path to the target file.
    """
    try:
        # Read the content of the source file
        
        with open(source_path, 'rb') as source_file:
            content = source_file.read()
        
        # Append the content to the target file
        
        with open(target_path, 'ab') as target_file:
            if (not is_file_empty(target_path)):
                target_file.write(b'\n')
            target_file.write(content)

        #print(f"Content from {source_path} has been appended to {target_path}.")
    except IOError as e:
        print(f"An error occurred: {e}")


def store_in_single_table(message,tx_file_path,rx_file_path,noise_pw,output_table_path):
    line_send = count_lines(tx_file_path)
    line_recv = count_lines(rx_file_path)
    lines = line_send - line_recv
    global_logger = lg.getLogger('global')
    if not os.path.exists(output_table_path):
        with open(output_table_path,'ab') as table:
            table.write(b'PWR_NOISE,MSG_TX,MSG_RX\n')
    else:
        with open(output_table_path,'ab') as table:
            for lost_line in range(lines):
                line_out = f'{noise_pw:2.2f}'.encode()+ b',' + message[0:-1] + b',' + b'\'\'' +b'\n'
                table.write(line_out)
            with open(rx_file_path, 'rb') as rx_file:
                for rx_line in rx_file:
                    lines += 1
                    rx_line = rx_line.replace(b"\n", b"")

                    line_out =  f'{noise_pw:2.2f}'.encode()+ b',' +message[0:-1]  + b',' + rx_line +b'\n'
                    table.write(line_out)

#UPDATE/ TODO to make plots in the desired order 
def sort_key(filename, fixed_part=None, fixed_value=None):

    # Extract parts of the filename using regular expressions
    match = re.match(r'.*_(\d+)_(\d+)_(\d+).csv', filename)
    if not match:
        #print(f"{filename}")
        return (float('inf'),)  # Files that don't match the pattern go at the end

    x, yy, zzzzzz = map(int, match.groups())

    if fixed_part == 'cr':
        return (yy, zzzzzz) if x == fixed_value else (float('inf'),)
    elif fixed_part == 'sf':
        return (x, zzzzzz) if yy == fixed_value else (float('inf'),)
    elif fixed_part == 'bw':
        return (x, yy) if zzzzzz == fixed_value else (float('inf'),)
    else:
        # If nothing is fixed, sort by X, then YY, then ZZZZZZ
        return (x, yy, zzzzzz)

def play_sound_multiple_times(file_path, times):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    for _ in range(times):
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing

def append_xyz_data(x_file_path, y_file_path, z_file_path, output_file_path):
    # Read the X, Y, and Z data from their respective CSV files
    x_data = pd.read_csv(x_file_path)
    y_data = pd.read_csv(y_file_path)
    z_data = pd.read_csv(z_file_path)

    # Merge the X, Y, and Z data
    merged_data = pd.concat([x_data, y_data, z_data], axis=1)

    # Check if the output file exists
    if os.path.exists(output_file_path):
        # Append the new data to the existing file
        with open(output_file_path, 'a') as f:
            merged_data.to_csv(f, header=False, index=False)
    else:
        # Write the merged data to a new file
        merged_data.to_csv(output_file_path, index=False)
# TODO
# - Create a function calculate the mean curve of a bunch of plots 
# - Create a function to plot the standard deviation from a bunch of plots (correlated with the mean plot)
# - Create a function to merge te results of a bunch of simulations to generate a single curve
