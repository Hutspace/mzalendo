#!/usr/bin/env python

"""
Odekro deployment script
"""

import os, re , time

from fabric.api import task
from fabric.api import hide, settings, cd, env, prefix, put, get, require
from fabric.api import local, run, sudo
from fabric.contrib.files import exists

from fab import postgres as pg
from fab import server, nginx, webapp


LOCAL_BASEDIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTION_ENV_USER = 'root'
STAGING_ENV_USER    = 'root'
PRODUCTION_ENV_PASS = None
STAGING_ENV_PASS    = None


env.local_root = LOCAL_BASEDIR
env.use_ssh_config = True

env.project = 'mzalendo'
env.git_remote = "origin"
env.git_branch = "odekro"
env.pip_requirements = 'requirements.txt'
env.local_settings = 'deploy/local_settings.py'
env.log_level = 'debug'

env.dbname = 'odekro'
env.dbuser = 'postgres'

env.webapp_user = 'odekro_webapp'
env.webapp_group = 'odekro_webapp'

env.basedir = '/var/www/%(project)s' % env
env.virtualenv = env.basedir
env.is_staging = True


@task
def odekro(cmd):
    webapp.ctl(cmd)

@task
def app(cmd, args='', version='current'):
    require('basedir')
    require('project')

    basedir = env.basedir
    project = env.project
    virtualenv = basedir
    
    if args:
        args = ' %s' % args

    project_home = '%(basedir)s/releases/%(version)s/%(project)s' % locals()
    with cd(project_home):
        webapp._sudo(('source %(virtualenv)s/bin/activate && '
                  # 'cd %(project_home)s && '
                      '%(virtualenv)s/bin/python manage.py %(cmd)s%(args)s') % locals())

@task
def deploy(db=None, dbuser=None, dbpasswd=None, email_passwd=None, 
           version=None, init='yes'):
    """Deploy latest (or a specific version) of the site.
        
    Deploys a version to the servers, install any required third party 
    modules, install the virtual host and then restart the web app server
    """
    require('hosts', provided_by=[vm, staging, production])
    require('basedir')
    require('virtualenv')
    require('webapp_user')
    require('git_branch')

    restart = False

    try:
        webapp.stop()
    except: pass

    if not version:
        env.version = time.strftime('%Y%m%d%H%M%S')
        
        webapp.upload()
        webapp.install()

        if db and dbuser and dbpasswd:
            configure(db, dbuser, dbpasswd, email_passwd, env.version)

        if init is 'yes':
            webapp.init()

        # ensite nginx.conf -> odekro
        try:
            nginx.dissite('default')
        except: pass

        try:
            nginx.dissite('odekro')
        except: pass
        
        nginx.ensite('%(basedir)s/releases/%(version)s/conf/nginx.conf' % env,
                     'odekro')

        restart = True
    else:
        #TODO check to see if version exists
        # env.version = version
        # _symlink_current_version()
        pass   

    if restart: 
        nginx.reload()
        webapp.start()

@task
def setup():
    require('hosts', provided_by=[vm, staging, production])
    require('webapp_user')
    require('basedir')
    require('virtualenv')
    
    try:
        webapp.stop()
    except: pass

    prepare()

    setup_postgis()
    setup_db()
    
    if not exists('/etc/init.d/nginx'):
        nginx.install()

@task
def prepare():
    require('hosts')
    require('webapp_user')

    server.install_packages()    
    server.create_webapp_user()
    webapp.prepare()

@task
def setup_postgis():    
    require('hosts', provided_by=[vm, staging, production])
    require('basedir')
    require('virtualenv')

    try:
        # install postgres and postgis
        pg.setup_postgis()
    except: pass

@task
def clean():
    require('hosts', provided_by=[vm, staging, production])
    require('basedir')
    require('virtualenv')
    
    try:
        webapp.stop()
    except: pass
    
    try:
        sudo('rm -fr %(basedir)s' % env)
    except: pass

@task
def init():
    webapp.init()

# ADHOC

@task
def configure(db=env.dbname, dbuser=env.dbuser, dbpasswd='', email_passwd='', version='current'):
    setup_db(db, dbuser, dbpasswd)
    configure_webapp(db, dbuser, dbpasswd, email_passwd, version)

@task
def setup_db(db=env.dbname, dbuser=env.dbuser, dbpasswd=''):
    if not pg.user_exists(dbuser):
        pg.create_user(dbuser, dbpasswd, groups=['gisgroup'])
    if not pg.database_exists(db):
        pg.create_database(db, dbuser, template='template_postgis')

@task
def configure_webapp(db=env.dbname, dbuser=env.dbuser, dbpasswd='', email_passwd='', version='current'):
    env.version = version
    webapp.configure(db=db, dbuser=dbuser, dbpasswd=dbpasswd, email_passwd=email_passwd)

try:
    from local_fabfile import *
except ImportError as e:
    pass


# ENVIRONMENTS

@task
def production():
    env.hosts = ['208.68.37.14']
    env.user = PRODUCT_ENV_USER # update this in the local_fabfile.py file
    if PRODUCT_ENV_PASS:
        env.password = PRODUCT_ENV_PASS
    env.domain = 'odekro.org'
    env.log_level = 'info'
    env.is_staging = False

@task
def staging():
    env.hosts = ['208.68.37.14']
    env.user = STAGING_ENV_USER # update this in the local_fabfile.py file
    if STAGING_ENV_USER:
        env.password = STAGING_ENV_PASS
    env.domain = 'staging.odekro.org'
    env.log_level = 'debug'

@task
def dev():
    """local machine."""
    env.hosts = ['0.0.0.0']

