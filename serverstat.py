#!/usr/bin/env python3
# coding:utf-8
import utils
import requests

def get_server_stat(api_url):
    r = requests.get(api_url)
    stats = utils.load_json_str(r.text)
    update_time_unix = utils.str_to_num(stats.get('updated'))
    if not update_time_unix:
        update_time = 'unknown'
    else:
        update_time = utils.get_time_str(update_time_unix) + ' UTC'
    try:
        stat = stats.get('servers')[4]
    except TypeError:
        stat_str = 'unknown'
    else:
        network_rx, rx_measure = utils.select_max_measure(utils.str_to_num(stat.get('network_rx')))
        network_tx, tx_measure = utils.select_max_measure(utils.str_to_num(stat.get('network_tx')))
        network_in = utils.str_to_num(stat.get('network_in')) // utils.GB
        network_out = utils.str_to_num(stat.get('network_out')) // utils.GB
        memory_total = utils.str_to_num(stat.get('memory_total')) // utils.MB
        memory_used = utils.str_to_num(stat.get('memory_used')) // utils.MB
        stat_str = 'mem: %dM / %dM\nnetwork: %.1f%s / %.1f%s\nbandwith: %dG / %dG\n' %(
            memory_used, memory_total,
            network_tx, tx_measure, network_rx, rx_measure,
            network_out, network_in
            )
    return stat_str, update_time