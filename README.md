
# Azure-PrivateML-OpenAI-Integration

## Description
This repository enables the automated creation of a secure, private Azure Machine Learning (AML) services, Azure OpenAI services, and Blob Storage which are configured to operate within an Azure Virtual Network (VNet), ensuring data privacy and secure API interactions.

## Motivation
 To efficiently build secure AI solutions, particularly using Language Learning Models (LLMs) for question-answering on sensitive, domain-specific client data. While Azure OpenAI service offers safety against data leakage to OpenAI, setting it up securely yet flexibly is non-trivial. The aim here is to provide a straightforward method to provision Azure environments that do not allow outbound network traffic, but will allow traffic between services. This not only assures clients of data integrity but also fosters a flexible development environment. By automating the provisioning of such workspaces, we accelerate the development speed and scalability of LLM solutions in privacy-critical applications.


## Features
- **Private Networking**: Isolate all services within a VNet.
- **Azure Machine Learning Workspace**: Run and manage ML tasks.
- **Azure OpenAI Service**: Leverage OpenAI capabilities within the same VNet.
- **Blob Storage**: Securely store project and client files.
- **Secure File Handling**: Enable safe file uploads and data imports.
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

2. Clone this repo


3. Add Service Principal Secrets
    - Create a service principal with the the `contributer` role
    - take note of its `client id`, `tenant id`, and obtain a `secret key` from it.
    - take note of the `subscription id` for the azure directory you wish to work in.
    - add these to the `config_template.yaml` file and **rename it** to `config.yaml`

4. Setup Python Virtual Environment & Install Requirements (Windows)
    - 4.1 Open project folder In VS Code
    - 4.2 Go to `Terminal` --> `New Terminal`
    - 4.3 Type `.\setup.bat` and hit `return`
    - Alternatively, do this from regular command line

5. Execute the `create-worspace` notebook
    - Connected to the `py_env` virtual environment
    - Easiest to run in VS Code
    