This folder contains the master data that will be used to create the actual configuration files from the template (tpl) files.
The `base.master.csv` will contain all configuration that is common to all the three environments (dev, uat, prod)
The base configuration can be overridden by the respective confgiuration files.
For instance, dev.master.csv will override those in base.master.csv when creating a dev environment. Similarly for uat and prod