#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
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
import limesdr




class RX_LIME(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.soft_decoding = soft_decoding = True
        self.sf = sf = 7
        self.samp_rate_rtl = samp_rate_rtl = 1200000
        self.samp_rate = samp_rate = 500000
        self.out_file = out_file = '/home/vcarv/TCC/pratica/rx_data/1/rx_7_125000/pqp.dat'
        self.impl_head = impl_head = False
        self.has_crc = has_crc = True
        self.cr = cr = 1
        self.center_freq = center_freq = 915e6
        self.bw = bw = 125000

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_char, 1, 'tcp://127.0.0.1:54321', 1000, False, -1, '')
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
        self.limesdr_source_0 = limesdr.source('', 0, '')
        self.limesdr_source_0.set_sample_rate(samp_rate_rtl)
        self.limesdr_source_0.set_center_freq(center_freq, 0)
        self.limesdr_source_0.set_bandwidth(5e6, 0)
        self.limesdr_source_0.set_gain(30,0)
        self.limesdr_source_0.set_antenna(255,0)
        self.limesdr_source_0.calibrate(5e6, 0)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_char*1,int(has_crc),0)
        self.blocks_selector_0.set_enabled(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_1, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.blocks_selector_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.limesdr_source_0, 0), (self.rational_resampler_xxx_0, 0))
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


    def get_soft_decoding(self):
        return self.soft_decoding

    def set_soft_decoding(self, soft_decoding):
        self.soft_decoding = soft_decoding

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf

    def get_samp_rate_rtl(self):
        return self.samp_rate_rtl

    def set_samp_rate_rtl(self, samp_rate_rtl):
        self.samp_rate_rtl = samp_rate_rtl

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_out_file(self):
        return self.out_file

    def set_out_file(self, out_file):
        self.out_file = out_file

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc
        self.blocks_selector_0.set_input_index(int(self.has_crc))

    def get_cr(self):
        return self.cr

    def set_cr(self, cr):
        self.cr = cr

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.limesdr_source_0.set_center_freq(self.center_freq, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw




def main(top_block_cls=RX_LIME, options=None):
    tb = top_block_cls()

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
