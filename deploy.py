#!/usr/bin/env python
#-*- coding: utf-8 -*-
import argparse
import os
import subprocess
import shutil
import shlex

script_path = os.path.dirname(__file__)

def execute(command):
    if isinstance(command, str):
        command = shlex.split(command)
    return subprocess.check_output(command).decode('utf-8')


def _change_perm(path, apache_user='www-data', permission=0o770):
    shutil.chown(path, apache_user, apache_user)
    return os.chmod(path, permission)


def git_unlock(**args):
    os.chdir(args['project_path'])
    try:
        execute('git-crypt unlock')
        return 'Unlocked git repo'
    except FileNotFoundError:
        pass

'''Clones git repo and adds 
'''
def git_clone(**args):
    if args['reinit']:
        shutil.rmtree(args['project_path'], ignore_errors=True)
    if not os.path.exists(args['project_path']):
        os.makedirs(args['project_path'], exist_ok=True)
        shutil.chown(args['project_path'], args['user'])

        execute('git clone {git_repo_path} {project_path}'.format(**args))
        return 'Cloned git repo'


def git_update(**args):
    os.chdir(args['project_path'])
    execute('git pull origin master')
    return 'Updated git repo'


'''Tries to create new python virtual environment and install any project requirements 
'''
def virtualenv(**args):
    if args['reinit']:
        shutil.rmtree(args['virtualenv'], ignore_errors=True)
    if not os.path.exists(args['virtualenv']):
        execute('virtualenv --python={python_ver} {virtualenv}'.format(**args))
        execute('{}/bin/pip install -r {}/requirements.txt'.format(args['virtualenv'], args['project_path']))
        return 'Installed python with requirements'


def create_www_dirs(**args):
    var_www = '{www_dir}/{project}'.format(**args)
    if args['reinit'] or not os.path.exists('{www_dir}/{project}'.format(**args)):
        os.makedirs(var_www, exist_ok=True)
        _change_perm(var_www, args['apache_user'])
        return 'Created {} successfully'.format(var_www)


'''Creates apache configuration files from templates
'''
def create_apache_configs(**args):
    args['virtualenv'] += '/lib/{python_ver}/site-packages'.format(**args)
    created_configs = []
    os.chdir(script_path)
    for template_filename, template_name in ((args['template_common'], 'common'), (args['template_http'], 'http'), (args['template_https'], 'https')):
        config_filename = '{}/sites-available/{}_{}.conf'.format(args['apache_dir'], args['project'], template_name)
        if args['reinit']:
            shutil.rmtree(config_filename, ignore_errors=True)
        if not os.path.exists(config_filename):
            with open(template_filename, 'r') as template_file:
                template = template_file.read()
            template = template.format(**args)
            with open(config_filename, 'w') as apache_conf:
                apache_conf.write(template)
    if created_configs:
        created_configs = 'Successfully created apache configs: {}'.format(' '.join(created_configs))
    return created_configs


'''Enables site with name_protocol and reloads apache
'''
def _enable_site(name, protocol):
    execute('a2ensite {}_{}'.format(name, protocol))
    return execute('service apache2 reload')

'''Enables http site and reloads apache
'''
def enable_http_site(**args):
    return _enable_site(args['project'], 'http')


'''Enables https site and reloads apache
'''
def enable_https_site(**args):
    if not args['disable_https']:
        return _enable_site(args['project'], 'https')

'''Creates ssl certificates from LetsEncrypt
'''
def letsencrypt_https(**args):
    if not args['disable_https'] and (args['reinit'] or not os.path.exists(args['letsencrypt_dir'])):
        return execute('{letsencrypt_certbot} certonly --webroot --webroot-path {www_dir}/{project} --renew-by-default --text --agree-tos -d {domain} -d www.{domain} {certbot_arguments}'.format(**args))


'''Calls django management command
'''
def _call_command(command, **args):
    return execute('{virtualenv}/bin/python {project_path}/manage.py {command} --no-input'.format(command=command, **args))

