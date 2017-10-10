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

    def create_duplicate_pvc(self, original_pvc, secondary_suffix):
        duplicate_pvc = client.V1PersistentVolumeClaim()


        #setting metadata for pvc
        duplicate_pvc_metadata = client.V1ObjectMeta()
        duplicate_pvc_metadata.annotations = {}

        if 'volume.beta.kubernetes.io/storage-class' in original_pvc.metadata.annotations:
            duplicate_pvc_metadata.annotations['volume.beta.kubernetes.io/storage-class'] = \
                original_pvc.metadata.annotations['volume.beta.kubernetes.io/storage-class'] + secondary_suffix
        if 'volume.beta.kubernetes.io/storage-provisioner' in original_pvc.metadata.annotations:
            duplicate_pvc_metadata.annotations['volume.beta.kubernetes.io/storage-provisioner'] = \
                original_pvc.metadata.annotations['volume.beta.kubernetes.io/storage-provisioner']


        duplicate_pvc_metadata.labels = original_pvc.metadata.labels
        duplicate_pvc_metadata.name = original_pvc.metadata.name + secondary_suffix
        duplicate_pvc_metadata.namespace = original_pvc.metadata.namespace
        duplicate_pvc.metadata = duplicate_pvc_metadata

        #setting spec for pvc
        duplicate_pvc_spec = client.V1PersistentVolumeClaimSpec()
        duplicate_pvc_spec.access_modes = original_pvc.spec.access_modes
        duplicate_pvc_spec.resources = original_pvc.spec.resources
        duplicate_pvc_spec.selector = original_pvc.spec.selector
        duplicate_pvc.spec = duplicate_pvc_spec

        new_pvc = self._client.create_namespaced_persistent_volume_claim(original_pvc.metadata.namespace, duplicate_pvc)




