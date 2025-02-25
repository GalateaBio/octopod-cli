import datetime
import os
from typing import Optional

import paramiko as paramiko

from octopod_wrapper import OctopodException


class OctopodSftpClient:
    sftp_host: str
    sftp_user: str
    sftp_password: Optional[str]
    sftp_keyfile: Optional[str]

    def __init__(
        self,
        sftp_host: str,
        sftp_user: str,
        sftp_password: Optional[str],
        sftp_keyfile: Optional[str],
    ) -> None:
        super().__init__()
        if not sftp_host:
            raise OctopodException('sftp_host arg is empty')
        if not sftp_user:
            raise OctopodException('sftp_user arg is empty')
        if not sftp_password and not sftp_keyfile:
            raise OctopodException('sftp_password and sftp_keyfile args are empty. But one of them should have value')

        self.sftp_host = sftp_host
        self.sftp_user = sftp_user
        self.sftp_password = sftp_password
        self.sftp_keyfile = sftp_keyfile

    def upload_file_from_file(
        self,
        file_name: str,
        remote_filename: Optional[str] = None,
        remote_folder: Optional[str] = None,
    ) -> str:
        """
            Upload a local file.

            Keyword Args:
                file_name: Full path to the file to upload.
                remote_filename: Filename on SFTP. If None or empty will be fetched from file_name arg.
                remote_folder: Folder for file on SFTP. If None or empty will be generated automatically.

            Returns:
                str: SFTP file name.
        """
        if not file_name:
            raise OctopodException('file_name arg is empty')

        if not remote_filename:
            _, tail = os.path.split(file_name)
            remote_filename = tail

        if not remote_folder:
            remote_folder = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        conn_kwargs = {
            'hostname': self.sftp_host,
            'username': self.sftp_user,
        }

        if self.sftp_password:
            conn_kwargs['password'] = self.sftp_password
        if self.sftp_keyfile:
            conn_kwargs['key_filename'] = self.sftp_keyfile

        ssh_client.connect(**conn_kwargs)

        try:
            with ssh_client.open_sftp() as sftp:
                try:
                    sftp.chdir(remote_folder)
                except IOError:
                    sftp.mkdir(remote_folder)
                    sftp.chdir(remote_folder)

                sftp.put(file_name, remote_filename)
        finally:
            ssh_client.close()

        return f'{remote_folder}/{remote_filename}'
