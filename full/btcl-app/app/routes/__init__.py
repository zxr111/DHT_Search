from .search import APP
from .linuxos import linuxos
from .custom_tempfilter import init_ctfilter

# ...
def init_app(app):
    #注册
    app.register_blueprint(APP)
    #linux
    app.register_blueprint(linuxos)
    #初始化自定义过滤器
    init_ctfilter(app)