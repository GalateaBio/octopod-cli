from typing import Optional

import paramiko as paramiko


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
        self.sftp_host = sftp_host
        self.sftp_user = sftp_user
        self.sftp_password = sftp_password
        self.sftp_keyfile = sftp_keyfile

    def upload_file_from_file(self, file_name: str, remote_filename: str, remote_folder: str):
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
