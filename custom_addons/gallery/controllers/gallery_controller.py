from odoo import http
from odoo.http import request

class GalleryController(http.Controller):
    @http.route('/gallery', auth='public', website=True)
    def gallery_page(self, **kw):
        # Fetch images from the 'gallery.image' model
        images = request.env['gallery.image'].sudo().search([])  # Adjust domain as needed
        return request.render('gallery.gallery_page', {
            'images': images,
        })

    @http.route(['/gallery/image/<int:image_id>'], type='http', auth="public", website=True)
    def gallery_detail(self, image_id, **kwargs):
        image = request.env['gallery.image'].sudo().browse(image_id)
        if not image.exists():
            return request.not_found()

        return request.render('gallery.gallery_detail_template', {
            'image': image,
        })
