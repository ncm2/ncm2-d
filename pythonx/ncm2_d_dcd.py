#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, CalledProcessError, TimeoutExpired
from multiprocessing import Process
import vim
import re
import os


def start_dcd_server():
    """Start dcd server."""

    def filter_nondirs(server_args):
        """Remove non existent dirs from server args."""
        f_args = []
        for item in server_args:
            m = re.match(r"-I(.+)", item)
            if m:
                dir_name = m.group(1)
                if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
                    continue
            f_args.append(item)
        return f_args

    server_args = list(vim.eval("g:ncm2_d#dcd_server_args"))
    cmd = ["dcd-server"]
    server_args = filter_nondirs(server_args)
    cmd.extend(server_args)

    try:
        sp = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        while sp.poll() is None:
            out = sp.stderr.readline()
            if "0 symbols cached" in out:
                vim.command(
                    "call ncm2_d#error({})".format(
                        '"dcd-server didn\'t cache any symbols! Double check dcd include paths -I flag!"'
                    )
                )
    except (CalledProcessError, FileNotFoundError) as e:
        vim.command(
            "call ncm2_d#error({})".format('"dcd-server executable not found!"')
        )
    except TimeoutExpired:
        vim.command("call ncm2_d#error({})".format('"dcd-server timeout!"'))


def main():
    """Main function."""
    p = Process(target=start_dcd_server, daemon=True)
    p.start()
    p.join()


main()
