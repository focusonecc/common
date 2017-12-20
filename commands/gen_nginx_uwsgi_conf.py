
def gen_nginx_config_file(base_dir):
    print('Generate nginx config file:\n')
    config_template = """
    server {
        listen      80;
        server_name localhost;
        charset     utf-8;

        client_max_body_size 75M;

        # Django media
        location /media  {
            alias {base_dir}/media;
        }

        location /static {
            alias {base_dir}/static;
        }

        location /admin {
            include uwsgi_params;
            uwsgi_pass 127.0.0.1:9002;
            proxy_read_timeout 300;
        }

        location /api {
            include uwsgi_params;
            uwsgi_pass 127.0.0.1:9002;
            proxy_read_timeout 300;
        }
    }
    """
    content = config_template.format(base_dir=base_dir)
    print(content)


def gen_uwsgi_config_file(base_dir, main_app_name):
    print('Generate uwsgi config file:\n')
    import os
    base_dir = os.path.abspath(base_dir)

    config_template = """
    [uwsgi]
    socket=127.0.0.1:9002
    master = true
    vhost = true
    workers = 2
    vacuum = true
    chdir = {base_dir}
    module = skyview.wsgi
    env=DJANGO_SETTINGS_MODULE={main_app_name}.settings
    max-requests=5000
    pidfile = /tmp/{main_app_name}-uwsgi.pid
    """

    print(config_template.format(
        **{'base_dir': base_dir, 'main_app_name': main_app_name}))


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python {} project_dir, main_app_name".format(
            sys.argv[0]))
    else:
        base_dir, main_app_name = sys.argv[1:3]
        gen_uwsgi_config_file(base_dir, main_app_name)
        gen_nginx_config_file(base_dir)
