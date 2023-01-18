# EKS Pod Monitoring
Repository for monitoring the pods if they restart in a time frame then the code compares number of restarts and update the status on MS Teams webhooks

### Dependencies
1. Create RoleBindings for the namespaces where you want to monitor
2. Create MS Teams Webhook and update in python file, Dockerfile and deployment yaml
3. Build image using Dockerfile (update the webhook in dockerfile)

### Steps
1. Build Image and update the image repository
2. Update deployment yaml with the Image path reference
3. If you are running the python code from a pod on the same cluster then comment out line 21 'config.load_kube_config(config_file=os.environ.get("KUBECONFIG"))' and uncomment line 16 'config.load_incluster_config()'