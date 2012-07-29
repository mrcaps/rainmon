## Setup for distributed execution

Multiple instances of the analysis pipeline can be run in parallel across multiple machines.

1. follow the single-node setup instructions on the second machine. Make sure that the same versions of Celery and rabbitmq are installed on the master and any worker nodes.

1. in `config.json`, change `tmpdir` to point at a directory that is shared between the master and workers. There are multiple options here depending on which OS you prefer - some helpful guides include:
   * NFS on Ubuntu: https://help.ubuntu.com/community/SettingUpNFSHowTo
   * SMB on Ubuntu: https://help.ubuntu.com/community/Samba
   * SMB on OS X: http://support.apple.com/kb/HT1568

1. On the slave node, run the following:

```
cd code/ui
celeryd --broker=amqp://guest:guest@HOST// --config=celeryconfig
```

where guest:guest is the username:password for the master node's rabbitmq broker, and HOST is the hostname/IP of the master node.

Now, when tasks are run from the UI they will be distributed across workers that are not busy. Saving and loading will be coordinated across all workers only if the shared directory is configured properly.