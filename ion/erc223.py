from __future__ import print_function
import sys
import argparse

from .ethrpc import EthJsonRpc
from .args import Bytes20Action, EthRpcAction, PosInt256Action
from .solproxy import solproxy


def Token(rpc, contract, account):
    return solproxy(rpc, "abi/Token.abi", contract.encode('hex'), account.encode('hex'))


def erc223_options(args):
    parser = argparse.ArgumentParser(description="ERC-223 token utility")

    parser.add_argument('-r', '--rpc', metavar="ip:port", dest='rpc', action=EthRpcAction,
                        help='Ethereum RPC address', default='127.0.0.1:8545')

    parser.add_argument('-c', '--contract', metavar="0x...20", dest='contract', action=Bytes20Action,
                        help='ERC-223 contract address', required=True)

    parser.add_argument('-a', '--account', metavar="0x...20", dest='from_account', action=Bytes20Action,
                        help='Ethereum account address', required=True)

    subparsers = parser.add_subparsers()

    transfer_group = subparsers.add_parser('transfer')
    transfer_group.add_argument('destination', action=Bytes20Action)
    transfer_group.add_argument('value', action=PosInt256Action)
    transfer_group.set_defaults(action="transfer")

    balance_group = subparsers.add_parser('balance')
    balance_group.add_argument('destination', action=Bytes20Action, nargs='*')
    balance_group.set_defaults(action="balance")

    mint_group = subparsers.add_parser('mint')
    mint_group.add_argument('value', action=PosInt256Action)
    mint_group.set_defaults(action="mint")

    burn_group = subparsers.add_parser('burn')
    burn_group.add_argument('value', action=PosInt256Action)
    burn_group.set_defaults(action="burn")

    opts = parser.parse_args(args or sys.argv[1:])

    if isinstance(opts.rpc, str):
        opts.rpc = EthJsonRpc(*opts.rpc.split(':'))

    return opts


def main(args=None):
    opts = erc223_options(args)

    token = Token(opts.rpc, opts.contract, opts.from_account)

    print("RPC Server:", opts.rpc)
    print("Contract:", opts.contract.encode('hex'))
    print("Account:", opts.from_account.encode('hex'))
    print("")

    if opts.action == "mint":
        print("Minting", opts.value)
        token.mint(opts.value)

    print(opts)

    if opts.action == "transfer":
        destination = opts.destination.encode('hex')
        print(len(destination))
        print("Transfer %r to %r" % (opts.value, destination))
        token.transfer_a9059cbb(destination, opts.value)

    if opts.action == "burn":
        print("Burning", opts.value)
        token.burn(opts.value)

    destination = getattr(opts, 'destination', [])
    if not isinstance(destination, list):
        destination = [destination]
    if not len(destination):
        destination = [opts.from_account]
    for balance_addr in destination:
        balance_addr = balance_addr.encode('hex')
        print(balance_addr, "Balance = ", token.balanceOf(balance_addr))



if __name__ == "__main__":
    main()