import configparser
import argparse
import sys
class Configurations:
    '''
    Class that contains an ArgsParser and implements a basic structure to carry all parameters of the simulation during runtime.
    '''
    def __init__(self, filename):
        '''
        Creates the configuration object.

        :param filename: Path of the config.ini file.
        :type filename: str
        '''
        self.can_start = True
        if (len(sys.argv) == 2):
            if ('-h' in sys.argv[1]):  
                self.can_start = False
            
        self.ignore_inputs = False
        self.config = configparser.ConfigParser()
        try:
            self.args = self.arg_parser()
        except:
            self.ignore_inputs = True
        finally:
            self.config.read(filename)
            self.files = self.get_files()
            self.radio_params = self.get_radio_params()
            self.simulation = self.get_simulation()
            
    def arg_parser(self):
        '''
        Parse the arguments called in the when the program is started

        :return: Structured of the arguments passed
        :rtype: Dictionary like structure
        '''
        parser = argparse.ArgumentParser(description='Simulation of a GNURadio file. Setting the arguments through here will overwrite the paramters used in config.ini file. Type --help to see more info')
    
        ###### FILES ######
        parser.add_argument('--tx_path',type=str, help='Path where the file with the messages to be send is stored (directory)')
        parser.add_argument('--recv_path',type=str, help='Path where the received messages will be stored (directory)')
        parser.add_argument('--log_path',type=str, help='Path where the logs will be stored (directory)')
        parser.add_argument('--global_log_path',type=str, help='Path where the global log file will be stored (file)')
        parser.add_argument('--result_path',type=str, help='Path where the SNR and BER files will be stored (directory)')
        parser.add_argument('--plot_path',type=str, help='Path where the plots will be stored (directory)')

        ##### RADIO PARAMS #####
        parser.add_argument('--samp_rate',type=str, help='Sample rate of the GNU Radio Simulation')
        parser.add_argument('--center_freq', type=int, help='Center frequency in Hz')
        parser.add_argument('--band_width', type=str,  help='Bandwidth in Hz')
        parser.add_argument('--s_fact', type=str, help='Spreading Factor')
        parser.add_argument('--crs', type=str, help='Coding Rate')
        parser.add_argument('--has_crc', type=int, help='Has CRC? 0 for No, 1 for Yes')
        parser.add_argument('--header', type=int, help='Has Header? 0 for No, 1 for Yes')
        
        parser.add_argument('--f_offset', type=str, help='Frequency offset')
       

        ##### SIMULATION #####
        parser.add_argument('--message', type=str, help='Standard message to be send.')
        parser.add_argument('--send_number', type=int, help='How many times the message wil be repeated')
        parser.add_argument('--taps', type=str, help='Taps a+bj,c+dj')
        parser.add_argument('--noise_seed', type=int, help='Seed for noise generation')
        parser.add_argument('--tx_power', type=float, help='Power of the simulation')
        parser.add_argument('--l_SNR_lv', type=float, help='Lower SNR level in dB')
        parser.add_argument('--u_SNR_lv', type=float, help='Upper SNR level in dB')
        parser.add_argument('--step', type=int, help='Step between two noise values')
        parser.add_argument('--log_lv', type=int, help='Has logger Enabled? 0 for No, 1 for console and global log 2 for full log')
        parser.add_argument('--sim_lv', type=int, help='Complexity of the simulation 0-2. Each option also output the results of the other.\
                                \n\t0 - Output: Number of message received \(without any analysis of the content). \
                                \n\t1 - Output: Previous output and the number of messages received correctly. \
                                \n\t2 - Output: Previous output of messages received correctly and the BER considering the missing and received messages.')
        parser.add_argument('--sound', type=int, default=1, help='Disable sound if set to 0 (1 == default)')
        args = parser.parse_args()
        return args

    def get_files(self):
        '''
        Parses into a dictionary all the items in the 'files' category

        :return: Dictionary of strings as values and config.ini items as keys.
        :rtype: _type_
        '''
        # Assuming [DEFAULT] section for simplicity, adjust as needed
        return {k: v for k, v in self.config['files'].items()}
    
    def get_radio_params(self):
        '''
        Parses into a dictionary all the items in the 'radio_params' category

        :return: Dictionary of strings as values and config.ini items as keys.
        :rtype: _type_
        '''
        return {k: v for k, v in self.config['radio_params'].items()}

    def get_simulation(self):
        '''
        Parses into a dictionary all the items in the 'simulation' category

        :return: Dictionary of strings as values and config.ini items as keys.
        :rtype: _type_
        '''
        return {k: v for k, v in self.config['simulation'].items()}
    
    def update_configurations(self):   
        '''
        Update the configurations overriding the arguments from the config,ini with the ones available as parameters when the system is called.
        '''
        if(not self.ignore_inputs):
            for arg, value in vars(self.args).items():
                if value is not None:
                    if arg in self.files:
                        self.files[arg] = value
                    elif arg in self.radio_params:
                        self.radio_params[arg] = value
                    elif arg in self.simulation:
                        self.simulation[arg] = value
                    else:
                        print(f'arg {arg}')
                        print(f'value {arg}')
                        print('ERROR, invalid parameter')
        
        return
        
    
   
    ##### FILES #####
          
    @property
    def tx_path(self):
        '''
        Path of send messages.

        :return: Relative path where the send messages are located.
        :rtype: str
        '''
        return self.files['tx_path']
    
    @property
    def recv_path(self):
        '''
        Path of received messages.

        :return: Relative path of messages received.
        :rtype: str
        '''
        return self.files['recv_path'] 
   
    @property
    def log_path(self):
        '''
        Path of simulation iteration log.

        :return: Relative path of log for each number of messages send.
        :rtype: str
        '''
        return self.files['log_path']
   
    @property
    def global_log_path(self):
        '''
        Path of global log file.

        :return: Relative path of global log file.
        :rtype: str
        '''
        return self.files['global_log_path']
    
    @property
    def result_path(self):
        '''
        Path to results directory.

        :return: Relative where the simulation results will be stored,
        :rtype: str
        '''
        return self.files['result_path']
    
        
    @property
    def plot_path(self):
        '''
        Directory where the plot will be stored.

        :return: Path to store the plots.
        :rtype: str
        '''
        return self.files['plot_path']
    
    ##### GNURadioparams #####
    
    @property
    def sample_rate(self):
        '''
        Sample rate.

        :return: Sample rate of the simulation.
        :rtype: int
        '''
        return int(self.radio_params['sample_rate'])
    
    @property
    def center_freq(self):
        '''
        Central frequency.

        :return: Central frequency used in the simulation (Hz).
        :rtype: int
        '''
        return int(self.radio_params['center_freq'])
    
    @property
    def band_width(self):
        '''
        Bandwidth.

        :return: Bandwidth used  in the simulation (Hz).
        :rtype: int
        '''
        return [int(bw) for bw in self.radio_params['band_width'].split(',')]
    
    @property
    def s_fact(self):
        '''
        Spreading Factor (7-12).

        :return: Spreading factor (related with duration of the chirp).
        :rtype: int
        '''
        return [int(sf) for sf in self.radio_params['s_fact'].split(',')]
    
    @property
    def crs(self):
        '''
        Coding rate 1:= 4B/5B - 4:=4B/8B.

        :return: Coding Rate for the simulation.
        :rtype: int
        '''
        return [int(cr) for cr in self.radio_params['crs'].split(',')]
    
    @property
    def has_crc(self):
        '''
        Implements CRC in simulation.

        :return: 0 or 1, indicating if will implement the CRC.
        :rtype: int
        '''
        return int(self.radio_params['has_crc'])
    
    @property
    def header(self):
        '''
        Header.

        :return: 0 or 1 indicating if it will implement the Header. 
        :rtype: int
        '''
        return int(self.radio_params['header'])
    
    @property
    def noise_seed(self):
        '''
        Noise seed.

        :return: Value of the noise seed set for the simulation.
        :rtype: int
        '''
        return int(self.simulation['noise_seed'])
    
    @property
    def f_offset(self):
        '''
        Frequency offset.

        :return: Frequency offset.
        :rtype: int
        '''
        return float(self.radio_params['f_offset'])
    
    ##### SIMULATION #####

    @property
    def message(self):
        '''
        Message to be send.

        :return: Base message that will be transmitted.
        :rtype: str
        '''
        return self.simulation['message']
    
    @property
    def send_number(self):
        '''
        Send number.

        :return: Number of time the message will be send.
        :rtype: int
        '''
        return int(self.simulation['send_number'])
    
    @property
    def taps_str_list(self):
        '''
        List of taps in a string format 'a+bj'.

        :return: A list containing all taps in a string form.
        :rtype: list[str] 
        '''
        return self.simulation['taps'].split(',')
    
    @property
    def tx_power(self):
        '''
        Power of the transmission in VERIFY UNIT 

        :return: power of the transmission
        :rtype: float
        '''
        return float(self.simulation['tx_power'])
    
    @property
    def l_snr_lv(self):
        '''
        Lower SNR level for the simulation.

        :return: Lower SNR level of the simulation.
        :rtype: float
        '''
        return float(self.simulation['l_snr_lv'])

    @property
    def u_snr_lv(self):
        '''
        Upper SNR level for the simulation

        :return: Upper SNR level of the simulation.
        :rtype: float
        '''
        return float(self.simulation['u_snr_lv'])
    @property
    def step(self):
        return float(self.simulation['step'])
    
    @property
    def log_lv(self):
        '''
        Level of the logger 0-2

        :return: Level of the logger
        :rtype: int
        '''
        return int(self.simulation['log_lv'])

    @property
    def sim_lv(self):
        '''
        Level of complexity of the simulation from 0 - 5 

        :return: Complexity of the simulation
        :rtype: int
        '''
        return int(self.simulation['sim_lv'])
    
    @property
    def sound(self):
        return bool(self.simulation['sound'])
 