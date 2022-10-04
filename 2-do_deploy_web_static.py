#!/usr/bin/python3
"""Generates a .tgz archive from the
contents of the web_static folder
Distributes an archive to a web server"""

from fabric.operations import local, run, put
from datetime import datetime
import os
from fabric.api import env

env.hosts = ['3.234.246.28', '34.229.62.188']
env.user = "ubuntu"


def do_pack():
    """Function to compress files to .tgz"""
    local("mkdir -p versions")
    arch = local("tar -cvzf versions/web_static_{}.tgz web_static"
                 .format(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")),
                 capture=True)
    if arch.succeeded:
        return arch
    return None


def do_deploy(archive_path):
    """Function to distribute an archive to a server"""
    if not os.path.exists(archive_path):
        return False

    try:
        # web_static_20220929115037.tgz
        arch_name = archive_path.split("/")[1]
        # web_static_20220929115037
        file_name = arch_name.split(".")[0]

        # upload archive to /tmp/
        put(archive_path, "/tmp/{}".format(arch_name))

        # uncompress the archive to /data/web_static/releases/file_name
        run("mkdir -p /data/web_static/releases/{}".format(file_name))
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/"
            .format(arch_name, file_name))

        # delete the archive from the web server
        run("rm /tmp/{}".format(arch_name))

        # delete the symbolic link /data/web_static/current
        run("mv /data/web_static/releases/{}/web_static/*"
            " /data/web_static/releases/{}/".format(file_name, file_name))
        run("rm -rf /data/web_static/releases/{}/web_static".format(file_name))
        run("rm -rf /data/web_static/current")

        # create a new symbolic link /data/web_static/current
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current"
            .format(file_name))

        print("New version deployed!")
        return True
    except Exception:
        return False
