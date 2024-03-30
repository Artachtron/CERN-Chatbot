"""An Azure RM Python Pulumi program"""

# Docker images
""" docker_image_registry = docker.ImageRegistryArgs(
    server="docker.io",
    username=proj_cfg.require_secret("dockerUsername"),
    password=proj_cfg.require_secret("dockerPassword"),
) 

backend = docker.Image(
    "backend",
    build=docker.DockerBuildArgs(context="./src/backend"),
    image_name="cern-backend:latest",
    skip_push=False,
    registry=docker_image_registry,
)

frontend = docker.Image(
    "frontend",
    build=docker.DockerBuildArgs(context="./src/frontend"),
    image_name="cern-frontend:latest",
    skip_push=False,
    registry=docker_image_registry,
)
"""

""" network = docker.Network("network", name=f"services_{stack}")

postgres_container = docker.Container(
    "cern-postgres",
    name="cern-postgres",
    image="postgres:latest",
    ports=[docker.ContainerPortArgs(internal=postgres_port, external=postgres_port)],
    networks_advanced=[
        docker.ContainerNetworksAdvancedArgs(name=network.name, aliases=["postgres"])
    ],
)


backend_container = (
    docker.Container(
        "cern-backend",
        name="cern-backend",
        image=backend.image_name,
        ports=[docker.ContainerPortArgs(internal=backend_port, external=backend_port)],
        envs=[
            f"DATABASE_USER={database_user}",
            f"DATABASE_PASSWORD={database_password}",
            f"DATABASE_HOST={database_host}",
            f"DATABASE_NAME={database_name}",
        ],
        networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=network.name)],
        opts=pulumi.ResourceOptions(depends_on=[postgres_container]),
    ),
)

frontend_container = docker.Container(
    "cern-frontend",
    name="cern-frontend",
    image=frontend.image_name,
    ports=[docker.ContainerPortArgs(internal=frontend_port, external=frontend_port)],
    envs=[
        f"BACKEND_URL=http://{backend_container.name}:{backend_port}",
        f"PORT={frontend_port}",
    ],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=network.name)],
) """

import base64
import pulumi

import pulumi_docker as docker
import pulumi_kubernetes as k8s
from pulumi_azure_native import resources
from pulumi_azure_native import network
from pulumi_azure_native import containerservice, containerregistry
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes import Provider, core

proj_cfg = pulumi.Config()

# Docker containers
stack = pulumi.get_stack()

frontend_port = proj_cfg.get_int("frontendPort", 3000)
backend_port = proj_cfg.get_int("backendPort", 8000)
postgres_port = proj_cfg.get_int("postgresPort", 5432)

database_user = proj_cfg.require("databaseUser")
database_password = proj_cfg.require_secret("databasePassword")
database_host = proj_cfg.require("databaseHost")
database_name = proj_cfg.require("databaseName")

# Get some project-namespaced configuration values or use default values
num_worker_nodes = proj_cfg.get_int("numWorkerNodes", 1)
k8s_version = proj_cfg.get("kubernetesVersion", "1.27")
prefix_for_dns = proj_cfg.get("prefixForDns", "pulumi")
node_vm_size = proj_cfg.get("nodeVmSize", "Standard_DS2_v2")
# The next two configuration values are required (no default can be provided)
mgmt_group_id = proj_cfg.require("mgmtGroupId")
ssh_pub_key = proj_cfg.require("sshPubKey")

# Create an Azure Resource Group
resource_group = resources.ResourceGroup("resource_group")

azure_container_registry = containerregistry.Registry(
    "azure_container_registry",
    resource_group_name=resource_group.name,
    registry_name="pulumi",
    admin_user_enabled=True,
    sku=containerregistry.SkuArgs(name="Basic"),
)


def get_registry_credentials(args):
    creds = containerregistry.list_registry_credentials_output(
        resource_group_name=resource_group.name,
        registry_name=azure_container_registry.name,
    )
    return {
        "server": azure_container_registry.login_server,
        "username": creds.username,
        "password": creds.passwords[0].value if creds.passwords else None,
    }


docker_image_registry = pulumi.Output.all().apply(get_registry_credentials)


""" backend_image = docker.Image(
    "backend",
    build=docker.DockerBuildArgs(context="../src/backend/"),
    image_name=azure_container_registry.login_server.apply(
        lambda server: f"{server.lower()}/cern-backend:latest"
    ),
    registry=docker_image_registry,
)

frontend_image = docker.Image(
    "frontend",
    build=docker.DockerBuildArgs(context="../src/frontend/"),
    image_name=azure_container_registry.login_server.apply(
        lambda server: f"{server.lower()}/cern-frontend:latest"
    ),
    registry=docker_image_registry,
) """


