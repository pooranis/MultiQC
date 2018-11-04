#!/usr/bin/env python3

import logging
import pytest
from flash import MultiqcModule as fl

def test_extra_colors():
    assert fl.get_colors(5) ==  ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]

def test_whole_colors():
    assert fl.get_colors(44) == ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
                      "#CC79A7","#001F3F", "#0074D9", "#7FDBFF", "#39CCCC", "#3D9970", "#2ECC40",
                       "#01FF70", "#FFDC00", "#FF851B", "#FF4136", "#F012BE", "#B10DC9",
                                 "#85144B", "#AAAAAA", "#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
                      "#CC79A7","#001F3F", "#0074D9", "#7FDBFF", "#39CCCC", "#3D9970", "#2ECC40",
                       "#01FF70", "#FFDC00", "#FF851B", "#FF4136", "#F012BE", "#B10DC9",
                       "#85144B", "#AAAAAA", "#000000"]

def test_whole_extra_colors():
    assert fl.get_colors(25) == ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00",
                      "#CC79A7","#001F3F", "#0074D9", "#7FDBFF", "#39CCCC", "#3D9970", "#2ECC40",
                       "#01FF70", "#FFDC00", "#FF851B", "#FF4136", "#F012BE", "#B10DC9",
                                 "#85144B", "#AAAAAA", "#000000", "#E69F00", "#56B4E9", "#009E73"]

@pytest.fixture
def bad_histfile():
    return {'fn': '22057.hist', 'root': './testdata/temp/', 'filesize': 263, 's_name': '22057', 'f': '200\tb\n201\t6\n203\t2\n205\t1\n217\t1\n237\t2\n238\t1\n241\t1\n249\t1\n265\t1\n266\t1\n270\t1\n281\t1\n284\t5\n285\t4\n286\t6\n287\t4\n288\t14\n289\t45\n290\t216\n291\t8418\n292\t15297\n293\t279\n294\t6\n295\t1\n296\t1\n327\t1\n377\t1\n388\t1\n419\t3\n420\t2\n425\t1\n427\t1\n432\t2\n451\t1\n457\t1\n464\t1\n484\t4\n497\t1\n511\t1\n512\t2\n'}

@pytest.fixture
def good_histfile():
    return {'fn': '22057.hist', 'root': './testdata/temp/', 'filesize': 263, 's_name': '22057', 'f': '200\t5\n201\t6\n203\t2\n205\t1\n217\t1\n237\t2\n238\t1\n241\t1\n249\t1\n265\t1\n266\t1\n270\t1\n281\t1\n284\t5\n285\t4\n286\t6\n287\t4\n288\t14\n289\t45\n290\t216\n291\t8418\n292\t15297\n293\t279\n294\t6\n295\t1\n296\t1\n327\t1\n377\t1\n388\t1\n419\t3\n420\t2\n425\t1\n427\t1\n432\t2\n451\t1\n457\t1\n464\t1\n484\t4\n497\t1\n511\t1\n512\t2\n'}

def test_parse_hist_logerror(caplog):
    fl.parse_hist_files(bad_histfile())
    assert 'Error' in caplog.text

def test_parse_hist_error():
    assert fl.parse_hist_files(bad_histfile()) == dict()
