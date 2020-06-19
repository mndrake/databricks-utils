#!python
# import functools
import json
import os
import time
import requests
import re
import urllib 
# import uuid
import configparser
import click

# Assumes that the Databricks CLI is installed and configured

class DatabricksAPI(object):
    """
    Databricks API request wrapper.
    doc page: https://docs.databricks.com/dev-tools/api/latest/index.html
    """
    host = None
    organization = None
    headers = None
    cluster = None

    def __init__(self, host, token):
        azure_pattern = r'^(https://[a-z0-9.]+)/\?o=([0-9]+)'
        azure_match = re.match(azure_pattern, host)
        if azure_match:
            matches = azure_match.groups()
            self.host = matches[0]
            self.organization = matches[1]
        else:
            self.host = host
        self.headers = {'Authorization': f'Bearer {token}'}

    def request(self, route, params=None, body=None):
        url = urllib.parse.urljoin(self.host, os.path.join('api', route))
        if body is None:
            response = requests.get(url, headers=self.headers, params=params)
        else:
            response = requests.post(url, headers=self.headers, json=body)
        response.raise_for_status()
        return response.json()

    def cluster_create(self, definition):
        self.cluster = self.request('2.0/clusters/create', body=definition)
        return True

    def cluster_state(self):
        cluster_status=self.request('2.0/clusters/get', params=self.cluster)
        return cluster_status['state']

    def install_libraries(self, libraries):
        self.request('2.0/libraries/install', body={**self.cluster, **{'libraries': libraries}})
        return True



@click.command()
@click.option('--profile', default='DEFAULT', help='Databricks CLI profile')
@click.option('--config', prompt='cluster config file', help='Cluster JSON config and libraries')
def create_cluster(profile=None, config=None):
    cluster_config = json.load(open(config))

    # retrieve databricks config for the profile
    cli_config = configparser.ConfigParser()
    cli_config.read(os.path.expanduser('~/.databrickscfg'))
    profile_config = cli_config[profile]
    
    # set databricks constants for the profile
    api = DatabricksAPI(profile_config['host'], profile_config['token'])

    click.echo(api.host)

    # create cluster
    api.cluster_create(cluster_config['cluster'])

    # wait for cluster to start
    cluster_pending = True

    while cluster_pending:
        click.echo('waiting for cluster to start ....')
        time.sleep(30)
        cluster_pending = api.cluster_state() == 'PENDING'

    click.echo('installing libraries...')
    # install libraries
    api.install_libraries(cluster_config['libraries'])


if __name__ == '__main__':
    create_cluster()
