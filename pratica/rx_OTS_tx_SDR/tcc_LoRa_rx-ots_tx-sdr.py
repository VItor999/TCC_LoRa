from tcc import Configurations as config
from tcc import functions as f
from tcc import SimpleLogger as logger 
import zmq
import serial 
import time
import threading
import TX_SDR_LIME as tx_sdr

MUTEX_TIME_RETRY_LOCK = 0.003 

def tx_flowchart_loop(cr,sf,bw,input):
    global recv_path_sim,run_tx_thread,mutex_tx_sdr,run_threads
    run = False
    tx_flowchart = tx_sdr.TX_SDR_LIME(cr=cr,sf=sf,bw=bw,in_file=input)
    while not run:
        run = run_threads and run_tx_thread
    tx_flowchart.start()
    tx_flowchart.wait()
    print('TX Flowchart thread stopped!')
    return


def send_command(serial,command):
    serial.write(f"{command}\n".encode())  # Send the command to Arduino

def wait_for_response(serial):
    waiting = True
    response = ''
    while waiting:
        #print(f'Trapped {who}')
        #time.sleep(0.100)
        if serial.in_waiting > 0:
            waiting = False
            response = serial.readline().decode().strip()
    return response

def verify_command(response):
    command = response[:-1] # removes the end command
    print(command)
    ans= {'SetupOk': False,
          'ComError' : False,
          'StartOK': False, 
          'Error' : False,
          'EndSimOk' : False,
          'DoneOK': False
            }
    
    if (command == 'SetupOk'):
        print('Setup OK')
    elif(command == 'DoneOK'):
        print('Done OK')
    elif (command == 'ComError'):
        print('Error on serial read/write as for retransmission')
    elif (command == 'StartOk'):
        print('Starting experiment')
    elif (command == 'Error'):
        print('Unknown Error, restart LoRa Sender and this program')
    elif (command == 'EndSimOk'):
        print('Ending simulation with the current configuration')
    else:
        return None
    ans[command] = True
    return ans

def execute_command(command_tag,command_str):
    command_ok = False
    while (not command_ok): #command validation
        send_command(ser,command_str)
        response_recv = False
        while not response_recv:
            response = wait_for_response(ser)
            if (response != command_str):
                response_recv = True
        command = verify_command(response)
        if command != None:
            if command[f'{command_tag}Ok']:
                command_ok = True
    return

def serial_thread_loop():
    global ser
    ended = False
    while(not mutex_serial.acquire(blocking=False)):
        time.sleep(MUTEX_TIME_RETRY_LOCK)
    while (not ended):
        response = wait_for_response(ser)
        command = verify_command(response)
    if (command['EndSim']):
        ended = True
    mutex_serial.release()
    return 

def set_run_threads(state):
    global run_threads
    while(not mutex_stop_thread.acquire(blocking=False)):
        time.sleep(MUTEX_TIME_RETRY_LOCK)
    run_threads = state
    mutex_stop_thread.release()
    return

def stop_program():
    global tx_thread
    print('Exiting')
    set_run_threads(False)
    if(tx_thread.is_alive()):
        tx_thread.join()
    print('Exiting main thread')
    exit()


if __name__ == "__main__":

#region CONFIGS
    conf = config.Configurations('config.ini')
    conf.update_configurations()

    if (conf.can_start):
        # FILES
        tx_path = conf.tx_path
        recv_path = conf.recv_path
        log_path = conf.log_path
        global_log_path = conf.global_log_path
        result_path = conf.result_path
        plot_path = conf.plot_path

        # GNURadioParams
        sample_rate = conf.sample_rate
        center_freq = conf.center_freq
        band_width = conf.band_width
        s_fact = conf.s_fact
        crs = conf.crs
        has_crc = conf.has_crc
        header = conf.header
        noise_seed = 10 # conf.noise_seed
        f_offset = conf.f_offset
    
        # Custom Simulation Params
        message = conf.message
        send_number = conf.send_number
        taps_str_list = conf.taps_str_list
        sim_level = conf.sim_lv
        tx_power = conf.tx_power
        msg_path = f'{tx_path}tx_text.txt'
    #endregion    
        
#region FILES
        f.delete_file(global_log_path)
        f.clear_directory(recv_path)
        f.clear_directory(log_path)
        f.clear_directory(result_path)
        f.create_dir(tx_path)
        f.create_std_message(msg_path,message,send_number)
       

#endregion 

#region LOG
        log = logger.SimpleLogger(global_log_path=global_log_path)
        if(conf.log_lv == 0):
            log.global_logger.disabled = True
            log.local_logger.disabled = True
        else:
            file_handler = logger.lg.FileHandler(global_log_path)
            file_handler.setLevel(logger.lg.INFO)
            file_handler.setFormatter(log.formatter)
            log.global_logger.addHandler(file_handler)
#endregion

        ser = serial.Serial('/dev/hal_LoRa',57600,timeout=1)
        time.sleep(1)  # Wait for the connection to establish  

        msg = f'{f.read_line_from_binary(msg_path).decode("utf-8").split(",")[0]}\n'.encode("utf-8")
        log.global_logger.info(f'Base message {msg}')
        start_time = time.perf_counter()

