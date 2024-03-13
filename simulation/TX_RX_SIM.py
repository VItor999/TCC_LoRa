#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Tx Rx Sim
# Author: vcarv
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
import pmt
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.lora_sdr as lora_sdr




class TX_RX_SIM(gr.top_block):

    def __init__(self, bw=125000, center_freq=915000000, cr=1, has_crc=1, impl_head=0, in_file='/home/vcarv/TCC/test/tx_data/tx_text.txt', noise=0, noise_seed=42, out_file='/home/vcarv/TCC/test/rx_noise_0.dat', samp_rate=250000, sf=7, soft_decoding=0, taps_str=['1.0+0.0j']):
        gr.top_block.__init__(self, "Tx Rx Sim", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.bw = bw
        self.center_freq = center_freq
        self.cr = cr
        self.has_crc = has_crc
        self.impl_head = impl_head
        self.in_file = in_file
        self.noise = noise
        self.noise_seed = noise_seed
        self.out_file = out_file
        self.samp_rate = samp_rate
        self.sf = sf
        self.soft_decoding = soft_decoding
        self.taps_str = taps_str

        ##################################################
        # Variables
        ##################################################
        self.taps = taps = [complex(tap) for tap in taps_str]

        ##################################################
        # Blocks
        ##################################################
        self.lora_sdr_whitening_0 = lora_sdr.whitening(False,',')
        self.lora_sdr_modulate_0 = lora_sdr.modulate(sf, samp_rate, bw, [8,16], int(20*2**sf*samp_rate/bw),8)
        self.lora_sdr_modulate_0.set_min_output_buffer(10000000)
        self.lora_sdr_interleaver_0 = lora_sdr.interleaver(cr, sf, 0, 125000)
        self.lora_sdr_header_decoder_1 = lora_sdr.header_decoder(bool(impl_head), 3, 255, False, 0, False)
        self.lora_sdr_header_0 = lora_sdr.header(bool(impl_head), bool(has_crc), cr)
        self.lora_sdr_hamming_enc_0 = lora_sdr.hamming_enc(cr, sf)
        self.lora_sdr_hamming_dec_0 = lora_sdr.hamming_dec(soft_decoding)
        self.lora_sdr_gray_mapping_0 = lora_sdr.gray_mapping( bool(soft_decoding))
        self.lora_sdr_gray_demap_0 = lora_sdr.gray_demap(sf)
        self.lora_sdr_frame_sync_0 = lora_sdr.frame_sync(int(center_freq), bw, sf, impl_head, [18], int(samp_rate/bw),8)
        self.lora_sdr_fft_demod_0 = lora_sdr.fft_demod( soft_decoding, True)
        self.lora_sdr_dewhitening_0 = lora_sdr.dewhitening()
        self.lora_sdr_deinterleaver_0 = lora_sdr.deinterleaver( soft_decoding)
        self.lora_sdr_crc_verif_0 = lora_sdr.crc_verif( False, False)
        self.lora_sdr_add_crc_0 = lora_sdr.add_crc(bool(has_crc))
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=noise,
            frequency_offset=0.0,
            epsilon=1.0,
            taps=taps,
            noise_seed=noise_seed,
            block_tags=False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_char*1,has_crc,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_file_source_1 = blocks.file_source(gr.sizeof_char*1, in_file, False, 0, 0)
        self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_char*1, out_file, False)
        self.blocks_file_sink_0_0.set_unbuffered(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_sdr_header_decoder_1, 'frame_info'), (self.lora_sdr_frame_sync_0, 'frame_info'))
        self.connect((self.blocks_file_source_1, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_file_sink_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.lora_sdr_whitening_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.lora_sdr_frame_sync_0, 0))
        self.connect((self.lora_sdr_add_crc_0, 0), (self.lora_sdr_hamming_enc_0, 0))
        self.connect((self.lora_sdr_crc_verif_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.lora_sdr_deinterleaver_0, 0), (self.lora_sdr_hamming_dec_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.lora_sdr_dewhitening_0, 0), (self.lora_sdr_crc_verif_0, 0))
        self.connect((self.lora_sdr_fft_demod_0, 0), (self.lora_sdr_gray_mapping_0, 0))
        self.connect((self.lora_sdr_frame_sync_0, 0), (self.lora_sdr_fft_demod_0, 0))
        self.connect((self.lora_sdr_gray_demap_0, 0), (self.lora_sdr_modulate_0, 0))
        self.connect((self.lora_sdr_gray_mapping_0, 0), (self.lora_sdr_deinterleaver_0, 0))
        self.connect((self.lora_sdr_hamming_dec_0, 0), (self.lora_sdr_header_decoder_1, 0))
        self.connect((self.lora_sdr_hamming_enc_0, 0), (self.lora_sdr_interleaver_0, 0))
        self.connect((self.lora_sdr_header_0, 0), (self.lora_sdr_add_crc_0, 0))
        self.connect((self.lora_sdr_header_decoder_1, 0), (self.lora_sdr_dewhitening_0, 0))
        self.connect((self.lora_sdr_interleaver_0, 0), (self.lora_sdr_gray_demap_0, 0))
        self.connect((self.lora_sdr_modulate_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.lora_sdr_whitening_0, 0), (self.lora_sdr_header_0, 0))


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
        self.lora_sdr_hamming_enc_0.set_cr(self.cr)
        self.lora_sdr_header_0.set_cr(self.cr)
        self.lora_sdr_interleaver_0.set_cr(self.cr)

    def get_has_crc(self):
        return self.has_crc

    def set_has_crc(self, has_crc):
        self.has_crc = has_crc
        self.blocks_selector_0.set_input_index(self.has_crc)

    def get_impl_head(self):
        return self.impl_head

    def set_impl_head(self, impl_head):
        self.impl_head = impl_head

    def get_in_file(self):
        return self.in_file

    def set_in_file(self, in_file):
        self.in_file = in_file
        self.blocks_file_source_1.open(self.in_file, False)

    def get_noise(self):
        return self.noise

    def set_noise(self, noise):
        self.noise = noise
        self.channels_channel_model_0.set_noise_voltage(self.noise)

    def get_noise_seed(self):
        return self.noise_seed

    def set_noise_seed(self, noise_seed):
        self.noise_seed = noise_seed

    def get_out_file(self):
        return self.out_file

    def set_out_file(self, out_file):
        self.out_file = out_file
        self.blocks_file_sink_0_0.open(self.out_file)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

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

    def get_taps_str(self):
        return self.taps_str

    def set_taps_str(self, taps_str):
        self.taps_str = taps_str
        self.set_taps([complex(tap) for tap in self.taps_str])

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.channels_channel_model_0.set_taps(self.taps)



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
        "--in-file", dest="in_file", type=str, default='/home/vcarv/TCC/test/tx_data/tx_text.txt',
        help="Set /home/vcarv/TCC/test/tx_data/tx_text.txt [default=%(default)r]")
    parser.add_argument(
        "--noise", dest="noise", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set noise [default=%(default)r]")
    parser.add_argument(
        "--noise-seed", dest="noise_seed", type=intx, default=42,
        help="Set noise_seed [default=%(default)r]")
    parser.add_argument(
        "--out-file", dest="out_file", type=str, default='/home/vcarv/TCC/test/rx_noise_0.dat',
        help="Set /home/vcarv/TCC/test/rx_noise_0.dat [default=%(default)r]")
    parser.add_argument(
        "--samp-rate", dest="samp_rate", type=intx, default=250000,
        help="Set samp_rate [default=%(default)r]")
    parser.add_argument(
        "--sf", dest="sf", type=intx, default=7,
        help="Set sf [default=%(default)r]")
    parser.add_argument(
        "--soft-decoding", dest="soft_decoding", type=intx, default=0,
        help="Set soft_decoding [default=%(default)r]")
    return parser


def main(top_block_cls=TX_RX_SIM, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(bw=options.bw, center_freq=options.center_freq, cr=options.cr, has_crc=options.has_crc, impl_head=options.impl_head, in_file=options.in_file, noise=options.noise, noise_seed=options.noise_seed, out_file=options.out_file, samp_rate=options.samp_rate, sf=options.sf, soft_decoding=options.soft_decoding)

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
