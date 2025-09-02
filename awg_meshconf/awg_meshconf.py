#!/usr/bin/env python3
"""
Name: awg-meshconf
Based on: wg-meshconf by K4YT3X
Creator: K4YT3X
Date Created: July 19, 2020
Last Modified: September 3, 2025

Modified by: SamuraJ
Modification Date: September 1, 2025
Changes: Added support for AmneziaWG obfuscation parameters and fixed csv handling

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt
(C) 2018-2021 K4YT3X
(C) 2025 SamuraJ - Modifications
"""

import argparse
import logging
import pathlib

from .database_manager import DatabaseManager


def parse_arguments():
    """parse CLI arguments"""
    parser = argparse.ArgumentParser(prog="awg-meshconf", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-d",
        "--database",
        type=pathlib.Path,
        help="path where the database file is stored",
        default=pathlib.Path("database.csv"),
    )

    # add subparsers for commands
    subparsers = parser.add_subparsers(dest="command")

    # initialize empty database
    subparsers.add_parser("init")

    # add new peer
    addpeer = subparsers.add_parser("addpeer")
    addpeer.add_argument("name", help="Name used to identify this node")
    addpeer.add_argument("--address", help="address of the server", action="append", required=True)
    addpeer.add_argument("--endpoint", help="peer's public endpoint address")
    addpeer.add_argument("--allowedips", help="additional allowed IP addresses", action="append")
    addpeer.add_argument("--privatekey", help="private key of server interface")
    addpeer.add_argument("--listenport", help="port to listen on", default=51820)
    addpeer.add_argument("--persistentkeepalive", help="set persistent keepalive interval")
    addpeer.add_argument("--fwmark", help="fwmark for outgoing packets")
    addpeer.add_argument("--dns", help="server interface DNS servers")
    addpeer.add_argument("--mtu", help="server interface MTU")
    addpeer.add_argument("--table", help="server routing table")
    addpeer.add_argument("--preup", help="command to run before interface is up")
    addpeer.add_argument("--postup", help="command to run after interface is up")
    addpeer.add_argument("--predown", help="command to run before interface is down")
    addpeer.add_argument("--postdown", help="command to run after interface is down")
    addpeer.add_argument(
        "--saveconfig",
        action="store_true",
        help="save server interface to config upon shutdown",
        default=None,
    )

    # AmneziaWG obfuscation parameters
    addpeer.add_argument("--jc", help="number of junk packets (3-10)", type=int)
    addpeer.add_argument("--jmin", help="minimum junk packet size (50-1000)", type=int)
    addpeer.add_argument("--jmax", help="maximum junk packet size (50-1000)", type=int)
    addpeer.add_argument("--s1", help="handshake initiation prefix size (15-150)", type=int)
    addpeer.add_argument("--s2", help="handshake response prefix size (15-150)", type=int)
    addpeer.add_argument("--h1", help="custom type for handshake initiation", type=int)
    addpeer.add_argument("--h2", help="custom type for handshake response", type=int)
    addpeer.add_argument("--h3", help="custom type for data packets", type=int)
    addpeer.add_argument("--h4", help="custom type for under-load packets", type=int)
    addpeer.add_argument("--i1", help="signature packet 1 (hex string)")
    addpeer.add_argument("--i2", help="signature packet 2 (hex string)")
    addpeer.add_argument("--i3", help="signature packet 3 (hex string)")
    addpeer.add_argument("--i4", help="signature packet 4 (hex string)")
    addpeer.add_argument("--i5", help="signature packet 5 (hex string)")

    # update existing peer information
    updatepeer = subparsers.add_parser("updatepeer")
    updatepeer.add_argument("name", help="Name used to identify this node")
    updatepeer.add_argument("--address", help="address of the server", action="append")
    updatepeer.add_argument("--endpoint", help="peer's public endpoint address")
    updatepeer.add_argument("--allowedips", help="additional allowed IP addresses", action="append")
    updatepeer.add_argument("--privatekey", help="private key of server interface")
    updatepeer.add_argument("--listenport", help="port to listen on")
    updatepeer.add_argument("--persistentkeepalive", help="set persistent keepalive interval")
    updatepeer.add_argument("--fwmark", help="fwmark for outgoing packets")
    updatepeer.add_argument("--dns", help="server interface DNS servers")
    updatepeer.add_argument("--mtu", help="server interface MTU")
    updatepeer.add_argument("--table", help="server routing table")
    updatepeer.add_argument("--preup", help="command to run before interface is up")
    updatepeer.add_argument("--postup", help="command to run after interface is up")
    updatepeer.add_argument("--predown", help="command to run before interface is down")
    updatepeer.add_argument("--postdown", help="command to run after interface is down")
    updatepeer.add_argument(
        "--saveconfig",
        action="store_true",
        help="save server interface to config upon shutdown",
        default=None,
    )

    # AmneziaWG obfuscation parameters
    updatepeer.add_argument("--jc", help="number of junk packets (3-10)", type=int)
    updatepeer.add_argument("--jmin", help="minimum junk packet size (50-1000)", type=int)
    updatepeer.add_argument("--jmax", help="maximum junk packet size (50-1000)", type=int)
    updatepeer.add_argument("--s1", help="handshake initiation prefix size (15-150)", type=int)
    updatepeer.add_argument("--s2", help="handshake response prefix size (15-150)", type=int)
    updatepeer.add_argument("--h1", help="custom type for handshake initiation", type=int)
    updatepeer.add_argument("--h2", help="custom type for handshake response", type=int)
    updatepeer.add_argument("--h3", help="custom type for data packets", type=int)
    updatepeer.add_argument("--h4", help="custom type for under-load packets", type=int)
    updatepeer.add_argument("--i1", help="signature packet 1 (hex string)")
    updatepeer.add_argument("--i2", help="signature packet 2 (hex string)")
    updatepeer.add_argument("--i3", help="signature packet 3 (hex string)")
    updatepeer.add_argument("--i4", help="signature packet 4 (hex string)")
    updatepeer.add_argument("--i5", help="signature packet 5 (hex string)")

    # delpeer deletes a peer form the database
    delpeer = subparsers.add_parser("delpeer")
    delpeer.add_argument("name", help="Name of peer to delete")

    # showpeers prints a table of all peers and their configurations
    showpeers = subparsers.add_parser("showpeers")
    showpeers.add_argument(
        "name",
        help="Name of the peer to query",
        nargs="?",
    )
    showpeers.add_argument(
        "-v",
        "--verbose",
        help="display all columns despite they hold empty values",
        action="store_true",
    )

    # generate config
    genconfig = subparsers.add_parser("genconfig")
    genconfig.add_argument(
        "name",
        help="Name of the peer to generate configuration for, \
            configuration for all peers are generated if omitted",
        nargs="?",
    )
    genconfig.add_argument(
        "-o",
        "--output",
        help="configuration file output directory",
        type=pathlib.Path,
        default=pathlib.Path.cwd() / "output",
    )

    return parser.parse_args()