#region THREADS
        run_threads = False # creating global thread control variable 
        # Mutex
        mutex_recv_path = threading.Lock()
        mutex_stop_thread = threading.Lock()
        mutex_serial = threading.Lock()
        mutex_tx_sdr = threading.Lock()
        # Create and start the socket listening thread

#endregion

### SIMULATION 
        set_run_threads(True)
        for cr in crs:
            for sf in s_fact:
                for bw in band_width:
                    i=0
                    rx_path_data = f'{recv_path}{cr}/rx_{sf}_{bw}/'
                    folder_data_path = f'{result_path}sim_{cr}_{sf}_{bw}/'
                    local_logs_path = f'{log_path}log/{cr}/{sf}_{bw}/'
                    f.create_dir(folder_data_path)
                    f.create_dir(local_logs_path)
                    f.create_dir(rx_path_data)   
                    option = ''
                    while option == '':
                        option = input(f'(Re)Insert attenuation level (dBm), or type exit to quit (or write q){i}:\t')
                    while (option.lower() != 'exit' and option.lower() != 'q'):
                        
                        attenuation = float(option)
                        log.global_logger.info(f'Simulation started:\n\tNumber of messages to send {send_number}\n\tCenter Frequency = {center_freq} \n\tSF = {sf} \n\tBW = {band_width}')
                        log.global_logger.info(f'CR 4:{cr+4} \tSF: {sf} \tBW: {bw} \tPW: {tx_power}')
                        log.global_logger.info(f'TX messages send from file: {msg_path}')
                        log.global_logger.info(f'RX data stored in folder: {rx_path_data}')
                        
                        #RTL_(center_freq=center_freq, sf=sf,
                        #                                    bw=bw, out_file=recv_path_sim, cr=cr ,has_crc=has_crc,
                        #                                    impl_head=header, samp_rate=sample_rate, in_file=msg_path, 
                        #                                    taps_str=taps_str_list)
                        command_tag = 'Setup' 
                        command_str = f"{command_tag}#{cr}#{sf}#{bw}#{send_number}#{tx_power}#{message}!"
                        execute_command(command_tag,command_str)
                        file_to_log = ''
                        if (conf.log_lv == 2):
                            file_to_log = logger.lg.FileHandler(f'{local_logs_path}log_{attenuation:2.2f}.txt')
                            file_to_log.setLevel(logger.lg.INFO)
                            log.local_logger.addHandler(file_to_log)

                        log.local_logger.info(f'###### Starting Simulation attention = {attenuation}')
                        log.local_logger.info(f'\t##### Bits per message:{len(msg)*8}')
                        while(not mutex_recv_path.acquire(blocking=False)):
                            time.sleep(MUTEX_TIME_RETRY_LOCK)
                        recv_path_sim = f'{rx_path_data}{i}_rx_{attenuation:2.2f}.dat'
                        f.check_create_file(recv_path_sim)
                        mutex_recv_path.release()
                        command_tag = 'Start'
                        command_str = f'{command_tag}!'
                        initial_time = time.perf_counter()
                        while(not mutex_tx_sdr.acquire(blocking=False)):
                            time.sleep(MUTEX_TIME_RETRY_LOCK)
                        run_tx_thread = True
                        mutex_tx_sdr.release()  
                        tx_thread = threading.Thread(target=tx_flowchart_loop,args=(cr,sf,bw,msg_path))
                        tx_thread.start()
                        
                        execute_command(command_tag,command_str)
                        
                        not_done = True
                        while not_done:
                            response = ''
                            waiting = True
                            print('Please wait')
                            while waiting:
                                if ser.in_waiting > 0:
                                    waiting = False
                                    response = ser.read(ser.in_waiting)
                            ans = verify_command(response)
                            if ans == None :
                                print("aqui")
                                with open(recv_path_sim, 'ab') as file:
                                    file.write(response)
                            elif (ans['EndSimOk']):
                                not_done = False
                           
                        time.sleep(0.100)
                        final_time = time.perf_counter()
                        dif = final_time - initial_time
                        formatted_duration = f.time_dif_format(dif)
                        log.local_logger.info(f'\t###### Simulation duration: {formatted_duration}')
                        log.local_logger.info(f'###### End of simulation')
                        log.local_logger.removeHandler(file_to_log)
                        i+=1 
                        formatted_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        log.global_logger.info(f'End time {formatted_date_time}')
                        log.global_logger.info(f'Total time spent: {formatted_duration}')
                        #while(not mutex_tx_sdr.acquire(blocking=False)):
                        #    time.sleep(MUTEX_TIME_RETRY_LOCK)
                        #run_tx_thread = False
                        #mutex_tx_sdr.release() 
                        #tx_thread.join() 
                        option = input(f'(Re)Insert attenuation level (dBm), or type exit to quit (or write q){i}:\t')

        stop_program()

