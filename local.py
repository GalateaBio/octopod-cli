import argparse

from octopod_cli import SetConfigCommand, GetConfigCommand, UploadFileViaApiCommand, UploadFileViaSftpCommand


def main():
    parser = argparse.ArgumentParser('octopod-cli')

    commands = [
        SetConfigCommand(),
        GetConfigCommand(),
        UploadFileViaApiCommand(),
        UploadFileViaSftpCommand(),
    ]

    subparsers = parser.add_subparsers()
    for command in commands:
        command.add_args(subparsers, parser)

    args = parser.parse_args()

    if not hasattr(args, 'command'):
        return

    command_arg = args.command
    for command in commands:
        if command_arg == command.command_name:
            command.run_command(args)
            break


if __name__ == '__main__':
    main()
