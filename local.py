from octopod_wrapper import OctopodClient

if __name__ == '__main__':
    dev_api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcxNTg5MDc5LCJpYXQiOjE3NDAwNTMwNzksImp0aSI6ImM5ZGU4NDkwNzRmYTQ2OGZiMzZmYThlMmM1Mjk2NTRlIiwidXNlcl9pZCI6ImM2ZjM1NTFjLWUzNTQtNDQwZS05ZTMyLWY3NjUxZjdhZDBlYiJ9.4zViqRdapxUXkTAp-1qWcCvRW5U0aSFFyvkoKx5TbLg'
    client = OctopodClient('https://api.dev.galatea.bio', dev_api_key)
    client.file_api.download_file('fb4012e2-2eee-48d7-a899-bbaf5248d2bb')
