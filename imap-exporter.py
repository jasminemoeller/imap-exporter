#!/usr/bin/env python3
import imaplib
import re
from prometheus_client import start_http_server, Gauge
import time
import yaml
import argparse

quota_used = Gauge('imap_quota_used_kb', 'IMAP quota used in KB', ['account'])
quota_limit = Gauge('imap_quota_limit_kb', 'IMAP quota limit in KB', ['account'])
imap_up = Gauge('imap_up', 'IMAP connection status', ['account'])

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def check_quota(account_config):
    account_name = account_config['name']
    server = account_config['server']
    port = account_config.get('port', 993)
    username = account_config['username']
    password = account_config['password']
    
    try:
        print(f"Checking quota for {account_name} ({username})...")
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)
        
        typ, quota_data = mail.getquotaroot('INBOX')
        
        # Flatten nested list structure
        quota_str = ''
        if isinstance(quota_data, list):
            for item in quota_data:
                if isinstance(item, bytes):
                    quota_str += item.decode() + ' '
                elif isinstance(item, str):
                    quota_str += item + ' '
                elif isinstance(item, list):
                    for subitem in item:
                        if isinstance(subitem, bytes):
                            quota_str += subitem.decode() + ' '
                        elif isinstance(subitem, str):
                            quota_str += subitem + ' '
        
        match = re.search(r'STORAGE (\d+) (\d+)', quota_str)
        if match:
            used = int(match.group(1))
            limit = int(match.group(2))
            
            quota_used.labels(account=account_name).set(used)
            quota_limit.labels(account=account_name).set(limit)
            print(f"{account_name}: {used}/{limit} KB ({used/limit*100:.1f}%)")
        else:
            print(f"WARNING - Could not parse quota for {account_name}")
        
        mail.logout()
        imap_up.labels(account=account_name).set(1)
        
    except Exception as e:
        print(f"Error checking {account_name}: {e}")
        imap_up.labels(account=account_name).set(0)

def check_all_accounts(config):
    for account in config['accounts']:
        check_quota(account)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IMAP Quota Exporter for Prometheus')
    parser.add_argument('--config', '-c', 
                       default='/app/config.yml',
                       help='Path to config file (default: /app/config.yml)')
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    # Get check interval from config, default to 900 seconds (15 minutes)
    check_interval = config.get('check_interval', 900)
    
    start_http_server(9226)
    print(f"IMAP exporter on :9226")
    print(f"Monitoring {len(config['accounts'])} accounts")
    print(f"Check interval: {check_interval} seconds ({check_interval/60:.1f} minutes)")
    
    while True:
        check_all_accounts(config)
        time.sleep(check_interval)