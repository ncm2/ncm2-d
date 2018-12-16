#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, CalledProcessError, TimeoutExpired
from multiprocessing import Process


def start_dcd_server():
    """Start dcd server."""
    try:
        out = Popen(
            ["dcd-server"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        ).communicate()[0]
    except (CalledProcessError, FileNotFoundError) as e:
        print("dcd-server executable not available!")
    except TimeoutExpired:
        print("dcd-server timeout!")


def main():
    """Main function."""
    p = Process(target=start_dcd_server, daemon=True)
    p.start()
    p.join()


main()
