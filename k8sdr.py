#!/usr/bin/env python
"""
Author: Kapil Arora
Github: @kapilarora
"""
import ConfigParser
import sys
import os.path
import io
import logging
from k8s_client import K8SClient
from time import strftime

def main():
    config_file_name = 'k8s_solidfire_dr.cfg'
    try:
        config_file_name = sys.argv[2]
        print 'This script will use the following config file for execution:'
        print config_file_name
    except IndexError:
        print 'No config name provided, using the default name k8s_solidfire_dr.cfg '

    # check if config file exist
    if not os.path.isfile(config_file_name):
        print 'Error: Config file does not exist!'
        sys.exit('Config file does not exist!')

    config = ConfigParser.ConfigParser()
    # reading config file
    config.read(io.BytesIO(config_file_name))
    default_config = dict(config.items('default'))

    # getting log level from the config file
    log_level = default_config['log_level']
    level = _get_Log_level(log_level)
    # initializing logger
    log_filename = strftime("k8s_solidfire_dr_%Y%m%d%H%M%S.log")
    logging.basicConfig(filename=log_filename,
                        level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    operation = None

    try:
        operation = sys.argv[1]
    except IndexError:
        print 'This script needs an operation as argument.'

    if operation == 'start' or operation == 'failover' or operation == 'failback' or operation == 'cleanup':
        logging.info('Requested operation is : %s', operation)
    else:
        if operation == None:
            print 'No operation provided!'
        elif operation != 'help':
            print 'Invalid operation: ' + operation
        print_help()
        exit

    # @TODO change no-execute to env variable
    # no-execute? checking if no_execute is set. We won't execute any apis..just list the operations
    no_execute_str = default_config['no_execute']
    if no_execute_str.lower() == 'true':
        no_execute = True
    else:
        no_execute = False

    k8s_config = dict(config.items('k8s'))
    primary_k8s_kubeconfig = k8s_config['primary_k8s_kubeconfig']
    secondary_k8s_kubeconfig = k8s_config['secondary_k8s_kubeconfig']
    namespaces = k8s_config['namespaces'].split(',')
    if len(namespaces) == 1 and namespaces[0] == '*':
        all_namespaces = True
        logging.info('You have selected all namespaces')
    k8s_primary = K8SClient(primary_k8s_kubeconfig, no_execute)
    k8s_secondary = K8SClient(secondary_k8s_kubeconfig, no_execute)
    secondary_pvc_suffix = k8s_config['secondary_pvc_suffix']


    if all_namespaces:
        if operation == "start":
            start(k8s_primary, k8s_secondary, secondary_pvc_suffix)


def start(k8s_primary, k8s_secondary, secondary_pvc_suffix):

    #read all secondary pvcs and create a name array
    secondary_pvcs = k8s_secondary.get_all_pvc()
    secondary_pvc_names = []
    for pvc in secondary_pvcs.items:
        secondary_pvc_names.append(pvc.metadata.name)
    logging.info('list of secondary pvc names: %s', secondary_pvc_names)

    #read all primary pvcs and create duplicate on secondary if it doesnt already exist
    primary_pvcs = k8s_primary.get_all_pvc()
    for pvc in primary_pvcs.items:
        secondary_pvc_name = pvc.metadata.name + secondary_pvc_suffix
        logging.info('checking if pvc %s is duplicated on secondary as secondary_pvc_name',
                     pvc.metadata.name, secondary_pvc_name)
        if secondary_pvc_name in secondary_pvc_names:
           print 'pvc '+ pvc.metadata.name + ' is not yet on secondary'















def print_help():
    print '###### HELP ######'
    print 'Valid Operations:'
    print '1. start - Start Replication of Volumes'
    print '2. failover - Failover to Secondary Site'
    print '3. failback - Failback to Primary Site'
    print '4. cleanup - Cleanup all Secondary Volumes that do not exist on Primary'
    print '###### Sample commands ######'
    print 'python k8sdr.py start'
    print 'python k8sdr.py failover'
    print 'python k8sdr.py failback'
    print 'python k8sdr.py cleanup'
    print 'You can also provide a custom config file name as the second parameter, default is k8s-solidfire-dr.cfg'
    print '###### Sample commands with config file name ######'
    print 'python k8sdr.py start /path/to/dr_config1.cfg'
    print 'python k8sdr.py failover /path/to/dr_config1.cfg'




def _get_Log_level(log_level):
    '''

    :param log_level: str info/error/warn/debug
    :return: logging.level
    '''
    if log_level == 'info':
        level = logging.INFO
    elif log_level == 'error':
        level = logging.ERROR
    elif log_level == 'warn':
        level = logging.WARN
    else:
        level = logging.DEBUG
    return level


if __name__ == '__main__':
    main()
