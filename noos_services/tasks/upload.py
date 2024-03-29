#!/usr/bin/python

import sys
# import pysftp
# import paramiko
import ftplib

# if sys.version_info.major != 3:
#    print("This utility is not compatible with Python v{}.{}.{}".format(sys.version_info.major, sys.version_info.minor,
#                                                                        sys.version_info.micro))
#    sys.exit(0)
import getopt
from os.path import isfile, abspath, split
from os import environ


# def _load_key(key_filename):
#     key_pass = ""
#     pkey = paramiko.RSAKey.from_private_key_file(key_filename, key_pass)
#     if pkey is None:
#         print('Failed to load key: {}'.format(key_filename))
#     return pkey
#
#
# def _load_keys(key_filename=None, allow_agent=True):
#     keys = []
#     default_key_path = join(expanduser("~"), '.ssh', 'id_rsa')
#     if key_filename is not None:
#         key = _load_key(key_filename)
#         keys.append(key)
#
#     if allow_agent:
#         agent = paramiko.agent.Agent()
#         for key in agent.get_keys():
#             keys.append(key)
#
#     if not keys and isfile(default_key_path):
#         key = _load_key(default_key_path)
#         keys.append(key)
#
#     if not keys:
#         print('No keys available in ssh agent or no key in {}. '
#               'Do you need to add keys to your ssh agent via '
#               'ssh-add or specify a --ssh-key-file?'.format(default_key_path))
#     return keys

# Temporary function
# def http_proxy_tunnel_connect(proxy, target, timeout=None):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.settimeout(timeout)
#     sock.connect(proxy)
#     print("connected")
#     cmd_connect = "CONNECT %s:%d HTTP/1.1\r\n\r\n" % target
#     print("--> %s" % repr(cmd_connect))
#     sock.sendall(cmd_connect)
#     response = []
#     sock.settimeout(2)  # quick hack - replace this with something better performing.
#     try:
#         # in worst case this loop will take 2 seconds if not response was received (sock.timeout)
#         while True:
#             chunk = sock.recv(1024)
#             if not chunk:  # if something goes wrong
#                 break
#             response.append(chunk)
#             if "\r\n\r\n" in chunk:  # we do not want to read too far ;)
#                 break
#     except socket.error as se:
#         if "timed out" not in se:
#             response = [se]
#     response = ''.join(response)
#     print("<-- %s" % repr(response))
#     if not "200 connection established" in response.lower():
#         raise Exception("Unable to establish HTTP-Tunnel: %s" % repr(response))
#     return sock


# def secure_copy(user, host, src, dest, key_filename=None, host_key_file=None, allow_agent=True):
#     keys = _load_keys(key_filename, allow_agent)
#     pkey = keys[0]
#     ssh = paramiko.SSHClient()
#     proxy = None
#     # proxy = paramiko.proxy.ProxyCommand("ssh NOOS_PROXY_USER@NOOS_SCP_PROXY -W %h:%p")
#     # ssh_config_file = expanduser("~/.ssh/config")
#     # if exists(ssh_config_file):
#     #     conf = paramiko.SSHConfig()
#     #     with open(ssh_config_file) as f:
#     #         conf.parse(f)
#     #     host_config = conf.lookup(host)
#     #     if 'proxycommand' in host_config:
#     #         proxy = paramiko.ProxyCommand(host_config['proxycommand'])
#     ssh.load_system_host_keys(host_key_file)
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(host, username=user, pkey=pkey, sock=proxy)
#     scp = SCPClient(ssh.get_transport())
#     scp.put(src, dest)
#     scp.close()
#     ssh.close()


