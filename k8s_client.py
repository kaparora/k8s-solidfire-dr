#!/usr/bin/env python
"""
Author: Kapil Arora
Github: @kapilarora
"""
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8SClient(object):

    def __init__(self, kubeconfig, no_execute):

        self._kubeconfig = kubeconfig
        self._no_execute = no_execute
        self._client = self.create_k8s_client()

    def create_k8s_client(self):
        config.load_kube_config(self._kubeconfig)
        return client.CoreV1Api()

    def get_all_pvcs(self):
        return self._client.list_persistent_volume_claim_for_all_namespaces()




