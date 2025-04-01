# LYIK Platform – Setup Guide

This guide provides clear and beginner-friendly steps to install, configure, and run the LYIK platform.

---

## Prerequisites

Before proceeding, ensure the following tools and information are available:

- **Docker**:  
  Ensure Docker is installed and running on your system.

  - [Linux installation guide](https://docs.sevenbridges.com/docs/install-docker-on-linux)  
  - [Windows installation guide](https://docs.sevenbridges.com/docs/install-docker-on-windows)

  **Check installation:**
  ```bash
  docker --version
  ```

- **Azure Token**:  
  Contact `admin@lyik.com` to obtain azure token.

- **License Key**:  
  Contact `admin@lyik.com` to obtain a valid license key.

---

## Accessing LYIK Docker Images

You will need credentials to pull LYIK Docker images.

**Login to the container registry:**
```bash
docker login -u LYIK-CUSTOMER -p <your_azure_token_here> lyikprodblueacr.azurecr.io
```

Ensure Docker is running before attempting login.

---

## Host Mapping

To access services locally using domain-like URLs, update your system's host file:

```bash
sudo vim /etc/hosts
```

Add the following lines:

```
127.0.0.1 api.test.lyik.com admin.test.lyik.com forms.test.lyik.com dashboard.test.lyik.com
```

---


## API Configuration

### Configure Environment, License Key

Edit the `lyik_base.env` file with appropriate values for your setup.
Add the provided LICENSE_KEY value in `lyik_base.env`

---

## Deploying the Platform

1. Pull the latest base image and build the local Docker containers:
   ```bash
   make build
   ```

2. Ensure the Docker network `net_lyik` exists:
   ```bash
   docker network create net_lyik
   ```

3. Start services using Docker Compose:
   ```bash
   docker compose -f compose_lyik_stack.yml up -d
   ```

4. Verify running containers:
   ```bash
   docker ps
   ```

5. Stop services press `Ctrl+C` in the terminal, or run:
   ```bash
   docker compose -f compose_lyik_stack.yml down
   ```

---

## Accessing the Platform

After deployment, open your browser and go to:

- Forms Portal: `https://forms.test.lyik.com` or your configured domain
- Admin Portal: `https://admin.test.lyik.com`
- API Endpoint: `https://api.test.lyik.com`
- Dashboard: `https://dashboard.test.lyik.com`

---

## Troubleshooting

Check running containers and logs:

```bash
docker ps
docker logs <container-name or container-id>
```

---

## Additional Information

- For help and support, contact `support@lyik.com`.