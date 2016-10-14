import json
import os

from cnr.exception import (Forbidden, PackageAlreadyExists)
from cnr.models.package_base import PackageBase
from cnr.models.channel_base import ChannelBase


class CnrDB(object):
    Channel = ChannelBase
    Package = PackageBase

    @classmethod
    def restore_backup(cls, data):
        """ bulk add data in db """
        i = 0
        size = len(data['packages'])
        for package_data in data['packages']:
            i += 1
            package = cls.Package(package_data['package'],
                                  package_data['release'],
                                  package_data['media_type'])
            package.data = package_data
            try:
                package.save(False)
                print '%s/%s  restored: %s(%s) - %s' % (str(i), str(size),
                                                        package.package, package.version, package.media_type)
            except PackageAlreadyExists:
                print '%s/%s  existed: %s(%s) - %s' % (str(i), str(size),
                                                       package.package, package.version, package.media_type)

            for channel_name in package_data['channels']:
                channel = cls.Channel(channel_name, package.package)
                channel.add_release(package.version, cls.Package)
                print "%s/%s  restored-channel-release: %s, %s, %s" % (str(i), str(size),
                                                                       channel.package, channel.name, package.version)

        i = 0
        size = len(data['channels'])
        for channel_data in data['channels']:
            i += 1
            channel = cls.Channel(channel_data['name'], channel_data['package'])
            channel.current = channel_data['current']
            channel.save(True)
            print "%s/%s  restored-channel: %s" % (str(i), str(size), channel.name)

    @classmethod
    def restore_backup_from_file(cls, filepath):
        """ bulk add data in db """
        with open(filepath, 'rb') as f:
            data = json.load(f)
        return cls.restore_backup(data)

    @classmethod
    def reset_db(cls, force=False):
        """ clean the database """
        if os.getenv("CNR_DB_ALLOW_RESET", "false") == "true":
            raise NotImplementedError
        else:
            raise Forbidden("Reset DB is deactivated")

    @classmethod
    def backup(cls):
        data = {'packages': cls.Package.dump_all(),
                'channels': cls.Channel.dump_all()}
        return data

    @classmethod
    def backup_to_file(cls, filepath):
        with open(filepath, 'wb') as f:
            json.dump(cls.backup(), f)
