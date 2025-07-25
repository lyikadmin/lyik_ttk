name: lyik_platform
# NOTES
# Create a network first time:
# docker network create net_lyik
# Start using:
# docker compose -f compose-production-stack.yml up -d
services:
  nginx-proxy-prod:
    image: nginx:latest
    container_name: nginx-proxy-prod
    ports:
      - 80:80
      - 443:443
    command: ["nginx", "-g", "daemon off;"]
    volumes:
      - ./nginx/nginx_single_domain.conf:/etc/nginx/nginx.conf
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - ./certificates/tls.crt:/etc/nginx/certs/certificate.crt
      - ./certificates/tls.key:/etc/nginx/certs/private.key
      - ./logs/nginx-proxy-prod:/var/log/nginx
      - ./static_files:/app/static_files
    depends_on:
      - lyik_api
      - lyik_spa
      - lyik_admin_portal
      - grafana
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 384M
        reservations:
          cpus: "0.25"
          memory: 128M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  lyik_spa:
    container_name: 'lyik_spa'
    image: TPL_LYIK_SPA_VERSION
    restart: always
    # ports:
    #   - 3030:3030
    command: ["nginx", "-g", "daemon off;"]
    volumes:
      - ./forms_config.json:/app/config/config.json
      # - ./lyik_spa/fonts:/app/public/assets/fonts
      - ./lyik_spa/images:/app/public/assets/images
      - ./lyik_spa/theme.json:/app/public/config/theme.json
      - ./lyik_spa/theme.json:/usr/share/nginx/html/config/theme.json
      - ./lyik_spa/fonts:/usr/share/nginx/html/assets/fonts
      # - ./lyik_spa/navbar.json:/app/public/config/navbar.config.json
      - ./lyik_spa/navbar.json:/usr/share/nginx/html/config/navbar.config.json
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
    environment:
      - TZ=Asia/Calcutta

  lyik_api:
    container_name: 'lyik_api'
    # @API - REPLACE WITH YOUR IMAGE NAME AND IMAGE TAG in case using modified images.
    image: lyik-api:latest
    restart: always
    ports:
      - 8080:8080
    stdin_open: true # docker run -i
    tty: true        # docker run -t
    command: ['bash']
    environment:
      - MODE=PROD
      - TZ=Asia/Calcutta
    volumes:
      - /tmp/lyik:/tmp/lyik
      - ./plugin_files:/lyik/certificate
      - ./templates:/lyik/templates
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
    
    # @MONGO - Uncomment the following lines of code if you're running mongodb database service on Docker Container.
    depends_on:
      - mongodb
    env_file:
      - lyik_base.env
      - customer.env  # Uncomment this line if you have your own sepcific specific environment variables.


  # @MONGO - Uncomment the following lines of code if you're running mongodb database service on Docker Container. This will start and use the non-persistent mongodb container.
  mongodb:
    container_name: 'mongodb'
    image:  mongodb/mongodb-community-server:latest
    restart: always
    ports:
      - 27017:27017
    volumes:
      - TPL_MONGODB_MOUNT_DIR:/data/db 
    user: root
    logging:
      driver: "json-file"
      options:
        max-size: "10m"

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /tmp/lyik:/promtail/logs:ro  # Read lyik Docker logs
      - /etc/hostname:/etc/host_hostname
      - ./promtail:/etc/promtail
      - .:/var/lib/promtail
    command: -config.file=/etc/promtail/promtail-config.yml
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
    depends_on:
      - lyik_api
    restart: always
    # extra_hosts:
    #   lyik_api: "192.168.65.254"


  lyik_admin_portal:
    container_name: 'lyik_admin_portal'
    image: lyikprodblueacr.azurecr.io/lyik-admin
    restart: always
    # ports:
    #   - 3000:3000
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
    volumes:
      - ./admin_config.json:/app/config/config.json
    environment:
      - TZ=Asia/Calcutta

  grafana:
    container_name: 'grafana'
    image: grafana/grafana
    # ports:
    #   - '3001:3000'
    depends_on:
      - loki
    restart: always
    volumes:
      - ./grafana/custom.ini:/etc/grafana/custom.ini
      - ./grafana/loki.yaml:/usr/share/grafana/conf/provisioning/datasources/loki.yaml
      - ./grafana/loki.yaml:/etc/grafana/provisioning/datasources/loki.yaml
    environment:
      - GF_PATHS_CONFIG=/etc/grafana/custom.ini
    logging:
      driver: "json-file"
      options:
        max-size: "10m"

  loki:
    image: grafana/loki:latest
    container_name: loki
    # ports:
    #   - "3100:3100"
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"

networks:
  default:
    name: net_lyik
    external: true

