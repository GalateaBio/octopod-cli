import argparse

from octopod_cli.config_commands import SetConfigCommand, GetConfigCommand, ClearConfigCommand
from octopod_cli.file_commands import UploadFileViaApiCommand, UploadFileViaSftpCommand, FindFileCommand, \
    DeleteFileCommand, UpdateFileSampleAliasCommand, DownloadFileCommand
from octopod_cli.order_commands import SubmitOrderCommand, CancelOrderCommand, UpdateOrderTagsCommand, FindOrderCommand
from octopod_cli.organization_commands import GetOrganizationModelsCommand, GetOrganizationInfoCommand
from octopod_cli.result_commands import ListResultPdfReportsCommand, DownloadResultFileCommand, \
    DownloadResultJsonCommand, ListResultSamplesCommand
from octopod_cli.tag_commands import CreateTagCommand, ListTagsCommand, FindTagCommand, UpdateTagCommand


def main():
    parser = argparse.ArgumentParser('octo', add_help=True)

    commands = [
        SetConfigCommand(),
        GetConfigCommand(),
        ClearConfigCommand(),
        UploadFileViaApiCommand(),
        UploadFileViaSftpCommand(),
        FindFileCommand(),
        DeleteFileCommand(),
        UpdateFileSampleAliasCommand(),
        DownloadFileCommand(),
        GetOrganizationModelsCommand(),
        GetOrganizationInfoCommand(),
        SubmitOrderCommand(),
        CancelOrderCommand(),
        UpdateOrderTagsCommand(),
        FindOrderCommand(),
        CreateTagCommand(),
        ListTagsCommand(),
        FindTagCommand(),
        UpdateTagCommand(),
        ListResultPdfReportsCommand(),
        DownloadResultFileCommand(),
        DownloadResultJsonCommand(),
        ListResultSamplesCommand(),
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
