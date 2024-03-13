#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RX_RTL
# Author: Vitor Carvalho
# Description: GNURadio flowchart to recieve LoRa messages using RTL-SDR and send the recieved messages via socket.
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import gnuradio.lora_sdr as lora_sdr
import osmosdr
import time




class RX_RTL(gr.top_block):

    def __init__(self, bw=125000, center_freq=915000000, cr=1, has_crc=1, impl_head=0, out_file='/home/vcarv/TCC/practice/rx_SDR_tx_SDR/pqp.dat', samp_rate_0=250000, sf=9, soft_decoding=1):
        gr.top_block.__init__(self, "RX_RTL", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.center_freq = center_freq
        self.cr = cr
        self.has_crc = has_crc
        self.impl_head = impl_head
        self.out_file = out_file
        self.samp_rate_0 = samp_rate_0
        self.sf = sf
        self.soft_decoding = soft_decoding

        ##################################################
        # Variables
        ##################################################
        self.samp_rate_rtl = samp_rate_rtl = 1200000
        self.samp_rate = samp_rate = 500000

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:54321', 1000, False, -1, '')
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate_rtl)
        self.rtlsdr_source_0.set_center_freq(915e6, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(28, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=5,
                decimation=12,
                taps=[],
                fractional_bw=0)
        self.lora_sdr_header_decoder_1 = lora_sdr.header_decoder(False, 3, 255, False, 0, False)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( soft_decoding)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], int(samp_rate/bw),8)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, True)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        self.lora_sdr_crc_verif_0_0 = lora_sdr.crc_verif( False, False)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_char*1,int(has_crc),0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_char*1, out_file, False)
        self.blocks_file_sink_1.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_1, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.blocks_selector_0, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.lora_sdr_crc_verif_0_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_1, 0))
        self.connect((self.lora_sdr_header_decoder_1, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.rational_resampler_xxx_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc
        self.blocks_selector_0.set_input_index(int(self.has_crc))

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_out_file(self):
        return self.out_file

    def set_out_file(self, out_file):
        self.out_file = out_file
        self.blocks_file_sink_1.open(self.out_file)

    def get_samp_rate_0(self):
        return self.samp_rate_0

    def set_samp_rate_0(self, samp_rate_0):
        self.samp_rate_0 = samp_rate_0

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_samp_rate_rtl(self):
        return self.samp_rate_rtl

    def set_samp_rate_rtl(self, samp_rate_rtl):
        self.samp_rate_rtl = samp_rate_rtl
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate_rtl)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate



def argument_parser():
    description = 'GNURadio flowchart to recieve LoRa messages using RTL-SDR and send the recieved messages via socket.'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--bw", dest="bw", type=intx, default=125000,
        help="Set bw [default=%(default)r]")
    parser.add_argument(
        "--center-freq", dest="center_freq", type=intx, default=915000000,
        help="Set 915e6 [default=%(default)r]")
    parser.add_argument(
        "--cr", dest="cr", type=intx, default=1,
        help="Set cr [default=%(default)r]")
    parser.add_argument(
        "--has-crc", dest="has_crc", type=intx, default=1,
        help="Set has_crc [default=%(default)r]")
    parser.add_argument(
        "--impl-head", dest="impl_head", type=intx, default=0,
        help="Set impl_head [default=%(default)r]")
    parser.add_argument(
        "--out-file", dest="out_file", type=str, default='/home/vcarv/TCC/practice/rx_SDR_tx_SDR/pqp.dat',
        help="Set /home/vcarv/TCC/practice/rx_SDR_tx_SDR/pqp.dat [default=%(default)r]")
    parser.add_argument(
        "--samp-rate-0", dest="samp_rate_0", type=intx, default=250000,
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--sf", dest="sf", type=intx, default=9,
        help="Set sf [default=%(default)r]")
    parser.add_argument(
        "--soft-decoding", dest="soft_decoding", type=intx, default=1,
        help="Set soft_decoding [default=%(default)r]")
    return parser


def main(top_block_cls=RX_RTL, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bw=options.bw, center_freq=options.center_freq, cr=options.cr, has_crc=options.has_crc, impl_head=options.impl_head, out_file=options.out_file, samp_rate_0=options.samp_rate_0, sf=options.sf, soft_decoding=options.soft_decoding)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
