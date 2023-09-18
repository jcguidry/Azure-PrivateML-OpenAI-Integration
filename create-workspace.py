# %%
# Imports
from azure.identity import ClientSecretCredential
from azure.common.credentials import ServicePrincipalCredentials
from azureml.core.authentication import ServicePrincipalAuthentication

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage import StorageManagementClient
from azureml.core import Workspace
# from azure.ai.ml.entities import Workspace
import datetime
import yaml

# %% [markdown]
# ## Azure Client Authentication

# %%
# Load secret keys from YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

subscription_id = config.get("subscription_id")
client_id = config.get("client_id")
secret = config.get("secret")
tenant_id = config.get("tenant_id")

# %%
# Create `credebtial` object that holds the keys.

credential = ClientSecretCredential(
    client_id=client_id,
    client_secret=secret,
    tenant_id=tenant_id
)

# Authenticate to Azure Python SDK Clients
resource_client = ResourceManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
storage_client = StorageManagementClient(credential, subscription_id)


# %%
# Configuration Parameters
resource_group_name = 'AI_IC_NAM_GenAI-Template-2'
location = 'eastus'
vnet_name = 'MyVNet'
subnet_name = 'MyPrivateSubnet'
firewall_name = 'my_firewall'
route_table_name = 'myRouteTable'
aml_workspace_name = 'secureamlsdemo'
storage_account_name = 'amlprivatestorage'
openai_account_name = 'genai-test-openai'


# %%
# Create Resource Group
resource_client.resource_groups.create_or_update(
    resource_group_name,
    {"location": location}
)

# %% [markdown]
# ## Configure Networking Resources

# %%
# Create Virtual Network
vnet_params = {
    'location': location,
    'address_space': {
        'address_prefixes': ['10.0.0.0/16']
    }
}
network_client.virtual_networks.begin_create_or_update(resource_group_name, vnet_name, vnet_params)

# %% [markdown]
# ### Create Firewall

# %%
# Create a Subnet for the Firewall, within the VNet
# This subnet must be named "AzureFirewallSubnet"

subnet_params_2 = {
    'address_prefix': '10.0.0.0/24',
}

network_client.subnets.begin_create_or_update(
    resource_group_name,
    vnet_name,
    'AzureFirewallSubnet',
    subnet_params_2
).result()


# Get Subnet ID
subnet = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)
subnet_id = subnet.id

# %%
# Create public IP for firewall to use
public_ip_params = {
    "location": location,
    "sku": {
        "name": "Standard"
    },
    "public_ip_allocation_method": "Static",
    "public_ip_address_version": "IPv4"
}

network_client.public_ip_addresses.begin_create_or_update(resource_group_name, "myFirewallPublicIP", public_ip_params).result()


