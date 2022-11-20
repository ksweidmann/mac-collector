import logging
import re
import datetime
import json
import paramiko
import argumet_parser

from netmiko import ConnectHandler


def prepare():
    import os
    try:
        os.mkdir('./results')
    except FileExistsError:
        pass

def colon_mac(address):
    mac = list()
    two = re.compile('(..)')
    
    if ':' in address:
        return address
    
    if '.' in address:
        splitted = address.split('.')
    
    if '-' in address:
        splitted = address.split('-')
        
    for i in splitted:
        for x in two.findall(i):
            mac.append(x)

    return ":".join(mac)

def dot_mac(address):
    mac = ""
    if '.' in address:
        return address
    
    if ':' in address:
        mac = address.split(':')
        mac = [ mac[0:2], mac[2:4], mac[4:6] ]
        mac = [ "".join(x) for x in mac ]
        mac = ".".join(mac)

    if '-' in address:
        mac = address.replace('-', '.')
        
    return mac

def hyphen_mac(address):
    mac = ""
    if '-' in address:
        return address
    
    if ':' in address:
        mac = address.split(':')
        mac = [ mac[0:2], mac[2:4], mac[4:6] ]
        mac = [ "".join(x) for x in mac ]
        mac = "-".join(mac)

    if '.' in address:
        mac = address.replace('.', '-')
        
    return mac


def add_spaces(text, length):
    if len(text) < int(length):
        while True:
            if len(text) >= int(length):
                break
            text += " "
    return text

class MacCollector:
    def __init__(self, username, hostname, os, key_path):
        port = 22
        if ':' in hostname:
            port = int(hostname.split(":")[1])
            hostname = hostname.split(":")[0]
            
        self.data = str()
        self.pairs = list()

        self.hostname = hostname
        self.username = username
        self.port = port
        self.os = os
            
        self.conn_data = {
            'device_type': self.os,
            'host':   self.hostname,
            'username': self.username,
            'port' : self.port,
            'key_file': key_path,
            'allow_agent': True,
            'conn_timeout': 5
        }
        self.get_data()
        self.parse_data()
        self.save_data()

    def get_data(self):
        commands = {
            "mikrotik_routeros": [
                '/ip/arp/print without-paging proplist=address,mac-address',
            ],
            "cisco": [
                'term len 0',
                'show arp'
            ],
            "huawei": [
                'mmi-mode enable',
                'display arp'
            ]
            
        }

        log.info('Trying connect to %s' % self.hostname)
        try:
            device = ConnectHandler(**self.conn_data)
        except paramiko.ssh_exception.SSHException:
            self.conn_data['disabled_algorithms'] = {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
            device = ConnectHandler(**self.conn_data)
        
        for cmd in commands[self.os]:
            log.info('Sending command "%s"' % cmd)
            self.data += device.send_command(cmd)
        log.info('Host %s successful collected' % self.hostname)

    def parse_data(self):
        pair = {
            "mikrotik_routeros": re.compile('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))'),
            "huawei": re.compile('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>([0-9A-Fa-f]){4}-([0-9A-Fa-f]){4}-([0-9A-Fa-f]){4})'),
            "cisco": re.compile('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*(?P<mac>([0-9A-Fa-f]){4}\.([0-9A-Fa-f]){4}\.([0-9A-Fa-f]){4})')
        }
        for line in self.data.split('\n'):
            try:
                log.debug('Parse line: %s' % line)
                ip = pair[self.os].search(line).group("ip")
                mac = pair[self.os].search(line).group("mac")
                log.debug('Parsed info %s %s' % (ip, mac))
            except: continue
            else:
                self.pairs.append({"ip":ip,"mac":mac})
        
        self.data = ""
        self.data += "%s \n" % datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.data += "=" * 80 + "\n"
        for x in self.pairs:
            self.data += "{} {} {} - {} {}\n".format(
                colon_mac(x['mac']),
                hyphen_mac(x['mac']),
                dot_mac(x['mac']),
                add_spaces(x['ip'], 15),
                x['ip'].replace('.', '-')
            )
        self.data += "\n"
    
    def save_data(self):
        txt_file = "results/macs-%s.txt" % self.hostname
        log.debug('Store file %s' % txt_file)
        with open(txt_file, "wb") as f:
            f.write(self.data.encode())

        if STORE_JSON:
            json_file = 'results/%s.json' % self.hostname
            log.debug('Store json file %s' % json_file)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.pairs, f)

if __name__ == "__main__":
    log_format = '%(asctime)s - %(name)s %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format,
                        datefmt='%d-%b-%y %H:%M:%S',
                        handlers=[
                            logging.FileHandler("collector.log"),
                            logging.StreamHandler()
                        ]
    )
    log = logging.getLogger("Collector")
    parser = argumet_parser.parser()
    args = parser.parse_args()
    log_levels = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "CRITICAL": logging.CRITICAL
    }
    log.setLevel(log_levels[args.log_level])
    STORE_JSON = args.store_json
    prepare()
    for host in args.hosts:
        collector = MacCollector(username=args.user,
                                hostname=host,
                                os=args.type,
                                key_path=args.key)