# if the file is not being imported
def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_arguments()

    database_manager = DatabaseManager(args.database)

    if args.command == "init":
        database_manager.init()

    elif args.command == "addpeer":
        database_manager.addpeer(
            args.name,
            args.address,
            args.endpoint,
            args.allowedips,
            args.listenport,
            args.persistentkeepalive,
            args.fwmark,
            args.privatekey,
            args.dns,
            args.mtu,
            args.table,
            args.preup,
            args.postup,
            args.predown,
            args.postdown,
            args.saveconfig,
            # AmneziaWG parameters
            args.jc,
            args.jmin,
            args.jmax,
            args.s1,
            args.s2,
            args.h1,
            args.h2,
            args.h3,
            args.h4,
            args.i1,
            args.i2,
            args.i3,
            args.i4,
            args.i5,
        )

    elif args.command == "updatepeer":
        database_manager.updatepeer(
            args.name,
            args.address,
            args.endpoint,
            args.allowedips,
            args.listenport,
            args.persistentkeepalive,
            args.fwmark,
            args.privatekey,
            args.dns,
            args.mtu,
            args.table,
            args.preup,
            args.postup,
            args.predown,
            args.postdown,
            args.saveconfig,
            # AmneziaWG parameters
            args.jc,
            args.jmin,
            args.jmax,
            args.s1,
            args.s2,
            args.h1,
            args.h2,
            args.h3,
            args.h4,
            args.i1,
            args.i2,
            args.i3,
            args.i4,
            args.i5,
        )

    elif args.command == "delpeer":
        database_manager.delpeer(args.name)

    elif args.command == "showpeers":
        database_manager.showpeers(args.name, args.verbose)

    elif args.command == "genconfig":
        database_manager.genconfig(args.name, args.output)

    # if no commands are specified
    else:
        logger.error("No command specified\nUse awg-meshconf --help to see available commands")
