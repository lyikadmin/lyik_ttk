
# LYIK Platform Installation and Setup Guide

This guide provides comprehensive step-by-step instructions to install, configure, and deploy the LYIK platform.

---

## **Prerequisites**

Before starting, ensure that your environment meets the following requirements:

- **Docker**: Installed and running. Refer to the 
  1. [Docker installation guide for Linux](https://docs.sevenbridges.com/docs/install-docker-on-linux)
  2. [Docker installation guide for Windows](https://docs.sevenbridges.com/docs/install-docker-on-windows) 
   
   or follow the [Official Documentation](https://docs.docker.com/engine/install/ubuntu/).
  Check if docker is installed
  ```
  docker --version # This will show the version of docker, if installed!
  ```
  If it is not installed, follow the link mentioed above to setup docker.

  If it is installed, start the docker daemon and run the hello-world container
  ```
  docker run hello-world
  ```

- **Supported Database**: MongoDB (Docker container or Mongo Atlas).
- **TLS/SSL Certificates**: Required for secure communication.  (default TLS certificate is provided for this setup)
- **License Key**: Contact `admin@lyik.com` to obtain a valid license key.

---

## **Accessing Docker Images**

To run the LYIK platform, you need access to the container registry. Follow these steps:

- **Log in to Azure Container Registry (ACR):**
Use the credentials provided by the LYIK administrator:

```bash
docker login -u LYIK-CUSTOMER -p <your_azure_token_here> lyikprodblueacr.azurecr.io
```
- Note: Ensure that Docker is running.
---

## **Database Setup**

### **Supported Database**

- **MongoDB**


    #### **MongoDB running on Docker Containe** r(non-persistent data, not recommended)

    1. Locate the `compose_lyik_stack.yml` file.
    2. Follow instruction comments tagged with `@MONGO`.
        ```
        # @MONGO 
        depends_on:
          - mongodb
        ```

    #### **MongoDB running as Cloud Managed Service** (Recommended)

    3. Create a database in MongoDB Atlas and obtain the connection URL. Refer to this [MongoDB Atlas setup guide](https://vinyldavyl.medium.com/how-to-create-a-database-in-mongodb-atlas-and-connect-your-database-to-your-application-step-by-9b63a2886b83).
    4. Additional resources:
        - [Install MongoDB Community Edition on Ubuntu](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)
        - [Install MongoDB Enterprise Edition on Ubuntu](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-enterprise-on-ubuntu/)
        - [Backup and Restore MongoDB](https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/)
        - [Recover MongoDB After Unexpected Shutdown](https://www.mongodb.com/docs/manual/tutorial/recover-data-following-unexpected-shutdown/)

---

## **Networking and Nginx Configuration**

### For Running locally
You need to edit the `/etc/hosts` file

```
sudo vim /etc/hosts # you can open with any editor
```
and add the following entries:
```
127.0.0.1 api.test.lyik.com admin.test.lyik.com forms.test.lyik.com dashboard.test.lyik.com
```

### For Production  
1. Edit the `nginx.conf` file in the `nginx` directory:
    - Replace placeholders tagged with `@DOMAIN` with your domain URLs for:
        - Forms Portal
        - Admin Portal
        - API Endpoint
        - Grafana Dashboard Portal
2. Place your TLS/SSL certificate files (`tls.cert` and `tls.key`) in the `certificates` directory.

---

## **LYIK API Setup**

### 1. **Edit Environment Variables**

- Open the `lyik_base.env` file.
- Update values to match your requirements.


### 2. **Copy Required Assets** (Optional)

- Place files corresponding to environment variables (e.g., certificates files for esigning and UCC) in the `~/plugins-files/` directory.

---
## **Forms Portal Setup**

1. Locate and edit the `forms_config.json` file to edit the values for following:
   ```
   "api_path": "https://<api-domain-url>" # No need to edit if nginx configuration is not edited for this.
   ```
2. Edit others as per requirement, for example if you want to use digilocker api services, add the api credentials along with `digilocker_callbackUrl` as `"https://<your-forms-domain>/digi_redirect",`
 
## **Admin Portal Setup**
No changes required for running locally.
    
**For Production**
Locate and edit the `admin_config.json` file.
```
"API_URL": "https://<your-api-domain>/v1/",
"form_filling_url": "https://<your-forms-domain>/"
```

---

## **Deploying the Platform**

To deploy the platform, follow these steps:

1. Run Docker Compose:

```bash
docker compose -f compose_lyik_stack.yml up -d
```

- **Note:** Ensure that the `net_lyik` network exists. If not, create it using:
```bash
docker network create net_lyik
```

1. Verify that all services are running using:

```bash
docker ps
```


---

## **Accessing the Platform**

Upon successful deployment, you can access various components of the platform via their respective URLs:

- Forms Portal: `https://forms.test.lyik.com` or `<your-forms-domain>`
- Admin Portal: `https://admin.test.lyik.com` or `<your-admin-portal-domain>`
- API Endpoint: `https://api.test.lyik.com` or `<your-api-domain>`
- Grafana Dashboard: `https://dashboard.test.lyik.com` or `<your-grafana-dashboard-domain>`

---

## **Notes**

1. Ensure Docker is running before executing any commands.
2. Double-check the environment variables in both `lyik_base.env`.

---

## **Miscellaneous**

1. A valid LYIK license key is required to run the platform. Contact `admin@lyik.com` for registration.
2. For troubleshooting or support, reach out to `support@lyik.com`.

## **Troubleshooting**
See the container logs.
```
docker ps
docker logs <container-name or id>
```

