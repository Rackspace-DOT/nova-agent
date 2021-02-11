
[![Github Tests Status](https://github.com/Rackspace-DOT/nova-agent/workflows/Tests/badge.svg)](https://github.com/Rackspace-DOT/nova-agent/workflows/Tests/badge.svg)

# Rackspace nova-agent

Running agent that helps with the setup of the server initially on first boot, and allows for password and network changes during the life cycle of the server.

#### Requirements

The agent will check and make sure that the instance is running on Rackspace hosts, and if so it will continue running and complete any tasks that is being requested through xenstore. If it is not then the agent will immediately stop running log the reason.

The agent will also look and see if `/dev/xen/xenbus` is available, and if so will utilize [pyxs](https://github.com/selectel/pyxs) library to interact with xenstore. If it is not available then the agent will try and utilize xenstore commands that are provided by xenstore-utils.

#### What does the agent do?

##### Networking
  * RHEL based systems use ifcfg scripts that are located in `/etc/sysconfig/network-scripts`

  **Note:** If extra options are placed in the ifcfg scripts scripts such as ZONE for firewalld. Then when networking is reset or IP addresses are added/removed those configuration options will be preserved by the agent.

  * Debian based systems use the `/etc/network/interfaces` file and sets them up accordingly.

  * Ubuntu based systems that utilize netplan will have networking setup in the following location: `/etc/netplan/50-rackspace-cloud.yaml`

  You can learn more about netplan here [https://netplan.io/](https://netplan.io/) and is available on Rackspace cloud in the Ubuntu 18.04 base image.

##### Hostname
  * On all systems the agent will try and use `hostnamectl` to set the hostname. If that fails then the agent will fall back and use the `hostname` command, and write to the `/etc/hostname` so that the hostname persists through a reboot.

##### Password
  * Sets the password assigned to the server on initial boot by nova. Also allows for password changes initiated by a user during the life cycle of the server

##### RHEL registration
  * For RHEL servers the agent completes RHN registration for the server on initial boot

#### Compatability

The agent is currently python 2.6 - 3.6 compatible, and Travis CI is being utilized for testing all python versions.
