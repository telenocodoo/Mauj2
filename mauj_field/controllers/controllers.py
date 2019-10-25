# -*- coding: utf-8 -*-
from odoo import http

# class MaujField(http.Controller):
#     @http.route('/mauj_field/mauj_field/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mauj_field/mauj_field/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mauj_field.listing', {
#             'root': '/mauj_field/mauj_field',
#             'objects': http.request.env['mauj_field.mauj_field'].search([]),
#         })

#     @http.route('/mauj_field/mauj_field/objects/<model("mauj_field.mauj_field"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mauj_field.object', {
#             'object': obj
#         })