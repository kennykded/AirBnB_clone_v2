#!/usr/bin/python3
"""Create and distributes an archive to web servers
"""
import os.path
import time
from fabric.api import local
from fabric.operations import env, put, run

env.hosts = ['3.234.246.28', '34.229.62.188']
env.user = "ubuntu"


def do_pack():
    """Generate an tgz archive from web_static folder."""
    try:
        local("mkdir -p versions")
        local("tar -cvzf versions/web_static_{}.tgz web_static/".
              format(time.strftime("%Y%m%d%H%M%S")))
        return ("versions/web_static_{}.tgz".format(time.
                                                    strftime("%Y%m%d%H%M%S")))
    except Exception:
        return None


def do_deploy(archive_path):
    """Distribute an archive to web servers."""
    if (os.path.isfile(archive_path) is False):
        return False

    try:
        file = archive_path.split("/")[-1]
        folder = ("/data/web_static/releases/" + file.split(".")[0])
        put(archive_path, "/tmp/")
        run("mkdir -p {}".format(folder))
        run("tar -xzf /tmp/{} -C {}".format(file, folder))
        run("rm /tmp/{}".format(file))
        run("mv {}/web_static/* {}/".format(folder, folder))
        run("rm -rf {}/web_static".format(folder))
        run('rm -rf /data/web_static/current')
        run("ln -s {} /data/web_static/current".format(folder))
        print("Deployment done")
        return True
    except Exception:
        return False


def deploy():
    """Create and distributes an archive to web servers."""
    try:
        path = do_pack()
        return do_deploy(path)
    except Exception:
        return False


def do_clean(number=0):
    """Delete out-of-date archives.
    Args:
        number (int, optional): Number of archives to keep.
    """
    number = 1 if int(number) == 0 else int(number)

    archives = sorted(os.listdir("versions"))
    [archives.pop() for i in range(number)]
    with lcd("versions"):
        [local("rm ./{}".format(a)) for a in archives]

    with cd("/data/web_static/releases"):
        archives = run("ls -tr").split()
        archives = [a for a in archives if "web_static_" in a]
        [archives.pop() for i in range(number)]
        [run("rm -rf ./{}".format(a)) for a in archives]
