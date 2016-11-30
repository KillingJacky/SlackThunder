#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import os
import re
import time
import logging
import verification_code
from yc_api import *
from slackclient import SlackClient
import config

if "SLACK_TOKEN" not in os.environ:
    print "You should specify a env variable named 'SLACK_TOKEN'."
    sys.exit(1)

SLACK_TOKEN = os.environ["SLACK_TOKEN"]

logger = logging.getLogger()

def pretty_print_list(l, columns=[], with_index=True, check_index=-1):
    result = ''
    header = ''

    if with_index:
        header = 'index, '
    for c in columns:
        header += '{}, '.format(c)
    header = header.rstrip(', ')

    index = 0
    for item in l:
        if check_index == index:
            result += '[x] '
        elif check_index >= 0:
            result += '[ ] '
        if with_index:
            result += '{}. '.format(index)
            index += 1
        for c in columns:
            if c not in item:
                return header + '\n' + 'column {} not exist'.format(c)
            result += u'{}, '.format(item.get(c, '-'))
        result = result.rstrip(', ') + '\n'

    return header + '\n' + result


def format_task_list(tasks):
    output = []
    for t in tasks:
        t['speed'] = str_filesize(t['speed']) + '/s'
        t['progress'] = '{:.2%}'.format(t['progress'] / 10000.00)
        output.append(t)
    return output

def process_slack_msg(msg, dl):
    text = msg.get('text')

    if re.search(r'login', text):
        if dl.has_logged_in():
            return 'Already logged in.'
        dl.login()
        if dl.has_logged_in():
            return 'Logged in.'
        else:
            return 'Login failed.'

    elif re.search(r'logout', text):
        dl.logout()
        return 'Logged out.'

    elif re.search(r'listdev', text):
        peers = dl.list_peer()
        return pretty_print_list(peers, ['name'])

    elif re.search(r'select (\d+)', text):
        try:
            index = int(re.search(r'select (\d+)', text).group(1))
            peers = dl.list_peer()
            if index+1 > len(peers):
                return 'index exceed range'
            peer = peers[index]
            dl.select_peer(peer.get('pid'))
            return pretty_print_list(peers, ['name'], check_index=index)
        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'adddir (\S+)', text):
        try:
            dir = re.search(r'adddir (\S+)', text).group(1)
            dl.add_target_dir(dir)
            dir_list = dl.list_target_dirs()
            if not dir_list:
                return '[]\n'
            else:
                return str(dir_list)+'\n'

        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'listdir', text):
        try:
            dir_list = dl.list_target_dirs()
            dirs = []
            for d in dir_list:
                dirs.append({'name': d})
            return pretty_print_list(dirs, ['name'])

        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'rmdir (\d+)', text):
        try:
            dir_index = int(re.search(r'rmdir (\d+)', text).group(1))
            dl.remove_target_dir(dir_index)
            dir_list = dl.list_target_dirs()
            if not dir_list:
                return '[]\n'
            else:
                return str(dir_list)+'\n'

        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'cleardir', text):
        try:
            dl.clear_target_dirs()
            dir_list = dl.list_target_dirs()
            if not dir_list:
                return '[]\n'
            else:
                return str(dir_list)+'\n'

        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'ping', text):
        return 'pong\n'

    elif re.search(r'info|list$', text):
        try:
            result = u'current downloader: {}\n\n'.format(dl.get_selected_peer_name())

            tasks = dl.list_downloading()
            result += 'downloading tasks:\n'
            result += pretty_print_list(format_task_list(tasks), ['name', 'speed', 'progress'])
            result += '\n'

            return result
        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'listfini', text):
        try:
            result = u'current downloader: {}\n\n'.format(dl.get_selected_peer_name())

            tasks = dl.list_finished(0, 10)
            result += 'finished tasks:\n'
            result += pretty_print_list(format_task_list(tasks), ['name', 'speed', 'progress'])

            return result
        except Exception as e:
            logger.warning(e)
            return str(e)

    elif re.search(r'rmtask (\d+)', text):
        try:
            task_index = int(re.search(r'rmtask (\d+)', text).group(1))
            tasks = dl.list_downloading()
            if task_index+1 > len(tasks):
                return 'index exceed reange.'
            task = tasks[task_index]

            result = dl.trash_task(task.get('id'), task.get('state'))
            return str(result)

        except Exception as e:
            logger.warning(e)
            return str(e)

    else:
        m = re.search(r'(magnet\:|ed2k\:|http\:|https\:|ftp\:)(\S+) (\d+)', text)
        if m:
            try:
                url = m.group(1) + m.group(2)
                url = url.rstrip('>')
                dir_index = int(m.group(3))
                print('download into dir index: {}'.format(dir_index))

                dir_list = dl.list_target_dirs()

                if dir_index+1 > len(dir_list):
                    return 'index exceed range'
                result = dl.create_task(url, dir_index)
                return str(result)
            except Exception as e:
                logger.warning(e)
                return str(e)

        m = re.search(r'(magnet\:|ed2k\:|http\:|https\:|ftp\:)(\S+)', text)
        if m:
            try:
                url = m.group(1) + m.group(2)
                url = url.rstrip('>')
                result = dl.create_task(url)
                return str(result)
            except Exception as e:
                logger.warning(e)
                return str(e)



    return """Commands:
1. `login`
2. `logout`
3. `listdev` - list the downloader devices
4. `select {index}` - select the downloader
5. `adddir {dir}` - add a preset download target dir
6. `listdir` - list all the saved target dirs
7. `rmdir {dir}` - remove a preset download target dir
8. `cleardir` - clear all the saved target dirs
9. `{url}` - download into the default target dir (configured on yc.xunlei.com)
10. `{url} {index}` - download into the index selected target dir
11. `info` or `list` - list the downloading status
12. `listfini` - list the finished tasks (recent 10)
14. `rmtask {index}` - stop the index selected task and trash it
14. `ping` - test if the slack script is working
""".replace("\r\n", "\n")



