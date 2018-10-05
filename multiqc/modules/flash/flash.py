#!/usr/bin/env python3

import logging
from multiqc.modules.base_module import BaseMultiqcModule
import re
from collections import OrderedDict

## Initialize log
log = logging.getLogger(__name__)


class Sample(dict):
    """simple dictionary class"""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(name)


class MultiqcModule(BaseMultiqcModule):
    def __init__(self):
        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='FLASh', anchor='flash',
        href="https://ccb.jhu.edu/software/FLASH/",
        info="is a very fast and accurate software tool to merge paired-end reads from next-generation sequencing experiments.")

        # Find all files with flash msgs
        self.flash_data = OrderedDict()
        for logfile in self.find_log_files('flash'):
             self.flash_data.update(self.parse_flash_log(logfile))

        
        # ignore sample names
        self.flash_data = self.ignore_samples(self.flash_data)

        # can't find any suitable files
        if len(self.flash_data) == 0:
            raise UserWarning

        print(next(iter(self.flash_data.values())))
        log.info("Found {} reports".format(len(self.flash_data)))

        self.stats_table(self.flash_data)
    
    @staticmethod   
    def split_log(f):
        """split concat log into individual samples"""
        flashpatt = re.compile('\[FLASH\] Fast Length Adjustment of SHort reads\n(.+?)\[FLASH\] FLASH', flags=re.DOTALL)
        return flashpatt.findall(f)

    @staticmethod
    def get_field(field, slog):
        """parse sample log for field"""
        field += '\:\s+([\d\.]+)'
        match = re.search(field, slog)
        if match:
            return float(match[1])
        return None

    def parse_flash_log(self, logf):
        data = OrderedDict()
        samplelogs = self.split_log(logf['f'])
        for slog in samplelogs:
            sample = Sample()
            ## Sample name ##
            s_name = re.search('Input files\:\n\[FLASH\]\s+(.+?)\n', slog)
            if not s_name:
                continue
            s_name = self.clean_s_name(s_name[1], logf['root'])
            print(s_name)
            sample.s_name = s_name
            
            ## Log attributes ##
            sample.totalpairs = self.get_field('Total pairs', slog)
            sample.discpairs = self.get_field('Discarded pairs', slog)
            sample.combopairs = self.get_field('Combined pairs', slog)
            sample.percdisc = self.get_field('Percent Discarded', slog)
            sample.inniepairs = self.get_field('Innie pairs', slog)
            sample.outiepairs = self.get_field('Outie pairs', slog)
            sample.uncombopairs = self.get_field('Uncombined pairs', slog)
            sample.perccombo = self.get_field('Percent combined', slog)
            
            data[s_name] = sample
        return data


    def stats_table(self, data):
        """ Add percent combined to general stats table """
        headers = OrderedDict()
        headers['perccombo'] = {
            'title': '% Combined',
            'description': '% reads combined by FLASh',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'PiYG'
            }
        self.general_stats_addcols(data, headers)

