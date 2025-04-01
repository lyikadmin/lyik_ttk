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

- **Database**:  
  MongoDB (self-hosted in Docker or via MongoDB Atlas)

- **TLS/SSL Certificates**:  
  Required for secure communication. Default certificates are included for initial setup.

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

## Database Setup

The platform supports **MongoDB**. Choose one of the following methods:

### Option 1: Using Docker (for testing only)

1. Open `compose_lyik_stack.yml`.
2. Look for and follow comments tagged `@MONGO`:
   ```yaml
   # @MONGO
   depends_on:
     - mongodb
   ```

This setup does not persist data and is not recommended for long-term use.

### Option 2: Using MongoDB Atlas (recommended)

1. Create a MongoDB Atlas account.
2. Set up a database and obtain the connection URI.  
   Refer to this [MongoDB Atlas setup guide](https://vinyldavyl.medium.com/how-to-create-a-database-in-mongodb-atlas-and-connect-your-database-to-your-application-step-by-9b63a2886b83).

**Additional MongoDB Resources:**
- [Install MongoDB on Ubuntu](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)
- [Backup and Restore](https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/)
- [Data Recovery](https://www.mongodb.com/docs/manual/tutorial/recover-data-following-unexpected-shutdown/)

---

## Host Mapping (for local setup)

To access services locally using domain-like URLs, update your system's host file:

```bash
sudo vim /etc/hosts
```

Add the following lines:

```
127.0.0.1 api.test.lyik.com admin.test.lyik.com forms.test.lyik.com dashboard.test.lyik.com
```

---

## NGINX Configuration

1. Open the `nginx.conf` file located in the `nginx` directory.
2. Replace all `@DOMAIN` placeholders with your domain names for:
   - Forms Portal
   - Admin Portal
   - API
   - Dashboard
3. Place your TLS certificate files (`tls.cert`, `tls.key`) in the `certificates` folder.

---

## API Configuration

### Step 1: Configure Environment

Edit the `lyik_base.env` file with appropriate values for your setup.

### Step 2: Optional Asset Files

If you're using digital signing or UCC services, place the required certificate/key files in the `~/plugins-files/` directory.

### Step 3: Plugin Setup

- Place your SSH key (`id_ed25519`) for plugin access in the `~/ssh/` folder.
- Uncomment the `@PLUGIN` section in the `Dockerfile` to enable plugin installation.

---

## Forms Portal Configuration

1. Open and edit `forms_config.json`.
   ```json
   "api_path": "https://<api-domain-url>"
   ```

2. If using DigiLocker, add:
   ```json
   "digilocker_callbackUrl": "https://<your-forms-domain>/digi_redirect"
   ```

Update other values as needed for your configuration.

---

## Admin Portal Configuration

For local setups, no changes are required.

To update settings manually:

1. Open `admin_config.json`.
2. Set the correct URLs:
   ```json
   "API_URL": "https://<your-api-domain>/v1/",
   "form_filling_url": "https://<your-forms-domain>/"
   ```

---

## Deploying the Platform

1. Pull the latest base image and build the local Docker containers:
   ```bash
   make build
   ```

2. Start services using Docker Compose:
   ```bash
   docker compose -f compose_lyik_stack.yml up -d
   ```

3. Ensure the Docker network `net_lyik` exists:
   ```bash
   docker network create net_lyik
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

- You must have a valid license key to run the platform. Email `admin@lyik.com` to get one.
- For help and support, contact `support@lyik.com`.