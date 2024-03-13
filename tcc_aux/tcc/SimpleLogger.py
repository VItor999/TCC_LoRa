import logging as lg
class SimpleLogger:

    '''
    Simples class for basic logging during simulation
    '''
    def __init__(self, level=lg.INFO, global_log_path = './log.txt'):
        self.global_logger = lg.getLogger('global')
        self.local_logger = lg.getLogger('local')
        self.global_logger.setLevel(level)
        self.local_logger.setLevel(level)

        # Create a console handler
        console_handler = lg.StreamHandler()
        console_handler.setLevel(lg.INFO)

        # Create a formatter and set it for the handlers
        self.formatter = lg.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(self.formatter)

        # Add handlers to the logger
        self.global_logger.addHandler(console_handler)   
