# mac-collector

mac-collector is app for collecting arp tables from cisco, huawei and mikrotik routers

## Installation


```bash
git clone git@github.com:ksweidmann/mac-collector.git
cd mac-collector
python -m venv .
source bin/activate
pip install -U -r requirements.txt
```

## Usage

```bash
cd mac-collector
source bin/activate
python collector.py -h
python collector.py --user admin --key /path/to/ssh.key --hosts 192.168.1.1:22 --type routeros
```