# Create an Azure Virtual Network
virtual_network = network.VirtualNetwork(
    "virtual_network",
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    resource_group_name=resource_group.name,
)

# Create three subnets in the virtual network
subnet1 = network.Subnet(
    "subnet-1",
    address_prefix="10.0.0.0/22",
    resource_group_name=resource_group.name,
    virtual_network_name=virtual_network.name,
)
subnet2 = network.Subnet(
    "subnet-2",
    address_prefix="10.0.4.0/22",
    resource_group_name=resource_group.name,
    virtual_network_name=virtual_network.name,
)
subnet3 = network.Subnet(
    "subnet-3",
    address_prefix="10.0.8.0/22",
    resource_group_name=resource_group.name,
    virtual_network_name=virtual_network.name,
)

# Create an Azure Kubernetes Service cluster
managed_cluster = containerservice.ManagedCluster(
    "managed_cluster",
    aad_profile=containerservice.ManagedClusterAADProfileArgs(
        enable_azure_rbac=True,
        managed=True,
        admin_group_object_ids=[mgmt_group_id],
    ),
    # Use multiple agent/node pools to distribute nodes across subnets
    agent_pool_profiles=[
        containerservice.ManagedClusterAgentPoolProfileArgs(
            availability_zones=[
                # "1",
                "2",
                "3",
            ],
            count=2,
            enable_node_public_ip=False,
            mode="System",
            name="systempool",
            os_type="Linux",
            os_disk_size_gb=30,
            type="VirtualMachineScaleSets",
            vm_size=node_vm_size,
            # Change next line for additional node pools to distribute across subnets
            vnet_subnet_id=subnet1.id,
        )
    ],
    # Change authorized_ip_ranges to limit access to API server
    # Changing enable_private_cluster requires alternate access to API server (VPN or similar)
    api_server_access_profile=containerservice.ManagedClusterAPIServerAccessProfileArgs(
        authorized_ip_ranges=["0.0.0.0/0"], enable_private_cluster=False
    ),
    dns_prefix=prefix_for_dns,
    enable_rbac=True,
    identity=containerservice.ManagedClusterIdentityArgs(
        type=containerservice.ResourceIdentityType.SYSTEM_ASSIGNED,
    ),
    kubernetes_version=k8s_version,
    linux_profile=containerservice.ContainerServiceLinuxProfileArgs(
        admin_username="azureuser",
        ssh=containerservice.ContainerServiceSshConfigurationArgs(
            public_keys=[
                containerservice.ContainerServiceSshPublicKeyArgs(
                    key_data=ssh_pub_key,
                )
            ],
        ),
    ),
    network_profile=containerservice.ContainerServiceNetworkProfileArgs(
        network_plugin="azure",
        network_policy="azure",
        service_cidr="10.96.0.0/16",
        dns_service_ip="10.96.0.10",
    ),
    resource_group_name=resource_group.name,
)

# Build a user Kubeconfig
# This SHOULD NOT be used for an explicit provider
# This SHOULD be used for user logins to the cluster
creds = containerservice.list_managed_cluster_user_credentials_output(
    resource_group_name=resource_group.name,
    resource_name=managed_cluster.name,
)
encoded = creds.kubeconfigs[0].value
kubeconfig = encoded.apply(lambda enc: base64.b64decode(enc).decode())

# Build an admin Kubeconfig
# This SHOULD be used for an explicit provider
# THIS SHOULD NOT be used for user logins to the cluster
adminCreds = containerservice.list_managed_cluster_admin_credentials_output(
    resource_group_name=resource_group.name,
    resource_name=managed_cluster.name,
)
encoded = adminCreds.kubeconfigs[0].value
adminKubeconfig = encoded.apply(lambda enc: base64.b64decode(enc).decode())


kubeconfig_file_path = "/mnt/h/Codes/Demo/CERN RAG/infra/k8s/kubeconfig"
with open(kubeconfig_file_path, "r") as file:
    kubeconfig_content = file.read()

k8s_provider = Provider("k8s-provider", kubeconfig=kubeconfig_content)

namespace = Namespace(
    "cern",
    metadata={"name": "cern"},
    # opts=pulumi.ResourceOptions(provider=k8s_provider),
)

app_labels = {"app": "cern"}


