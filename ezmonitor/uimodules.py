import tornado.web

class Header(tornado.web.UIModule):
    def css_files(self):
        return self.handler.static_url('css/header.css')
    
    def render(self, logged_in=False):
        return self.render_string(
            "module-header.html", 
            logged_in=logged_in
        )

class Footer(tornado.web.UIModule):
    def css_files(self):
        return self.handler.static_url('css/footer.css')
    
    def render(self):
        return self.render_string(
            "module-footer.html"
        )