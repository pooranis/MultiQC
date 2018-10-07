#!/usr/bin/env python3

import logging
import re
from collections import OrderedDict

from multiqc import config
from multiqc.modules.base_module import BaseMultiqcModule
from multiqc.plots import bargraph, linegraph


# Initialize log
log = logging.getLogger(__name__)

class MultiqcModule(BaseMultiqcModule):
    """FLASh MultiQC module"""
    def __init__(self):
        # Initialise the parent object
        super(MultiqcModule, self).__init__(
            name='FLASh',
            anchor='flash',
            href="https://ccb.jhu.edu/software/FLASH/",
            info="is a very fast and accurate software tool to merge paired-end reads from"\
            " next-generation sequencing experiments.")
        
        # Find all log files with flash msgs
        self.flash_data = OrderedDict()
        for logfile in self.find_log_files('flash/log'):
            self.flash_data.update(self.parse_flash_log(logfile))
            
        # ignore sample names
        self.flash_data = self.ignore_samples(self.flash_data)

        try:
            if not self.flash_data:
                raise
            log.info("Found %d log reports", len(self.flash_data))

            self.stats_table(self.flash_data)

            self.add_section(
                name='Read combination statistics',
                anchor='flash-bargraph',
                description='FLASh',
                helptext='help',
                plot=self.summary_plot(self.flash_data))
        except:
            pass

        ## parse histograms if user option is set
        self.flash_hist = None
        hist_config = getattr(config, 'flash', {}).get('hist', False)
        if hist_config:
             self.flash_hist = self.hist_results()

        # can't find any suitable logs
        if not self.flash_data and not self.flash_hist:
            raise UserWarning

    @staticmethod
    def split_log(f):
        """split concat log into individual samples"""
        flashpatt = re.compile(
            r'\[FLASH\] Fast Length Adjustment of SHort reads\n(.+?)\[FLASH\] FLASH', flags=re.DOTALL)
        return flashpatt.findall(f)

    @staticmethod
    def get_field(field, slog):
        """parse sample log for field"""
        field += r'\:\s+([\d\.]+)'
        match = re.search(field, slog)
        if match:
            return float(match[1])
        return 0

    def clean_pe_name(self, nlog, root):
        """additional name cleaning for paired end data"""
        use_output_name = getattr(config, 'flash', {}).get('use_output_name', False)
        if use_output_name:
            name = re.search(r'Output files\:\n\[FLASH\]\s+(.+?)\n', nlog)
            if not name:
                return None
            name = re.sub('.extendedFrags', '', name[1])
        else:
            name = re.search(r'Input files\:\n\[FLASH\]\s+(.+?)\n', nlog)
            if not name:
                return None
            name = name[1]
        name = self.clean_s_name(name, root)
        return name

    def parse_flash_log(self, logf):
        """parse flash logs"""
        data = OrderedDict()
        samplelogs = self.split_log(logf['f'])
        for slog in samplelogs:
            sample = dict()
            ## Sample name ##
            s_name = self.clean_pe_name(slog, logf['root'])
            if s_name is None:
                continue
            sample['s_name'] = s_name

            ## Log attributes ##
            sample['totalpairs'] = self.get_field('Total pairs', slog)
            sample['discpairs'] = self.get_field('Discarded pairs', slog)
            sample['combopairs'] = self.get_field('Combined pairs', slog)
            sample['percdisc'] = self.get_field('Percent Discarded', slog)
            sample['inniepairs'] = self.get_field('Innie pairs', slog)
            sample['outiepairs'] = self.get_field('Outie pairs', slog)
            sample['uncombopairs'] = self.get_field('Uncombined pairs', slog)
            sample['perccombo'] = self.get_field('Percent combined', slog)

            data[s_name] = sample
        return data

    def stats_table(self, data):
        """Add percent combined to general stats table"""
        headers = OrderedDict()
        headers['combopairs'] = {
            'title': 'Combined pairs',
            'description': 'Num reads combined',
            'shared_key': 'read_count',
            'scale': False
        }
        headers['perccombo'] = {
            'title': '% Combined',
            'description': '% reads combined',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'PiYG'
        }
        self.general_stats_addcols(data, headers)

    @staticmethod
    def summary_plot(data):
        """Barplot of combined pairs"""
        cats = OrderedDict()
        cats = {
            'inniepairs': {
                'name': 'Combined pairs',
                'color': '#E6A0C4'
            },
            'outiepairs': {
                'name': 'Combined outie pairs',
                'color': '#C6CDF7'
            },
            'uncombopairs': {
                'name': 'Uncombined pairs',
                'color': '#7294D4'
            },
            'discpairs': {
                'name': 'Discarded pairs',
                'color': '#D8A499'
            }
        }
        splotconfig = {'id': 'flash_combo_stats_plot', 'title': 'FLASh: Read combination statistics'}
        return bargraph.plot(data, cats, splotconfig)

    @staticmethod
    def parse_hist_files(hf):
        """parse histogram files"""
        data = dict()
        for l in hf['f'].splitlines():
            s = l.split()
            if s[1]:
                data[int(s[0])] = float(s[1])
        tot = sum(data.values(), 0)/100
        if tot == 0:
            return None
#        data =  {k: v / tot for k, v in data.items()}
        s_name = re.sub('\.hist$', '', hf['s_name'])
        nameddata = dict()
        nameddata[s_name] = data
        return(nameddata)

    def hist_results(self):
        """process flash numeric histograms"""
        self.hist_data = OrderedDict()
        for histfile in self.find_log_files('flash/hist'):
            self.hist_data.update(self.parse_hist_files(histfile))

        # ignore sample names
        self.hist_data = self.ignore_samples(self.hist_data)

        try:
            if not self.hist_data:
                raise
            log.info("Found %d histogram reports", len(self.hist_data))
            
            self.add_section(
                name='Frequency polygons of merged read lengths',
                anchor='flash-histogram',
                description='FLASh',
                helptext='help',
                plot=linegraph.plot(self.hist_data))
        except:
            pass
        return(len(self.hist_data))

