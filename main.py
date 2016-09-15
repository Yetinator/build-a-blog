#!/usr/bin/env python

#build a blog
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
                                        autoescape = True)
                                        
def getPosts(limit,offset):
    submits = db.GqlQuery("SELECT * FROM Submit "
                            "ORDER BY created DESC "
                            "LIMIT {0} OFFSET {1} ".format(limit, offset))
    return submits 

def getTotalPages():
    totalPages = db.GqlQuery("SELECT * FROM Submit").count()    
    if totalPages % 5 == 0:
        totalPages = totalPages/5
    else:
        totalPages = totalPages/5 + 1  
    return totalPages       
                                        
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw)) 
        
    def renderMain(self, title='', body='', error='', idL=''):
        submits = getPosts(5,0)
        self.render("index.html", title=title, body=body, error=error,submits=submits)
        
   
class Submit(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
        
class MainHandler(Handler):
    #this has been watered down to just a list of posts
        
    def get(self):
        self.redirect("/blog")
        
        #self.renderMain()
        
    
        
class BlogHandler(Handler):
    #displays 5 most recent posts
    #page perameter changes which posts
    #filter query by results
    def get(self):
        #the first number is the number to display, the second is the starting point
        page = self.request.get("page")
        #TODO in base.html set up page hyperlink that connects to a specific page sequence below.
        if page == '':
            page = 1
            entryStart = 0
        else:
            entryStart = (int(page)-1) * 5 #TODO minus one or not to minus one? 
        nextPage = int(page) + 1
        """if page != '':
            entryStart = (int(page) + 1) * 5 - 1
            nextPage = int(page) + 1
        else:
            entryStart = 0
            nextPage = 1
        """
        #TODO count entries and divide
        
       
        submits = getPosts(5,entryStart)
        self.render("index.html", submits=submits, page=page, totalPages=getTotalPages())
        
        
        
class NewPostHandler(Handler):
    #You are able to submit a new post at this route/view 
    #after which it displays on the main blog page (after a refresh)
    def get(self):
        self.render("newpost.html")
        
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
            self.render("newpost.html", error=error, title=title, body=body)
        
class ViewPostHandler(Handler):
    #This views a singe post without a lot of other stuff
    #This is the permalink
    
    def get(self, id):
        #TODO create post only output (what does this note mean?)
        #id comes from path get_by_id is a function of Submit...
        idLocal = int(id)
        this = Submit.get_by_id(idLocal)
        
        self.render("item.html", body = this.body, title = this.title, time = this.created)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogHandler),
    webapp2.Route("/blog/<id:\d+>", ViewPostHandler),
    ('/newpost', NewPostHandler)
], debug=True)
