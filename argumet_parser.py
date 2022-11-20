import argparse

def parser():
    parser = argparse.ArgumentParser(description='Collect and parse arp tables from huawei, cisco and mikrotik', add_help=True)
    parser.add_argument('-t', '--type',
        choices=['huawei', 'cisco', 'mikrotik_routeros'],
        help='router type, huawei, cisco or routeros',
        required=True
    )
    parser.add_argument('-u', '--user',
        help='username for login',
        required=True
    )
    parser.add_argument('-i', '--key',
        help='path to keyfile',
        required=False
    )
    parser.add_argument('-H','--hosts',
        help="hosts list separated by space",
        required=True,
        nargs='+',
        default=[]
    )
    parser.add_argument('--store-json',
        help='store jsonfile of arp table',
        required=False,
        action="store_true",
        default=False,
        dest="store_json"
    )
    parser.add_argument('--log-level',
        help="Set logging level",
        choices=["INFO", "DEBUG", "WARNING", "CRITICAL"],
        default="CRITICAL",
        dest="log_level"
    )
    return parser