#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: noise generator
# Author: Vitor Carvalho
# Description: Simple flowchart to transmit an AWGN noise centered in a specific frequency.
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import limesdr




class noise_TX(gr.top_block):

    def __init__(self, center_freq=915000000, noise=1, noise_seed=42, samp_rate=4000000):
        gr.top_block.__init__(self, "noise generator", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.center_freq = center_freq
        self.noise = noise
        self.noise_seed = noise_seed
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.limesdr_sink_0 = limesdr.sink('', 0, '', '')
        self.limesdr_sink_0.set_sample_rate(samp_rate)
        self.limesdr_sink_0.set_center_freq(center_freq, 0)
        self.limesdr_sink_0.set_bandwidth(5e6,0)
        self.limesdr_sink_0.set_gain(50,0)
        self.limesdr_sink_0.set_antenna(255,0)
        self.limesdr_sink_0.calibrate(5e6, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1, noise_seed)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.limesdr_sink_0, 0))


    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.limesdr_sink_0.set_center_freq(self.center_freq, 0)

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise

    def get_noise_seed(self):
        return self.noise_seed

    def set_noise_seed(self, noise_seed):
        self.noise_seed = noise_seed

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate



def argument_parser():
    description = 'Simple flowchart to transmit an AWGN noise centered in a specific frequency.'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--center-freq", dest="center_freq", type=intx, default=915000000,
        help="Set 915e6 [default=%(default)r]")
    parser.add_argument(
        "--noise", dest="noise", type=eng_float, default=eng_notation.num_to_str(float(1)),
        help="Set noise [default=%(default)r]")
    parser.add_argument(
        "--noise-seed", dest="noise_seed", type=intx, default=42,
        help="Set noise_seed [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=intx, default=4000000,
        help="Set samp_rate [default=%(default)r]")
    return parser


def main(top_block_cls=noise_TX, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(center_freq=options.center_freq, noise=options.noise, noise_seed=options.noise_seed, samp_rate=options.samp_rate)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
