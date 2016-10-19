# Python-based automated deployment scripts

This is a simple collection of scripts for deployment customized for my use (Django+Apache+LetsEncrypt).
I felt like Puppet/Chef was a overkill for my use-case, so I cobbled this together. Hopefully it will be useful for someone.


## Pipeline
Default pipeline is: 

1. git_clone ~optional
2. git_update
3. git_unlock ~optional
4. virtualenv ~optional
5. create_www_dirs ~optional
6. migrate
7. collectstatic
8. create_apache_configs ~optional
9. enable_http_site
10. letsencrypt_https ~optional
11. enable_https_site ~optional


## Usage
You need sudo privileges to run this.

```bash
$ sudo python deploy.py
usage: deploy.py [-h] [--http_port HTTP_PORT] [--disable_http2]
                 [--disable_https] [--https_port HTTPS_PORT]
                 [--letsencrypt_dir LETSENCRYPT_DIR]
                 [--letsencrypt_certbot LETSENCRYPT_CERTBOT]
                 [--certbot_arguments CERTBOT_ARGUMENTS]
                 [--apache_dir APACHE_DIR] [--apache_user APACHE_USER]
                 [--www_dir WWW_DIR] [--template_common TEMPLATE_COMMON]
                 [--template_http TEMPLATE_HTTP]
                 [--template_https TEMPLATE_HTTPS] [--python_ver PYTHON_VER]
                 [--user USER] [--virtualenv VIRTUALENV]
                 [--project_path PROJECT_PATH] [--git_repo_path PROJECT_PATH]
                 [--sqlite_path SQLITE_PATH] [--reinit]
                 project domain

positional arguments:
  project               Project name used for directories
  domain                Domain name used in apache config

optional arguments:
  -h, --help            show this help message and exit
  --http_port HTTP_PORT
                        HTTP port to use in apache config. (default: 80)
  --disable_http2       Whether to disable h2/h2c protocol in the apache
                        config (default: False)
  --disable_https       Whether to create certificate from LetsEncrypt and
                        start https apache virtual host. (default: False)
  --https_port HTTPS_PORT
                        HTTPS port to use in apache config. (default: 443)
  --letsencrypt_dir LETSENCRYPT_DIR
                        Where are LetsEncrypt certificates stored (default:
                        /etc/letsencrypt/live/{domain})
  --letsencrypt_certbot LETSENCRYPT_CERTBOT
                        Where is the LetsEncrypt certbot executable (default:
                        /opt/letsencrypt/certbot-auto)
  --certbot_arguments CERTBOT_ARGUMENTS
                        Additional arguments to pass to certbot (pass them the
                        same way you would call certbot directly) (default: )
  --apache_dir APACHE_DIR
                        Where are the Apache configs stored (default:
                        /etc/apache2/)
  --apache_user APACHE_USER
                        Apache user name (default: www-data)
  --www_dir WWW_DIR     Where is the public www directory (default: /var/www/)
  --template_common TEMPLATE_COMMON
                        Common template for apache config (default:
                        template_common.txt)
  --template_http TEMPLATE_HTTP
                        Template specifically for HTTP virtual host (default:
                        template_http.txt)
  --template_https TEMPLATE_HTTPS
                        Template specifically for HTTPS virtual host (default:
                        template_https.txt)
  --python_ver PYTHON_VER
                        Python version to use for virtual environment
                        (default: python3.4)
  --user USER           Default linux user to assign the project to (default:
                        dio)
  --virtualenv VIRTUALENV
                        Path to virtualenv, it gets created if it does not
                        exist yet (default: /home/dio/.virtualenvs/{project}/)
  --project_path PROJECT_PATH
                        Where to store the project (default: /opt/{project}/)
  --git_repo_path PROJECT_PATH
                        Path to the git repo (default:
                        /opt/git/{project}.git/)
  --sqlite_path SQLITE_PATH
                        Include if you are using sqlite db in your django
                        project as it needs some permission changes after
                        migration. (default: None)
  --reinit              Whether to force recreating/redoing everything
                        (default: False)

```


## License

MIT License

Copyright (c) 2016 Dionyz Lazar

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.