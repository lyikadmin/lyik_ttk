# Use the prepared base image
FROM lyikprodblueacr.azurecr.io/lyik-api:TPL_LYIK_API_VERSION


# # @PLUGIN uncomment this to Set up SSH keys (for your own Git repository of plugins)
# WORKDIR /root/.ssh
# COPY ssh/id_ed25519 /root/.ssh/id_ed25519
# RUN chmod 600 /root/.ssh/id_ed25519
# COPY ssh/ssh_config /root/.ssh/config
# RUN chmod 600 /root/.ssh/config
# RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
COPY plugin_repos_custom.txt /plugin_repos.txt
RUN bash /install_plugins_repos.sh

# Expose required ports
EXPOSE 8080

# Start the application
ENTRYPOINT ["/app/start.sh"]