if __name__ == '__main__':

    verification_code_reader = verification_code.default_verification_code_reader('file', config.thunder.get('verification_image_path'))
    auto_login = True
    dl = ThunderRemoteDownload(config.thunder.get('username'), config.thunder.get('password'), config.thunder.get('cookie_path'), auto_login, verification_code_reader)

    sc = SlackClient(SLACK_TOKEN)

    resp = sc.api_call(
        "channels.list",
        exclude_archived=1
    )
    if resp.get('ok') != True:
        logger.error('slack api call error')
        sys.exit()

    channels = resp.get('channels')

    config_channel = config.slack_channel
    channel_id = None
    for ch in channels:
        if ch.get('name') == config_channel:
            channel_id = ch.get('id')

    if not channel_id:
        resp = sc.api_call(
            'channels.create',
            name = config_channel
        )
        if resp.get('ok') != True:
            logger.error('slack api call error')
            sys.exit()
        channel_id = resp.get('channel').get('id')

    time.sleep(1)

    skip_first_msg = 0
    if sc.rtm_connect():
        while True:
            msgs = None
            try:
                msgs = sc.rtm_read()
            except Exception as e:
                logger.warning(e)
                continue

            if msgs and isinstance(msgs, list) and len(msgs) > 0:
                for msg in msgs:
                    #print msg
                    if msg.get('type') == 'hello': logger.info('connected')
                    if msg.get('type') != 'message': continue
                    if msg.get('channel') != channel_id: continue
                    if 'subtype' in msg: continue

                    # the last message will be retrieved when the RTM client connects in
                    # but we're not interested in this message
                    if not skip_first_msg:
                        skip_first_msg = 1
                        continue

                    logger.info('-------------------')
                    result = process_slack_msg(msg, dl)
                    if result[-1] != '\n': result += '\n'
                    result += '----\n'
                    logger.info(result)
                    sc.rtm_send_message(channel_id, result)
                    # send message with the Web API will be better, but I'm facing badly network connection
                    # issues with this type API. Rather, have to fallback to the ugly RTM API.
                    # while(result):
                    #     resp = sc.api_call(
                    #         'chat.postMessage',
                    #         channel = channel_id,
                    #         text = result,
                    #         username = '迅雷远程'
                    #     )
                    #     if resp.get('ok'): break;
                    #     break
                    #     time.sleep(2)
                    logger.info('-------------------')
            time.sleep(1)
    else:
        logger.error("Connection Failed, invalid token?")


