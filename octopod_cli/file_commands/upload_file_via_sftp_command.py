from octopod_cli import BaseCommand, get_config
from octopod_wrapper import OctopodSftpClient


class UploadFileViaSftpCommand(BaseCommand):
    @property
    def command_name(self) -> str:
        return 'sftp-upload-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Upload file via SFTP')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_name',
            required=True,
            help='Full path to the file to upload',
            type=str,
        )
        self._command_parser.add_argument(
            '--remote_file_name',
            nargs='?',
            default=None,
            help='Filename on SFTP. If None or empty will be fetched from file_name arg',
            type=str,
        )
        self._command_parser.add_argument(
            '--remote_folder',
            nargs='?',
            default=None,
            help='Folder for file on SFTP. If None or empty will be generated automatically',
            type=str,
        )

    def run_command(self, args):
        config = get_config()
        if config is None:
            print('ERROR! Config not set. Please use set-config command')
            return

        if not config.sftp_host or not config.sftp_user or not config.sftp_keyfile_path:
            print(
                'ERROR! sftp_host or sftp_user or sftp_keyfile_path not configured. '
                'Please use set-config command with correct arguments'
            )
            return

        sftp_client = OctopodSftpClient(
            sftp_host=config.sftp_host,
            sftp_user=config.sftp_user,
            sftp_password=None,
            sftp_keyfile=config.sftp_keyfile_path,
        )
        result = sftp_client.upload_file(
            file_name=args.file_name,
            remote_filename=args.remote_file_name,
            remote_folder=args.remote_folder,
        )
        print(result)
