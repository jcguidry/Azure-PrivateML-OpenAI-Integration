
# Azure-PrivateML-OpenAI-Integration

## Description
This repository enables the automated creation of a private Azure Machine Learning (AML) workspace, Blob Storage, Container Registry, Secrets Manager, and Azure OpenAI Service - all configured to operate within an Azure Virtual Network (VNet), ensuring data privacy and secure API interactions.

## Motivation
 To provision workspaces for secure AI solutions, particularly using Language Learning Models (LLMs) for question-answering on sensitive, domain-specific client data. Azure OpenAI service offers safety against data leakage to OpenAI, but developing solutions with it securely is non-trivial. The aim here is to create an AML workspace that restricts public outbound network traffic, but will allow traffic between private Azure services like OpenAI, assuring clients of data integrity. Automating this proces can accelerate the development speed of LLM solutions in privacy-critical applications.


## Features
- **Private Networking**: Isolate all services within a VNet.
- **Firewall**: Allow traffic to whitelisted domains.
- **Azure Machine Learning Workspace**: Run and manage ML tasks.
- **Azure OpenAI Service**: Leverage OpenAI capabilities within the same VNet.
- **Blob Storage**: Storage for AML, project development, and client data.
- **API Security**: Use private endpoints for AML-OpenAI communication.


## Useful Azure Machine Learning (AML) Reference Docs:
- [Manage Azure Machine Learning workspaces in the portal or with the Python SDK (v2)][1]
- [Workspace managed network isolation][2]
- [Secure Azure Machine Learning workspace resources using virtual networks (VNets)][3]

[1]: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?view=azureml-api-2&tabs=azure-portal
[2]: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-managed-network?view=azureml-api-2&tabs=python
[3]: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-network-security-overview?view=azureml-api-2



## Quick Start
Follow the step-by-step guide using Azure's Python SDK to configure and deploy the services.


### Project Setup on Windows

#### Prerequisites
- Python installed
- Azure CLI installed
- VS Code (optional)

1. Authenticate CLI with Azure (Optional)
    - Run 'az login' and follow on-screen instructions
    - Enables Azure interavtivity, using personal account
    - May require restart, to be added to system path

2. Create a Service Principal in Azure and create `config.yaml` file
    - Create a service principal with the the `contributer` role
    - take note of its `client id`, `tenant id`, and obtain a `secret key` from it.
    - take note of the `subscription id` for the azure directory you wish to work in.
    - add these to the `config_template.yaml` file and **rename it** to `config.yaml`

3. Clone this repo

4. Setup Python Virtual Environment & Install Requirements (Windows)
    - 4.1 Open project folder In VS Code
    - 4.2 Go to `Terminal` --> `New Terminal`
    - 4.3 Type `.\setup.bat` and hit `return`
    - Alternatively, do this from regular command line

5. Execute the `create-worspace` notebook
    - Connected to the `py_env` virtual environment
    - Easiest to run in VS Code
    