'''Migrates django db
'''
def migrate(**args):
    if args['sqlite_path']:
        parent_folder = os.path.split(args['sqlite_path'])[0]
        os.makedirs(parent_folder, exist_ok=True)
        _change_perm(parent_folder, args['apache_user'])
    _call_command('migrate', **args)
    if args['sqlite_path']:
        _change_perm(args['sqlite_path'], args['apache_user'])
    return 'Successfully migrated the db'

'''Collects static resources from django
'''
def collectstatic(**args):
    _call_command('collectstatic', **args)
    return 'Successfully collected static resources'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--http_port', action='store', dest='http_port', default='80',
                        help='HTTP port to use in apache config.')
    parser.add_argument('--disable_http2', action='store_true', dest='disable_https',
                        help='Whether to disable h2/h2c protocol in the apache config')
    parser.add_argument('--disable_https', action='store_true', dest='disable_https',
                        help='Whether to create certificate from LetsEncrypt and start https apache virtual host.')
    parser.add_argument('--https_port', action='store', dest='https_port', default='443', help='HTTPS port to use in apache config.')
    parser.add_argument('--letsencrypt_dir', action='store', dest='letsencrypt_dir', default='/etc/letsencrypt/live/{domain}', help='Where are LetsEncrypt certificates stored')
    parser.add_argument('--letsencrypt_certbot', action='store', dest='letsencrypt_certbot', default='/opt/letsencrypt/certbot-auto', help='Where is the LetsEncrypt certbot executable')
    parser.add_argument('--certbot_arguments', action='store', dest='certbot_arguments', default='', help='Additional arguments to pass to certbot (pass them the same way you would call certbot directly)')
    parser.add_argument('--apache_dir', action='store', dest='apache_dir', default='/etc/apache2/', help='Where are the Apache configs stored')
    parser.add_argument('--apache_user', action='store', dest='apache_user', default='www-data',
                        help='Apache user name')
    parser.add_argument('--www_dir', action='store', dest='www_dir', default='/var/www/',
                        help='Where is the public www directory')
    
    parser.add_argument('--template_common', action='store', dest='template_common', default='./template_common.txt', help='Common template for apache config')
    parser.add_argument('--template_http', action='store', dest='template_http', default='./template_http.txt', help='Template specifically for HTTP virtual host')
    parser.add_argument('--template_https', action='store', dest='template_https', default='./template_https.txt', help='Template specifically for HTTPS virtual host')


    parser.add_argument('--python_ver', action='store', dest='python_ver', default='python3.4', help='Python version to use for virtual environment')
    parser.add_argument('--user', action='store', dest='user', default='dio', help='Default linux user to assign the project to')
    parser.add_argument('--virtualenv', action='store', dest='virtualenv', default='/home/dio/.virtualenvs/{project}/', help='Path to virtualenv, it gets created if it does not exist yet')
    parser.add_argument('--project_path', action='store', dest='project_path', default='/opt/{project}/', help='Where to store the project')
    parser.add_argument('--git_repo_path', action='store', dest='git_repo_path', default='/opt/git/{project}.git/',
                        help='Path to the git repo')
    parser.add_argument('--sqlite_path', action='store', dest='sqlite_path', help='Include if you are using sqlite db in your django project as it needs some permission changes after migration.')

    parser.add_argument('--reinit', action='store_true', dest='reinit', help='Whether to force recreating/redoing everything')
    parser.add_argument('project', action='store', help='Project name used for directories')
    parser.add_argument('domain', action='store', help='Domain name used in apache config')
    args = parser.parse_args()
    args = vars(args)

    if os.getuid() != 0:
        class NotSudo(Exception):
            pass


        raise NotSudo("The script needs sudo privileges.")

    for name in args:
        if isinstance(args[name], str):
            args[name] = args[name].format(**args)
    if args['disable_https']:
        args['http2'] = ''
        args['http2c'] = ''
    else:
        args['http2'] = 'h2'
        args['http2c'] = 'h2c'


    pipeline = [git_clone, git_update, git_unlock, virtualenv, create_www_dirs, migrate, collectstatic, create_apache_configs, enable_http_site, letsencrypt_https, enable_https_site]
    for func in pipeline:
        result = func(**args)
        if result:
            print(result)
        else:
            print('{} skipped.'.format(func.__name__))