def main(argv):
    log_file_name = "/tmp/test2.txt"
    log_file = open(log_file_name, "w")

    file_to_upload = ''
    host = None
    user = None
    password = None

    # Get arguments
    log_file.write("Starting upload of file to central\n")
    try:
        opts, args = getopt.getopt(argv, "h:i:d:u:p", ["ifile="])
    except getopt.GetoptError as exce:
        print(exce.msg + '\nusage: upload.py -i <inputfile>')
        log_file.write(exce.msg + '\nusage: upload.py -i <inputfile>\n')
        sys.exit(2)

    if not opts:
        print('No input file provided\nusage: upload.py -i <inputfile>')
        log_file.write('No input file provided\nusage: upload.py -i <inputfile>\n')
        sys.exit(1)

    for opt, arg in opts:
        print(opt)
        print(arg)
        if opt == '-h':
            print('usage: upload.py -i <inputfile>')
            log_file.write('usage: upload.py -i <inputfile>\n')
            sys.exit()
        if opt in ("-i", "--ifile"):
            file_to_upload = arg
        if opt == '-d':
            host = arg
        if opt == '-u':
            user = arg
        if opt == '-p':
            password = arg

    if user is None:
        user = environ.get("NOOS_SFTP_USER")
        if user is None:
            print("No NOOS_SFTP_USER defined and exported in bash environment")
            log_file.write("No NOOS_SFTP_USER defined and exported in bash environment\n")
            assert user is not None
    if host is None:
        host = environ.get("NOOS_SFTP_HOST")
        if host is None:
            print("No NOOS_SFTP_HOST defined and exported in bash environment")
            log_file.write("No NOOS_SFTP_HOST defined and exported in bash environment\n")
            assert host is not None
    # TODO : Replace password with keyfile location (NOOS_SFTP_KEYFILE)
    if password is None:
        password = environ.get("NOOS_SFTP_PWD")
        if password is None:
            print("No NOOS_SFTP_PWD defined and exported in bash environment\n")
            log_file.write("No NOOS_SFTP_PWD defined and exported in bash environment\n")
            assert password is not None

    dest = "noosdrift"

    print("Python v{}.{}.{} - NOOS-Drift Upload utility".format(sys.version_info.major, sys.version_info.minor,
                                                                sys.version_info.micro))
    log_file.write("Python v{}.{}.{} - NOOS-Drift Upload utility\n".format(sys.version_info.major,
                                                                           sys.version_info.minor,
                                                                           sys.version_info.micro))
    print("-----------------------------------------")
    log_file.write("-----------------------------------------\n")

    if not isfile(file_to_upload):
        print('The file "' + file_to_upload + '" does not exist.')
        log_file.write('The file "{}" does not exist.\n'.format(file_to_upload))
        sys.exit(2)

    print('File to upload is: "{}"'.format(file_to_upload))
    log_file.write('File to upload is: "{}"\n'.format(file_to_upload))
    src = abspath(file_to_upload)
    path, filename = split(src)
    # secure_copy(user, host, src, dest, key_filename="")
    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None
    # with pysftp.Connection(host, username=user, password=password, cnopts=cnopts) as sftp:
    #     with sftp.cd(dest):  # temporarily chdir to test_sftp
    #        sftp.put(src)  # upload file to public/ on remote

    try:
        log_file.write("Trying to upload file \'{}\'\n".format(file_to_upload))
        with ftplib.FTP(host, user, password) as session:
            with open(src, 'rb') as result_archive:
                if dest != '':
                    session.cwd(dest)
                session.storbinary("STOR {}".format(filename), result_archive)
        log_file.write("Upload of file \'{}\' OK\n".format(file_to_upload))
    except ftplib.all_errors as ftperrs:
        log_file.write("Error {} uploading file \'{}\'\n".format(ftperrs, file_to_upload))
        raise ftperrs
    except Exception as otherexc:
        log_file.write("Error {} uploading file \'{}\'\n".format(otherexc, file_to_upload))
        raise otherexc
    finally:
        log_file.close()


if __name__ == "__main__":
    file_name = "/tmp/test.txt"
    file = open(file_name, "w")
    file.write("test")

    try:
        main(sys.argv[1:])
    except Exception as exc:
        file.write("{}\n".format(exc))
        sys.exit(2)
    finally:
        file.close()
