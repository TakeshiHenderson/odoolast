from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class GalleryImage(models.Model):
    _name = 'gallery.image'
    _description = 'Gallery Image'



    name = fields.Char(string='Title', required=True)
    image = fields.Image(string='Image', required=True)
    description = fields.Text(string='Description')
    detail_url = fields.Char(string='Detail URL', compute='_compute_detail_url', store=True)

    def _compute_detail_url(self):
        for record in self:
            # Generate the detail URL dynamically
            record.detail_url = f'/gallery/detail/{record.id}' if record.id else ''
            _logger.info(f'Computed detail URL for {record.name}: {record.detail_url}')
