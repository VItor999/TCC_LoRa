#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr
import limesdr




class TX_SDR_LIME(gr.top_block):

    def __init__(self, bw=125000, center_freq=915000000, cr=1, has_crc=1, impl_head=0, in_file='/home/vcarv/TCC/practice/rx_SDR_tx_SDR/tx_data/tx_text.txt', samp_rate=250000, sf=9, soft_decoding=1):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.center_freq = center_freq
        self.cr = cr
        self.has_crc = has_crc
        self.impl_head = impl_head
        self.in_file = in_file
        self.samp_rate = samp_rate
        self.sf = sf
        self.soft_decoding = soft_decoding

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False,',')
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [8,16], int(20*2**sf*samp_rate/bw),8)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 0, 125000)
        self.lora_sdr_header_0 = lora_sdr.header(bool(impl_head), bool(has_crc), cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(bool(has_crc))
        self.limesdr_sink_0 = limesdr.sink('', 0, '', '')
        self.limesdr_sink_0.set_sample_rate(samp_rate)
        self.limesdr_sink_0.set_center_freq(center_freq, 0)
        self.limesdr_sink_0.set_bandwidth(5e6,0)
        self.limesdr_sink_0.set_gain(30,0)
        self.limesdr_sink_0.set_antenna(255,0)
        self.limesdr_sink_0.calibrate(5e6, 0)
        self.blocks_file_source_1 = blocks.file_source(gr.sizeof_char*1, in_file, False, 0, 0)
        self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_1, 0), (self.lora_sdr_whitening_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.limesdr_sink_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.limesdr_sink_0.set_center_freq(self.center_freq, 0)

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_in_file(self):
        return self.in_file

    def set_in_file(self, in_file):
        self.in_file = in_file
        self.blocks_file_source_1.open(self.in_file, False)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_sdr_gray_demap_0.set_sf(self.sf)
        self.lora_sdr_hamming_enc_0.set_sf(self.sf)
        self.lora_sdr_interleaver_0.set_sf(self.sf)
        self.lora_sdr_modulate_0.set_sf(self.sf)

    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding



def argument_parser():
    parser = ArgumentParser()
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
        "--in-file", dest="in_file", type=str, default='/home/vcarv/TCC/practice/rx_SDR_tx_SDR/tx_data/tx_text.txt',
        help="Set /home/vcarv/TCC/practice/rx_SDR_tx_SDR/tx_data/tx_text.txt [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=intx, default=250000,
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--sf", dest="sf", type=intx, default=9,
        help="Set sf [default=%(default)r]")
    parser.add_argument(
        "--soft-decoding", dest="soft_decoding", type=intx, default=1,
        help="Set soft_decoding [default=%(default)r]")
    return parser


def main(top_block_cls=TX_SDR_LIME, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bw=options.bw, center_freq=options.center_freq, cr=options.cr, has_crc=options.has_crc, impl_head=options.impl_head, in_file=options.in_file, samp_rate=options.samp_rate, sf=options.sf, soft_decoding=options.soft_decoding)

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
