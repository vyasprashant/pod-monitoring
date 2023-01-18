from kubernetes import client, config
import json
import requests
import time
import logging
import os
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.addHandler(logging.StreamHandler())


# Initialize the Kubernetes client
# If running inside pod

# config.load_incluster_config()

# If running locally
# config.load_kube_config()
config.load_kube_config(config_file=os.environ.get("KUBECONFIG"))
v1 = client.CoreV1Api()

# The URL for the MS Teams webhook
webhook_url = 'https://outlook.office.com/webhook/{webhook_id}/{webhook_secret}/{channel_id}'

# A dictionary to keep track of pod restarts
restarted_pods = {}

# List of namespaces to monitor
namespaces = [ '<< namespace >>']

while True:
    for namespace in namespaces:
        # Get a list of pods in the namespace
        pod_list = v1.list_namespaced_pod(namespace)

        # For all namespaces
        # pod_list = v1.list_pod_for_all_namespaces()

        for pod in pod_list.items:
            # Check if the pod has restarted
            if pod.metadata.name in restarted_pods:
                if pod.status.container_statuses is None:
                    logger.warning(f"Container statuses not available for pod {pod.metadata.name}")
                    continue
                # if pod.status.container_statuses[0].restart_count > restarted_pods[pod.metadata.name]:
                if pod.status.container_statuses[0].restart_count is not None and pod.status.container_statuses[0].restart_count > restarted_pods[pod.metadata.name]:
                    # Send a message to MS Teams
                    node_status = v1.read_node_status(pod.spec.node_name)
                    message = f'Pod {pod.metadata.name} has restarted on node {node_status.metadata.name} in namespace {namespace}'
                    data = {'text': message}
                    try:
                        response = requests.post(webhook_url, data=json.dumps(data),headers={'Content-Type': 'application/json'})
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as err:
                        print(f'Error: {err}')
                    except requests.exceptions.RequestException as err:
                        print(f'Error: {err}')
                        if not response.status_code != 200:
                            logger.error("Error sending message to MS Teams: {}".format(response.content))
                            # print(f'Error sending message to MS Teams: {response.content}')
                    restarted_pods[pod.metadata.name] = pod.status.container_statuses[0].restart_count
            else:
                restarted_pods[pod.metadata.name] = pod.status.container_statuses[0].restart_count
    logger.info(f'{datetime.datetime.now()} Checked {len(pod_list.items)} pods')
    # Sleep for a short period before checking the pods again
    time.sleep(60)
