from kubernetes import client, config
import json
import requests
import time

# Initialize the Kubernetes client
config.load_kube_config()
v1 = client.CoreV1Api()

# The URL for the MS Teams webhook
webhook_url = 'https://outlook.office.com/webhook/{webhook_id}/{webhook_secret}/{channel_id}'

# A dictionary to keep track of pod restarts
restarted_pods = {}

while True:
    # Get a list of pods in the default namespace
    pod_list = v1.list_namespaced_pod('default')

    for pod in pod_list.items:
        # Check if the pod has restarted
        if pod.metadata.name in restarted_pods:
            if pod.status.container_statuses[0].restart_count > restarted_pods[pod.metadata.name]:
                # Send a message to MS Teams
                node_status = v1.read_node(pod.spec.node_name)
                message = f'Pod {pod.metadata.name} has restarted on node {node_status.metadata.name}'
                data = {'text': message}
                response = requests.post(webhook_url, json=data)
                if response.status_code != 200:
                    print(f'Error sending message to MS Teams: {response.content}')
                restarted_pods[pod.metadata.name] = pod.status.container_statuses[0].restart_count
        else:
            restarted_pods[pod.metadata.name] = pod.status.container_statuses[0].restart_count

    # Sleep for a short period before checking the pods again
    time.sleep(10)
