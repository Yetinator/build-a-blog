#!/usr/bin/env python

#build a blog
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                        autoescape = True)
                                        
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw)) 
        
    def renderMain(self, title='', body='', error='', idL=''):
        
        submits = db.GqlQuery("SELECT * FROM Submit "
                                "ORDER BY created DESC "
                                "LIMIT 5")                        
        self.render("index.html", title=title, body=body, error=error,submits=submits)
        
class Submit(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
        
class MainHandler(Handler):
    
        
    def get(self):
        self.renderMain()
        
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")
        
        if title and body:
            b = Submit(title = title, body = body)
            b.put()
            
            idL = b.key().id()
            self.redirect("/blog/{}".format(idL))
        else:
            error = "This is an error message for your convienence."
            self.renderMain(title, body, error)
        
class BlogHandler(Handler):
    #displays 5 most recent posts
    #filter query by results
    #TODO
    def get(self):
    
        self.write('you are here')
        #TODO
        
class NewPostHandler(Handler):
    #You are able to submit a new post at this route/view 
    #after which it displays on the main blog page (after a refresh)
    def get(self):
        self.write("I don't know where you're at")
        #TODO
        
class ViewPostHandler(Handler):
    def get(self, id):
        #TODO create post only output
        idLocal = int(id)
        this = Submit.get_by_id(idLocal)
        
        self.render("item.html", body = this.body, title = this.title, time = this.created)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogHandler),
    webapp2.Route("/blog/<id:\d+>", ViewPostHandler),
    ('/newpost', NewPostHandler)
], debug=True)
