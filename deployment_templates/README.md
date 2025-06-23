# LYIK Platform – Setup Guide

This guide provides steps to install, configure, and run the LYIK platform.

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
Do not forget to add the provided LICENSE_KEY value in `lyik_base.env`

---

## Deploying the Platform

**First time Setup and Start services (Only use once, or if changes are made):**

   ```bash
   make build-up
   ```
---
### Regular use (starting/stopping services):

1. **Start services:**

   ```bash
   make up
   ```

2. **Verify running containers:**

   ```bash
   make ps
   ```

3. **Stop services:**

   ```bash
   make down
   ```

4. **Restart a service:**

   ```bash
   docker restart <container-name>
   ```

   example:

   ```bash
    docker restart lyik_api
   ```

---

## Accessing the Platform

After deployment, open your browser and go to:

- Forms Portal: `https://forms.test.lyik.com` or your configured domain
- Admin Portal: `https://admin.test.lyik.com` or your configured domain
- API Endpoint: `https://api.test.lyik.com` or your configured domain
- Dashboard: `https://dashboard.test.lyik.com` or your configured domain

---

## Advanced Usage (more control)

These commands are for fine-grained control.

- **Build everything manually (API + pull UI images):**

  ```bash
  make build
  ```

- **Build only the API image (if there are updates to the API server):**

  ```bash
  make build-api
  ```

- **Build only the UI images (if there are updates to the UI):**

  ```bash
  make build-ui
  ```

- **Start the platform without rebuilding:**

  ```bash
  make up
  ```

- **Stop and remove all containers:**

  ```bash
  make down
  ```

- **Restart the full stack:**

  ```bash
  make restart
  ```

- **Check running containers:**

  ```bash
  make ps
  ```

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