# %%
# Create Firewall
firewall_params = {
    'location': 'eastus',
    'sku': {
        'name': 'AZFW_VNet',
        'tier': 'Standard',
    },
    'ip_configurations': [
        {
            'name': 'configuration',
            'subnet': {'id': f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/AzureFirewallSubnet"},
            'public_ip_address': {'id': f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/publicIPAddresses/myFirewallPublicIP"},
        }
    ],
    'application_rule_collections': [
        {
            'name': 'appRules',
            'priority': 100,
            'action': {
                'type': 'Allow'
            },
            'rules': [
                {
                    'name': 'rule1',
                    'protocols': [
                        {
                            'protocol_type': 'Http',
                            'port': 80  # HTTP usually uses port 80
                        }
                    ],
                    'source_addresses': ['*'],
                    'target_fqdns': ['whitelisted.com', 'example.com'],  # Replace with your actual whitelisted domains
                    'rule_type': 'ApplicationRule',
                    'action': 'Allow'
                }
            ]
        }
    ]
}
firewall_poller = network_client.azure_firewalls.begin_create_or_update(
    resource_group_name,
    firewall_name,
    firewall_params
)
firewall = firewall_poller.result()


# %% [markdown]
# ### Connect PrivateSubnet to Firewall w/ Route Table

# %%
# Get Azure Firewall details
firewall = network_client.azure_firewalls.get(resource_group_name, firewall_name)

# Retrieve the private IP address
private_ip_address = firewall.ip_configurations[0].private_ip_address if firewall.ip_configurations else None

print(f"The private IP address of the Azure Firewall is: {private_ip_address}")

# %%

# Create Route Table
route_table_params = {
    "location": location,
    "routes": [
        {
            "name": "myRoute",
            "properties": {
                "addressPrefix": "0.0.0.0/0",
                "nextHopType": "VirtualAppliance",
                # "nextHopIpAddress": "IP_ADDRESS_OF_AZURE_FIREWALL"
                "nextHopIpAddress": private_ip_address
            }
        }
    ]
}

route_table = network_client.route_tables.begin_create_or_update(
    resource_group_name, 
    route_table_name, 
    route_table_params
).result()

# %% [markdown]
# ## Create Private Subnet, to connect services to

# %%
# Create Private Subnet, within the VNet

subnet_params = {
    'address_prefix': '10.0.1.0/24',
    "route_table": {
    "id": route_table.id
    },
    # 'delegations': [],
    'service_endpoints': [
        {'service': 'Microsoft.CognitiveServices'},
        # {"service": "Microsoft.MachineLearningServices"},
        {"service": "Microsoft.ContainerRegistry"},
        {"service": "Microsoft.KeyVault"},
        {"service": "Microsoft.Storage"}
        ]
}

network_client.subnets.begin_create_or_update(
    resource_group_name,
    vnet_name,
    subnet_name,
    subnet_params
).result()


# Get Subnet ID
subnet = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)
subnet_id = subnet.id

# %% [markdown]
# # Work in Progress

# %%
aml_workspace_name

# %%
UID_str = datetime.datetime.now().strftime("%m%d%H%M")
UID_str


deployment_name = f"aml_workspace_vnet_deployment_{UID_str}"
template_uri = "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/quickstarts/microsoft.machinelearningservices/machine-learning-workspace-vnet/azuredeploy.json"

parameters = {
    "workspaceName": {"value": aml_workspace_name},
    "location": {"value": location},
    
    "storageAccountOption": {"value": "new"},
    "storageAccountName": {"value": f"amlstorage{UID_str}dt"},
    "storageAccountBehindVNet": {"value": "true"},

    "keyVaultOption": {"value": "new"},
    "keyVaultName": {"value": f"amlkeyvault{UID_str}dt"},
    "keyVaultBehindVNet": {"value": "true"},


    "containerRegistryOption": {"value": "new"},
    "containerRegistryName": {"value": f"amlcontregistry{UID_str}dt"},
    "containerRegistrySku": {"value": "Premium"},
    "containerRegistryBehindVNet": {"value": "true"},
    
    "vnetOption": {"value": "existing"},
    "vnetName": {"value": vnet_name},
    "addressPrefixes": {"value": ["10.0.0.0/16"]},
    "subnetOption": {"value": "existing"},
    "subnetName": {"value": subnet_name},
    "subnetPrefix": {"value": "10.0.1.0/24"},
    "privateEndpointType": {"value": "AutoApproval"}
}

deployment_properties = {
    "mode": "Incremental",
    "template_link": {
        "uri": template_uri
    },
    "parameters": parameters
}

resource_client.deployments.begin_create_or_update(
    resource_group_name, 
    deployment_name, 
    {"properties": deployment_properties}
).result()


# %% [markdown]
# ## Create private endpoint connections for the newly created resources

# %%
storage_account_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/amlstorage{UID_str}dt"
keyvault_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/amlkeyvault{UID_str}dt"
acr_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ContainerRegistry/registries/amlcontregistry{UID_str}dt"

# %%
def create_private_endpoint(network_client, resource_group_name, location, subnet_id, service_name, connection_name, service_id, group_ids):
    pe_params = {
        "location": location,
        "subnet": {
            "id": subnet_id
        },
        "private_link_service_connections": [{
            "name": connection_name,
            "private_link_service_id": service_id,
            "group_ids": group_ids
        }]
    }
    return network_client.private_endpoints.begin_create_or_update(
        resource_group_name,
        service_name,
        pe_params
    ).result()


# Creating storage blob private endpoint
storage_pe_blob = create_private_endpoint(network_client, resource_group_name, location, subnet_id, "StoragePrivateEndpoint_Blob", "StorageAccountConnection_Blob", storage_account_id, ["blob"])
print('created blob private endpoint connection to subnet')

# Creating storage file private endpoint
storage_pe_file = create_private_endpoint(network_client, resource_group_name, location, subnet_id, "StoragePrivateEndpoint_File", "StorageAccountConnection_File", storage_account_id, ["file"])
print('created file private endpoint connection to subnet')

# Creating key vault private endpoint
keyvault_pe = create_private_endpoint(network_client, resource_group_name, location, subnet_id, "KeyVaultPrivateEndpoint", "KeyVaultConnection", keyvault_id, ["vault"])
print('created keyvault private endpoint connection to subnet')

# Creating container registry private endpoint
acr_pe = create_private_endpoint(network_client, resource_group_name, location, subnet_id, "ContainerRegistryPrivateEndpoint", "ContainerRegistryConnection", acr_id, ["registry"])
print('created container registry private endpoint connection to subnet')


# %%
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.network import NetworkManagementClient
# from azure.mgmt.network.models import VirtualNetworkGateway, VirtualNetworkGatewayIPConfiguration, SubResource, IpAllocationMethod


# %%
# subnet = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)
# public_ip = network_client.public_ip_addresses.get(resource_group_name, public_ip_name) # myFirewallPublicIP


# %%
params = VirtualNetworkGateway(
    location=location,
    gateway_type="Vpn",
    vpn_type="RouteBased",
    enable_bgp=False,
    ip_configurations=[ip_config],
    sku={"name": "VpnGw1"}
    vpn_gateway_generation="Generation2"
)

network_client.virtual_network_gateways.begin_create_or_update(resource_group_name, gateway_name, params).result()