""" postgres_volume = k8s.core.v1.PersistentVolumeClaim(
    "cern-postgres-volume",
    metadata={"name": "cern-postgres-volume"},
    spec={
        "accessModes": ["ReadWriteOnce"],
        "resources": {"requests": {"storage": "1Gi"}},
    },
)

postgres_service = k8s.core.v1.Service(
    "cern-postgres-service",
    metadata={"name": "cern-postgres-service"},
    spec={
        "ports": [{"port": postgres_port, "targetPort": postgres_port}],
        "selector": app_labels,
    },
) """

postgres_volume_claim = k8s.core.v1.PersistentVolumeClaim(
    "cern-postgres-volume",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="cern-postgres-volume",
    ),
    spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        resources=k8s.core.v1.ResourceRequirementsArgs(requests={"storage": "1Gi"}),
    ),
)

postgres_service = k8s.core.v1.Service(
    "cern-postgres-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="cern-postgres-service",
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        ports=[
            k8s.core.v1.ServicePortArgs(port=postgres_port, target_port=postgres_port)
        ],
        selector=app_labels,
    ),
)

""" postgres_container = k8s.core.v1.ContainerArgs(
    name="cern-postgres",
    image="postgres:latest",
    ports=[{"containerPort": postgres_port}],
    volume_mounts=[
        {"name": "cern-postgres-volume", "mountPath": "/var/lib/postgresql/data"}
    ],
    env=[
        {"name": "POSTGRES_USER", "value": database_user},
        {"name": "POSTGRES_PASSWORD", "value": database_password},
        {"name": "POSTGRES_DB", "value": database_name},
    ],
)
 """
postgres_container = k8s.core.v1.ContainerArgs(
    name="cern-postgres",
    image="postgres:latest",
    ports=[k8s.core.v1.ContainerPortArgs(container_port=postgres_port)],
    env=[
        k8s.core.v1.EnvVarArgs(name="POSTGRES_USER", value=database_user),
        k8s.core.v1.EnvVarArgs(name="POSTGRES_PASSWORD", value=database_password),
        k8s.core.v1.EnvVarArgs(name="POSTGRES_DB", value=database_name),
    ],
    volume_mounts=[
        k8s.core.v1.VolumeMountArgs(
            name="postgres-data", mount_path="/var/lib/postgresql/data"
        )
    ],
)


""" deployment = Deployment(
    "cern-deployment",
    metadata={"namespace": namespace.metadata["name"], "labels": app_labels},
    spec={
        "selector": {"matchLabels": app_labels},
        "replicas": 1,
        "template": {
            "metadata": {"labels": app_labels},
            "spec": {
                "containers": [
                    {
                        "name": "cern-frontend",
                        "image": frontend_image.image_name,
                        "ports": [{"containerPort": frontend_port}],
                    },
                    {
                        "name": "cern-backend",
                        "image": backend_image.image_name,
                        "ports": [{"containerPort": backend_port}],
                    },
                    postgres_container,
                ],
                "volumes": [
                    {
                        "name": "cern-postgres-volume",
                        "persistentVolumeClaim": {
                            "claimName": postgres_volume.metadata["name"]
                        },
                    }
                ],
            },
        },
    },
) """

deployment = k8s.apps.v1.Deployment(
    "cern-postgres-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="cern-postgres-deployment", labels=app_labels
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
        replicas=1,
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    # k8s.core.v1.ContainerArgs(
                    #     name="cern-frontend",
                    #     image=frontend_image_name,
                    #     ports=[
                    #         k8s.core.v1.ContainerPortArgs(container_port=frontend_port)
                    #     ],
                    # ),
                    # # Backend container
                    # k8s.core.v1.ContainerArgs(
                    #     name="cern-backend",
                    #     image=backend_image_name,
                    #     ports=[
                    #         k8s.core.v1.ContainerPortArgs(container_port=backend_port)
                    #     ],
                    # ),
                    postgres_container,
                ],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name="postgres-data",
                        persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name=postgres_volume_claim.metadata.name
                        ),
                    )
                ],
            ),
        ),
    ),
)


# Export some values for use elsewhere
pulumi.export("rgname", resource_group.name)
pulumi.export("vnetName", virtual_network.name)
pulumi.export("clusterName", managed_cluster.name)
pulumi.export("kubeconfig", kubeconfig)
pulumi.export("adminKubeconfig", pulumi.Output.secret(adminKubeconfig))
# pulumi.export("backendImage", backend_image.image_name)
# pulumi.export("frontendImage", frontend_image.image_name)
