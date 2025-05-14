# Use the prepared base image
FROM lyikprodblueacr.azurecr.io/lyik-api:latest

COPY plugin_repos_custom.txt /plugin_repos.txt
RUN bash /install_plugins_repos.sh

# Expose required ports
EXPOSE 8080

# Start the application
ENTRYPOINT ["/app/start.sh"]