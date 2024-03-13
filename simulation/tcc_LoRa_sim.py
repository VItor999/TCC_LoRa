'''
This is an auxiliary script made to compare two bits from to files in order to calculate
the BER (bit error rate) between then. If the base (tx_file) has more lines the the output
file (rx_file) than the error rate off the missing lines will be set to 1.0000 (100%).
The way this code is implemented is that that base massage is always the same. 
There could be a better way to do this analysis ...
 
Made by Vitor Carvalho: https://github.com/VItor999
'''

import TX_RX_SIM as simulation
import time
from tcc import Configurations as config
from tcc import SimpleLogger as logger
from tcc import functions as f
from tqdm import tqdm as prog_bar
import random
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
        # Get the current timestamp
        timestamp = int(time.time())

        # Use the timestamp as a seed
        random.seed(timestamp)
        noise_seed = conf.noise_seed
        noise_seed =  random.randint(0,100) #
        print(noise_seed)
        f_offset = conf.f_offset
        # Custom Simulation Params
        message = conf.message
        send_number = conf.send_number
        taps_str_list = conf.taps_str_list
        lower_SNR_level = conf.l_snr_lv
        upper_SNR_level = conf.u_snr_lv
        step = conf.step
        sim_level = conf.sim_lv
        tx_power = conf.tx_power
        msg_path = f'{tx_path}tx_text.txt'
    #endregion    
        
#region FILES
        f.delete_file(global_log_path)
        f.clear_directory(plot_path)
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
        
        msg = f'{f.read_line_from_binary(msg_path).decode("utf-8").split(",")[0]}\n'.encode("utf-8")
        noise_list = f.noise_snr_range(min_value=lower_SNR_level,max_value=upper_SNR_level,step=step)
        log.global_logger.info(f'Noise list length message {len(noise_list)}')
        #print(f'Noise list length message {len(noise_list)}')
        f.save_sim_data(f'{tx_path}/noise.txt',noise_list)
        log.global_logger.info(f'Base message {msg}')
        log.global_logger.info(f'Noise level from {lower_SNR_level} to {upper_SNR_level}')
        start_time = time.perf_counter()
        for cr in crs:
            for sf in s_fact:
                for bw in band_width:
                 
                    #total_ber_list = []
                    #snr_list = []
                    rx_path_data = f'{recv_path}{cr}/rx_{sf}_{bw}/'
                    folder_data_path = f'{result_path}sim_{cr}_{sf}_{bw}/'
                    local_logs_path = f'{log_path}log/{cr}/{sf}_{bw}/'
                    #f.create_dir(folder_data_path)
                    f.create_dir(local_logs_path)
                    f.create_dir(rx_path_data)
                    
                    log.global_logger.info(f'Simulation started:\n\tNumber of messages to send {send_number}\n\tCenter Frequency = {center_freq} \n\tSF = {sf} \n\tBW = {band_width}')
                    log.global_logger.info(f'CR 4:{cr+4} \tSF: {sf} \tBW: {bw}')
                    log.global_logger.info(f'TX messages send from file: {msg_path}')
                    log.global_logger.info(f'RX data stored in folder: {rx_path_data}')
                    i = 0
                    ####### Simulation  
                    for noise_value in prog_bar(noise_list):
                        initial_time = time.perf_counter()
                        file_to_log = ''
                        if (conf.log_lv == 2):
                            file_to_log = logger.lg.FileHandler(f'{local_logs_path}log_{noise_value:2.2f}.txt')
                            file_to_log.setLevel(logger.lg.INFO)
                            log.local_logger.addHandler(file_to_log)

                        log.local_logger.info(f'###### Starting Simulation AWGN noise = {noise_value}')
                        log.local_logger.info(f'\t##### Bits per message:{len(msg)*8}')

                        recv_path_sim = f'{rx_path_data}{i}_rx_noise_{noise_value:2.2f}.dat'
                        ##### SIMULATION 
                        flow_graph = simulation.TX_RX_SIM(center_freq=center_freq, noise=noise_value, sf=sf,
                                                        bw=bw, out_file=recv_path_sim, cr=cr ,has_crc=has_crc,
                                                        impl_head=header, samp_rate=sample_rate, in_file=msg_path, 
                                                        taps_str=taps_str_list, noise_seed=noise_seed)
                        flow_graph.start()
                        flow_graph.wait()
                        ##### Per simulation Analyses
                        #total_ber = f.compute_ber(msg,send_path,recv_path_sim)
                        #snr = f.compute_SNR(tx_power,noise_value)
                        final_time = time.perf_counter()
                        dif = final_time - initial_time
                        formatted_duration = f.time_dif_format(dif)
                        log.local_logger.info(f'\t###### Simulation duration: {formatted_duration}')
                        log.local_logger.info(f'###### End of simulation')
                        log.local_logger.removeHandler(file_to_log)
                        
                        ###### Storing Data 
                        #total_ber_list.append(total_ber)
                        #snr_list.append(snr)1
                        i+=1 
                    # End Simulation
                    end_time = time.perf_counter()
                
                    dif = end_time - start_time
                    formatted_duration = f.time_dif_format(dif)
                    formatted_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    log.global_logger.info(f'End time {formatted_date_time}')
                    log.global_logger.info(f'Total time spent: {formatted_duration}')
                    if (conf.sound):
                        f.play_sound_multiple_times('/home/vcarv/TCC/tcc_aux/tcc/alarm.wav',1)
                 
        if (conf.sound):
            f.play_sound_multiple_times('/home/vcarv/TCC/tcc_aux/tcc/alarm.wav',5)