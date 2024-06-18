from odoo import fields, models, api
import logging
from markupsafe import Markup
import re

from lxml import etree
_logger = logging.getLogger(__name__)


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    contract_format_id = fields.Many2one('reclutamiento__kuale.contract_format', string='Tipo de Formato')
    contract_current = fields.Html(string='Contrato Actual')

    # body_html = fields.Html(related="contract_format_id.body")
    # body = fields.Html(string='Cuerpo del Formato', compute='_compute_body')

    @api.depends('contract_format_id')
    def _render_dynamic_body(self):
        for record in self:
            if record.contract_format_id:
                template = record.contract_format_id.body or ''
                _logger.info('Rendered Body template: %s', template)

                context = {'object': record}

                # Buscar todas las etiquetas t-out y reemplazar con los valores correspondientes
                def replace_match(match):
                    expr = match.group(1).strip()
                    # Evaluar la expresión en el contexto del objeto
                    try:
                        value = eval(expr, context)
                    except Exception as e:
                        value = str(e)
                    return str(value)

                body_rendered = re.sub(r'<t t-out="([^"]+)"></t>', replace_match, template)
                # record.body = Markup(body_rendered)
                record.contract_format_id.body = Markup(body_rendered)
            else:
                record.contract_format_id.body = ''

    def print_quotation(self):
        self.ensure_one()
        # Guarda el contenido del contrato generado por primera vez
        if self.contract_current:
            return self.env.ref('reclutamiento__kuale.report_contract_employee').report_action(self)
        else:
            self._render_dynamic_body()
            self.contract_current = self.contract_format_id.body
            _logger.info('Rendered Body_contarct: %s', self.contract_format_id.body)
            return self.env.ref('reclutamiento__kuale.report_contract_employee').report_action(self)


