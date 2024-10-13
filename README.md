# OFC Cacao System For Self Onboarding

## Description
This repository contains scripts and configurations for setting up a Cacao System for Self Onboarding purposes.

## Prerequisites
- Git
- Docker
- Docker Compose

## Setup
1. Clone the repository:
```bash
   git clone git@github.com:Open-Food-Chain/ofc-cacao
```
2.  Initialize submodules:
```bash
   git submodule update --init --recursive
```

## Usage
1.  Build API Provider:
```bash
	./build-api-provider.sh
```
2.  Build Organizations:
```bash
   ./build-orgs.sh
```
3.  Launch API Provider:
```bash
   ./launch-api-provider.sh
```
4.  Launch Block:
```bash
   ./launch-block.sh
```

## Additional Notes
-   Ensure Docker and Docker Compose are installed and running.
-   Modify configurations as necessary for your specific environment.
-   For troubleshooting or further customization, refer to individual script files and accompanying documentation.
