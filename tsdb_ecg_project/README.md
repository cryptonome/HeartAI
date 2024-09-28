Clean Up Existing Configurations
Remove any conflicting or outdated network configurations.

podman network rm tsdb_ecg_project_default

Note: This removes the custom network created by your Compose project. It will be recreated when you run the containers again.

Rebuild and Start Your Containers
After making the above changes, rebuild and start your containers:

podman-compose up --build


Verify Containers are Running
Check the status of your containers:

bash
Copiar código
podman ps