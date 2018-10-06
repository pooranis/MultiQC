#!/usr/bin/env python3

import logging
import re
from collections import OrderedDict

from multiqc import config
from multiqc.modules.base_module import BaseMultiqcModule
from multiqc.plots import bargraph

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
            " next-generation sequencing experiments."
        )

        # Find all files with flash msgs
        self.flash_data = OrderedDict()
        for logfile in self.find_log_files('flash'):
            self.flash_data.update(self.parse_flash_log(logfile))

        # ignore sample names
        self.flash_data = self.ignore_samples(self.flash_data)

        # can't find any suitable logs
        if not self.flash_data:
            raise UserWarning

        log.info("Found %d reports", len(self.flash_data))

        self.stats_table(self.flash_data)

        self.add_section(
            name='Read combination statistics',
            anchor='flash-bargraph',
            description='FLASh',
            helptext='help',
            plot=self.summary_plot(self.flash_data))

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
        output_as_s_name = getattr(config, 'flash', {}).get('output_as_s_name', False)
        if output_as_s_name:
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
        name_clean_regex = getattr(config, 'flash', {}).get('name_clean_regex', None)
        if name_clean_regex is not None:
            return re.sub(name_clean_regex, '', name)
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
            print(s_name)
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
        """Add percent combined to general stats table """
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
