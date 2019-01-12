#!/usr/bin/env python
# -*- coding: utf-8 -*-
import vim
from ncm2 import Ncm2Source, getLogger
from distutils.spawn import find_executable
import re
import subprocess


logger = getLogger(__name__)
re_func = re.compile(r"\w+(\(.*?\))?\((.*?)\)$")


class Source(Ncm2Source):
    def __init__(self, vim):
        Ncm2Source.__init__(self, vim)
        self.idenclass = {
            "c": "class",
            "i": "interface",
            "s": "struct",
            "u": "union",
            "v": "var",
            "m": "var",
            "k": "keyword",
            "f": "function",
            "g": "enum",
            "e": "enum",
            "P": "package",
            "M": "module",
            "a": "array",
            "A": "aarray",
            "l": "alias",
            "t": "template",
            "T": "mixin template",
        }

    def check(self):
        data = self.nvim.call("ncm2_d#data")
        for key, bin_path in data.items():
            if "_bin" in key and not find_executable(bin_path):
                self.nvim.call(
                    "ncm2_d#error",
                    'Cannot find "{}" executable. Please, install it first.'.format(
                        bin_path
                    ),
                )

    def on_complete(self, ctx, data, lines):

        src = "\n".join(lines)
        src = self.get_src(src, ctx)
        lnum = ctx["lnum"]
        bcol = ctx["bcol"]
        typed = ctx["typed"]
        filepath = ctx["filepath"]

        # use byte addressing
        src = src.encode()
        offset = self.lccol2pos(lnum, bcol, src)

        dcd_client = find_executable(data["dcd_client_bin"])
        dcd_client_args = data["dcd_client_args"]
        args = [dcd_client]
        if dcd_client_args and dcd_client_args != [""]:
            args.extend(dcd_client_args)
        args.extend(["-x", "-c" + str(offset)])
        args.extend(data["dcd_inc_dirs"])
        proc = subprocess.Popen(
            args=args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        result, errs = proc.communicate(src, timeout=10)
        if errs:
            logger.error(errs)
        logger.debug("args: %s, result: [%s]", args, result)

        result = result.decode().split("\n")
        if not result:
            return
        if result[0] != "identifiers":
            return

        startbcol = bcol
        startccol = len(typed.encode()[: startbcol - 1].decode())
        # based on the docs, the startccol should be + 1
        if typed[-1] == ".":
            startccol += 1

        max_args = 5
        values = [""] * max_args  # ident, kind, definition, sympath, doc
        matches = []
        for line in result[1:]:
            args = line.split("\t")
            for i, arg in enumerate(args):
                values[i] = arg
            for i in range(len(values), max_args):
                values[i] = args[i]
            item = dict(
                word=values[0],
                icase=1,
                dup=0,
                kind=values[1],
                menu=values[2],
                user_data={},
            )
            self.render_snippet(item)
            matches.append(item)

        logger.debug("startccol %s, matches %s", startccol, matches)
        self.complete(ctx, startccol, matches)

    def render_snippet(self, item):

        # function (and template ) snippet support
        m = re_func.search(item.get("menu", ""))
        if not m:
            return

        params = m.group(2)
        params = params.split(",")
        logger.debug("snippet params: %s", params)
        snip_params = []
        ultisnip_num = 1
        for param in [p.strip() for p in params]:
            if not param:
                logger.error(
                    "failed to process snippet for item: %s, param: %s", item, param
                )
                break
            if param.find("=") >= 0:
                continue
            # add optional args if it's the first param, and add stop point.
            index = param.find("...")
            if index >= 0:
                if ultisnip_num == 1:
                    snip_params.append(
                        self.snippet_placeholder(ultisnip_num, param[: index + 3])
                        + "${2}"
                    )
                    break
                else:
                    continue
            snip_params.append(self.snippet_placeholder(ultisnip_num, param))
            ultisnip_num += 1

        ud = item["user_data"]
        ud["is_snippet"] = 1
        ud["snippet"] = item["word"] + "(" + ", ".join(snip_params) + ")${0}"
        logger.debug("final snippet: %s", ud)

    def snippet_placeholder(self, ultisnip_num, txt=""):
        txt = txt.replace("\\", "\\\\")
        txt = txt.replace("$", r"\$")
        txt = txt.replace("}", r"\}")
        if txt == "":
            return "${%s}" % ultisnip_num
        return "${%s:%s}" % (ultisnip_num, txt)


source = Source(vim)
on_complete = source.on_complete
source.check()
