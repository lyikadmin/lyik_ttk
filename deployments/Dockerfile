# Use the prepared base image
FROM lyik-api:1.0.0

# Set environment variables
ENV LOAD=FALSE
ENV MODE=LDEV

# # Set up SSH keys (for private Git repo access)
# WORKDIR /root/.ssh
# COPY ssh/id_ed25519 /root/.ssh/id_ed25519
# RUN chmod 600 /root/.ssh/id_ed25519
# COPY ssh/ssh_config /root/.ssh/config
# RUN chmod 600 /root/.ssh/config
# RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Copy the plugin_repos.txt into the lyik-server stage
COPY plugin_repos_custom.txt /plugin_repos.txt

# Run the install_plugins_repos.sh script to build and install plugin wheels, and clean up
RUN /install_plugins_repos.sh

# Expose required ports
EXPOSE 8080

# Start the application
ENTRYPOINT ["/app/start.sh"]
